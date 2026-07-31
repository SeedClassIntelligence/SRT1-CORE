"""
SRT-1 Authority Client — External Signing Integration Point

This module provides the integration layer between SRT-1 Core and the
private signing authority service. SRT-1 does NOT perform signing locally.
It calls out to the authority service, which lives in its own private
repository and runs as a separate process.

The authority service handles:
    - Cryptographic provenance signing (SHA-256 chained signatures)
    - Signature injection into payloads
    - Signature validation (tamper detection)
    - Chain integrity verification (immutable audit trail)
    - Creator identity + timestamp binding (WHO + WHEN)

SRT-1 produces the content. The authority service signs it.
Without the authority service, SRT-1 cannot prove provenance —
only detect local tampering via plain hashes.

Configuration:
    SRT1_AUTHORITY_ENDPOINT  — Base URL of the authority service API
    SRT1_AUTHORITY_API_KEY   — API key for authentication

Usage:
    client = AuthorityClient()

    # Sign an artifact
    sig = client.sign(
        content={"repo": "my-project", "manifest_hash": "a1b2c3..."},
        operation_type="manifest_sign",
        metadata={"version": "1.0.0"},
    )

    # Inject signature into a payload
    signed_payload = client.inject(payload, sig)

    # Validate a signed payload (verify it hasn't been tampered with)
    is_valid = client.validate(signed_payload)

    # Verify the full signature chain
    chain_ok = client.verify_chain()
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

logger = logging.getLogger("srt1.authority")


# ─────────────────────────────────────────────────────────────────────────────
# Data Model — mirrors the authority service's signature dataclass
# ─────────────────────────────────────────────────────────────────────────────

class ProvenanceRecord:
    """
    A signed provenance record returned by the authority service.

    Each record contains:
        signature_id:       Unique ID for this signature
        operation_type:     What kind of operation was signed
        timestamp:          When the signature was issued
        content_hash:       SHA-256 of the content that was signed
        previous_signature: ID of the previous signature in the chain
        metadata:           Additional context (repo, version, creator, etc.)
        chain_position:     Position in the immutable signature chain
    """

    def __init__(
        self,
        signature_id: str,
        operation_type: str,
        timestamp: float,
        content_hash: str,
        previous_signature: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chain_position: int = 0,
        authority_issued: bool = True,
        status: Optional[str] = None,
        authority_id: Optional[str] = None,
        degradation_reason: Optional[str] = None,
    ):
        self.signature_id = signature_id
        self.operation_type = operation_type
        self.timestamp = timestamp
        self.content_hash = content_hash
        self.previous_signature = previous_signature
        self.metadata = metadata or {}
        self.chain_position = chain_position
        self.authority_issued = authority_issued
        self.status = status or ("signed" if authority_issued else "unsigned")
        self.authority_id = authority_id
        self.degradation_reason = degradation_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signature_id": self.signature_id,
            "operation_type": self.operation_type,
            "timestamp": self.timestamp,
            "content_hash": self.content_hash,
            "previous_signature": self.previous_signature,
            "metadata": self.metadata,
            "chain_position": self.chain_position,
            "authority_issued": self.authority_issued,
            "status": self.status,
            "authority_id": self.authority_id,
            "degradation_reason": self.degradation_reason,
            "lineage": "present" if self.previous_signature or self.chain_position == 0 else "missing",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceRecord":
        return cls(
            signature_id=data["signature_id"],
            operation_type=data["operation_type"],
            timestamp=data["timestamp"],
            content_hash=data["content_hash"],
            previous_signature=data.get("previous_signature"),
            metadata=data.get("metadata", {}),
            chain_position=data.get("chain_position", 0),
            authority_issued=data.get("authority_issued", True),
            status=data.get("status"),
            authority_id=data.get("authority_id"),
            degradation_reason=data.get("degradation_reason"),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Authority Client — calls out to an external authority service
# ─────────────────────────────────────────────────────────────────────────────

class AuthorityClient:
    """
    Integration client for an external signing authority service.

    SRT-1 uses this to:
        1. sign()      — Request a provenance signature for content
        2. inject()    — Embed a signature into a payload
        3. validate()  — Verify a signed payload hasn't been tampered with
        4. verify_chain() — Confirm the full signature chain is intact

    When the authority service is connected:
        → Signatures are authority-issued, verified, and registered
        → Payloads carry proof of WHO, WHEN, and WHAT

    When the authority service is NOT connected:
        → Falls back to local SHA-256 hashing
        → Payloads are tamper-detectable but NOT authority-signed
        → No proof of WHO or WHEN — only WHAT
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.endpoint = endpoint or os.environ.get("SRT1_AUTHORITY_ENDPOINT", "")
        self.api_key = api_key or os.environ.get("SRT1_AUTHORITY_API_KEY", "")
        self._available = bool(self.endpoint and self.api_key)

        # Local signature chain (used when authority is unavailable)
        self._local_chain: List[ProvenanceRecord] = []

        if self._available:
            logger.info("Authority service connected — signatures will be authority-issued.")
        else:
            logger.debug(
                "Authority service not configured. "
                "Set SRT1_AUTHORITY_ENDPOINT and SRT1_AUTHORITY_API_KEY "
                "for full provenance signing."
            )

    @property
    def is_available(self) -> bool:
        """True if the authority service is configured and reachable."""
        return self._available

    # ── SIGN ─────────────────────────────────────────────────────────────────

    def sign(
        self,
        content: Any,
        operation_type: str = "artifact",
        metadata: Optional[Dict[str, Any]] = None,
        phase: Optional[str] = None,
        require_authority: bool = False,
    ) -> ProvenanceRecord:
        """
        Sign content through the authority service.

        This is the core operation. It takes any JSON-serializable content,
        sends it to the authority service, and gets back a signed provenance
        record with a unique signature_id, verified timestamp, and chain link.

        Args:
            content: Any JSON-serializable data to be signed.
            operation_type: Category of the operation being signed
                           (e.g., "manifest_sign", "checkpoint", "report").
            metadata: Additional context to embed in the signature record.

        Returns:
            ProvenanceRecord with authority-issued signature, or a local
            fallback record if the authority service is unavailable.
        """
        operation_type = str(phase or operation_type or "artifact")
        if self._available:
            try:
                return self._remote_sign(content, operation_type, metadata)
            except Exception as e:
                logger.warning("Authority service could not issue a signature: %s", type(e).__name__)
                if require_authority:
                    return self._failed_record(content, operation_type, metadata, str(e))

        if require_authority:
            return self._failed_record(
                content,
                operation_type,
                metadata,
                "External Seed Signature authority is unavailable",
            )
        return self._local_sign(content, operation_type, metadata)

    # ── INJECT ───────────────────────────────────────────────────────────────

    def inject(
        self,
        payload: Dict[str, Any],
        record: ProvenanceRecord,
    ) -> Dict[str, Any]:
        """
        Inject a provenance record into a payload.

        The signed payload can later be validated with validate().

        Args:
            payload: The original payload dict.
            record: The ProvenanceRecord to embed.

        Returns:
            A new dict with the payload + embedded provenance record.
        """
        enhanced = payload.copy()
        enhanced["_provenance"] = record.to_dict()
        enhanced["_provenance_timestamp"] = datetime.fromtimestamp(
            record.timestamp
        ).isoformat()
        return enhanced

    # ── VALIDATE ─────────────────────────────────────────────────────────────

    def validate(self, signed_payload: Dict[str, Any]) -> bool:
        """
        Validate that a signed payload hasn't been tampered with.

        Recalculates the content hash from the payload (excluding the
        provenance fields) and compares it to the hash in the embedded
        provenance record. If they don't match, the content was modified
        after signing.

        Args:
            signed_payload: A payload that was previously signed with inject().

        Returns:
            True if the content matches the signature. False if tampered.
        """
        if "_provenance" not in signed_payload:
            return False

        record_data = signed_payload["_provenance"]

        # Rebuild the original content (exclude provenance fields)
        content = {
            k: v for k, v in signed_payload.items()
            if not k.startswith("_provenance")
        }

        # Recompute the hash
        content_str = json.dumps(content, sort_keys=True, default=str)
        expected_hash = hashlib.sha256(content_str.encode()).hexdigest()

        return record_data.get("content_hash") == expected_hash

    # ── VERIFY CHAIN ─────────────────────────────────────────────────────────

    def verify_chain(self) -> bool:
        """
        Verify the integrity of the local signature chain.

        Checks that:
            - The first signature has no previous_signature
            - Each subsequent signature links to the previous one
            - Chain positions are sequential

        Returns:
            True if the chain is intact and unbroken.
        """
        for i, record in enumerate(self._local_chain):
            if i == 0:
                if record.previous_signature is not None:
                    return False
            else:
                if record.previous_signature != self._local_chain[i - 1].signature_id:
                    return False
            if record.chain_position != i:
                return False
        return True

    # ── EXTRACT ──────────────────────────────────────────────────────────────

    def extract(self, signed_payload: Dict[str, Any]) -> Optional[ProvenanceRecord]:
        """Extract the provenance record from a signed payload."""
        if "_provenance" not in signed_payload:
            return None
        return ProvenanceRecord.from_dict(signed_payload["_provenance"])

    # ── CHAIN ACCESS ─────────────────────────────────────────────────────────

    def get_chain(self) -> List[Dict[str, Any]]:
        """Get the full signature chain as a list of dicts."""
        return [r.to_dict() for r in self._local_chain]

    # ── PRIVATE: REMOTE SIGNING ──────────────────────────────────────────────

    def _remote_sign(
        self,
        content: Any,
        operation_type: str,
        metadata: Optional[Dict[str, Any]],
    ) -> ProvenanceRecord:
        """Call the private authority service to sign content."""
        import urllib.request
        import urllib.error
        import time

        # Hash the content locally first
        content_str = json.dumps(content, sort_keys=True, default=str)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()

        # Previous signature in chain
        previous_sig = (
            self._local_chain[-1].signature_id if self._local_chain else None
        )

        payload = {
            "content_hash": content_hash,
            "operation_type": operation_type,
            "metadata": metadata or {},
            "previous_signature": previous_sig,
            "chain_position": len(self._local_chain),
            "requested_at": datetime.now(tz=timezone.utc).isoformat(),
        }

        url = self.endpoint.rstrip("/") + "/sign"
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "SRT1-Core/2.1",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Authority returned HTTP {e.code}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot reach authority: {e.reason}")

        record = ProvenanceRecord(
            signature_id=str(result.get("signature_id") or ""),
            operation_type=operation_type,
            timestamp=result.get("timestamp", time.time()),
            content_hash=content_hash,
            previous_signature=previous_sig,
            metadata=metadata or {},
            chain_position=len(self._local_chain),
            authority_issued=True,
            status="signed",
            authority_id=result.get("authority_id") or result.get("issuer"),
        )

        if not record.signature_id:
            raise RuntimeError("Authority response did not include a signature_id")

        self._local_chain.append(record)
        logger.info(f"Authority-signed: {record.signature_id} [{operation_type}]")
        return record

    # ── PRIVATE: LOCAL FALLBACK ──────────────────────────────────────────────

    def _local_sign(
        self,
        content: Any,
        operation_type: str,
        metadata: Optional[Dict[str, Any]],
    ) -> ProvenanceRecord:
        """
        Generate a local integrity record when the authority is unavailable.

        This produces a valid chain entry with a content hash, but it is
        NOT authority-signed. It can detect tampering but cannot prove:
            - WHO created the content
            - WHEN it was created (only local clock, unverified)
            - That the content is TRUSTED by an authority

        The record is marked authority_issued=False so consumers know
        the difference.
        """
        import time

        content_str = json.dumps(content, sort_keys=True, default=str)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()

        previous_sig = (
            self._local_chain[-1].signature_id if self._local_chain else None
        )

        timestamp = time.time()
        sig_data = f"{operation_type}_{timestamp}_{content_hash}_{previous_sig}"
        signature_id = "LOCAL-" + hashlib.sha256(sig_data.encode()).hexdigest()[:12].upper()

        record = ProvenanceRecord(
            signature_id=signature_id,
            operation_type=operation_type,
            timestamp=timestamp,
            content_hash=content_hash,
            previous_signature=previous_sig,
            metadata=metadata or {},
            chain_position=len(self._local_chain),
            authority_issued=False,
            status="unsigned",
            degradation_reason="External Seed Signature authority was not used",
        )

        self._local_chain.append(record)
        logger.debug(f"Local-only (unsigned): {record.signature_id} [{operation_type}]")
        return record

    def _failed_record(
        self,
        content: Any,
        operation_type: str,
        metadata: Optional[Dict[str, Any]],
        reason: str,
    ) -> ProvenanceRecord:
        """Return explicit failed trust metadata without creating a fake signature."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
        return ProvenanceRecord(
            signature_id="",
            operation_type=operation_type,
            timestamp=datetime.now(tz=timezone.utc).timestamp(),
            content_hash=content_hash,
            previous_signature=self._local_chain[-1].signature_id if self._local_chain else None,
            metadata=metadata or {},
            chain_position=len(self._local_chain),
            authority_issued=False,
            status="failed",
            degradation_reason=str(reason or "Authority signature failed"),
        )
