"""
SRT-1 Recall Packet contract.

Public Core owns the packet vocabulary and identity alignment. Private memory
systems may supply packet content, but they are optional and must fail closed.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
from typing import Any, Dict, Optional


def _default_trust_state() -> Dict[str, str]:
    return {
        "signature": "unsigned",
        "verification": "unverified",
        "lineage": "missing",
    }


def _packet_id(queue_seed_id: str, source_type: str, source_id: str, content: str) -> str:
    material = f"{queue_seed_id}:{source_type}:{source_id}:{content}".encode("utf-8")
    return f"recall_{sha256(material).hexdigest()[:16]}"


@dataclass
class RecallPacket:
    packet_id: str
    queue_seed_id: str
    srt_anchor_id: Optional[str]
    source_type: str
    source_id: str
    content: str
    relevance_score: float = 0.0
    freshness_state: str = "unknown"
    trust_state: Dict[str, str] = field(default_factory=_default_trust_state)
    manifest_hash: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    ttl: Optional[int] = 3
    degradation_reason: Optional[str] = None

    @classmethod
    def create(
        cls,
        queue_seed_id: str,
        content: str,
        source_type: str,
        source_id: str,
        srt_anchor_id: Optional[str] = None,
        relevance_score: float = 0.0,
        freshness_state: str = "unknown",
        trust_state: Optional[Dict[str, str]] = None,
        manifest_hash: Optional[str] = None,
        expires_at: Optional[str] = None,
        ttl: Optional[int] = 3,
        degradation_reason: Optional[str] = None,
    ) -> "RecallPacket":
        return cls(
            packet_id=_packet_id(queue_seed_id, source_type, source_id, content),
            queue_seed_id=queue_seed_id,
            srt_anchor_id=srt_anchor_id,
            source_type=source_type,
            source_id=source_id,
            content=content,
            relevance_score=relevance_score,
            freshness_state=freshness_state,
            trust_state=trust_state or _default_trust_state(),
            manifest_hash=manifest_hash,
            expires_at=expires_at,
            ttl=ttl,
            degradation_reason=degradation_reason,
        )

    @classmethod
    def from_external_reflection(
        cls,
        reflection: Dict[str, Any],
        queue_seed_id: str,
        srt_anchor_id: Optional[str] = None,
        manifest_hash: Optional[str] = None,
    ) -> "RecallPacket":
        content = str(reflection.get("content") or reflection.get("text") or "")
        source_id = str(reflection.get("id") or reflection.get("source_id") or "external_memory")
        return cls.create(
            queue_seed_id=queue_seed_id,
            srt_anchor_id=srt_anchor_id,
            source_type="external_private",
            source_id=source_id,
            content=content,
            relevance_score=float(reflection.get("relevance_score", reflection.get("score", 0.0)) or 0.0),
            freshness_state=reflection.get("freshness_state", "unknown"),
            trust_state=reflection.get("trust_state") or _default_trust_state(),
            manifest_hash=manifest_hash,
            ttl=reflection.get("ttl", 3),
            degradation_reason=reflection.get("degradation_reason"),
        )

    @classmethod
    def from_manifest_candidate(
        cls,
        candidate: Dict[str, Any],
        queue_seed_id: str,
        srt_anchor_id: Optional[str] = None,
        manifest_hash: Optional[str] = None,
    ) -> "RecallPacket":
        name = candidate.get("name") or candidate.get("qualified_name") or "manifest_candidate"
        content = candidate.get("content") or candidate.get("purpose") or str(candidate)
        return cls.create(
            queue_seed_id=queue_seed_id,
            srt_anchor_id=srt_anchor_id,
            source_type="manifest",
            source_id=str(name),
            content=str(content),
            relevance_score=float(candidate.get("relevance_score", 0.0) or 0.0),
            freshness_state="fresh" if manifest_hash else "unknown",
            manifest_hash=manifest_hash,
        )

    @classmethod
    def from_thread_recovery_candidate(
        cls,
        candidate: Dict[str, Any],
        queue_seed_id: str,
        srt_anchor_id: Optional[str] = None,
    ) -> "RecallPacket":
        content = candidate.get("text") or candidate.get("content") or str(candidate)
        source_id = candidate.get("id") or candidate.get("message_index") or "thread_recovery"
        return cls.create(
            queue_seed_id=queue_seed_id,
            srt_anchor_id=srt_anchor_id,
            source_type="thread_recovery",
            source_id=str(source_id),
            content=str(content),
            relevance_score=float(candidate.get("relevance_score", 0.0) or 0.0),
            freshness_state="unknown",
        )

    @classmethod
    def degraded(
        cls,
        queue_seed_id: str,
        reason: str,
        srt_anchor_id: Optional[str] = None,
    ) -> "RecallPacket":
        return cls.create(
            queue_seed_id=queue_seed_id,
            srt_anchor_id=srt_anchor_id,
            source_type="recall_unavailable",
            source_id="private_memory_unavailable",
            content="Recall source unavailable.",
            freshness_state="degraded",
            degradation_reason=reason,
            ttl=1,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_reinjection_dict(self) -> Dict[str, Any]:
        data = self.to_dict()
        data.update({
            "mode": "recall",
            "priority": max(1, min(49, int(self.relevance_score * 49) or 25)),
            "source": self.source_type,
        })
        return data
