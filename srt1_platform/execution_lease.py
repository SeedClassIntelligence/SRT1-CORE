# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)
# Trust awareness: unsigned unless an external authority signs this artifact.

"""
execution_lease.py — Time-Bounded Execution Authority
=======================================================
Defines a temporary, revocable local permission record for an approved
operation inside a FileCell/Workcell. Without a lease, no bounded local
operation has lease-backed mutation authority. A lease expires; an
expired lease means the operation must stop.

Doctrine:
    - No lease = no mutation authority
    - Lease TTL is bounded (30s - 600s)
    - Lease can be revoked by GovernanceMonitor, human, or FileCell violation
    - One active lease per seed_id at a time
    - Renewal requires re-validation of ChangeProposal

SCIA Contract: SCIA-CONTRACT-004
"""

import uuid
import hashlib
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

logger = logging.getLogger("srt1.execution_lease")


class LeaseExpiredViolation(Exception):
    """Raised when an operation is attempted after lease expiry."""
    pass


class LeaseScopeViolation(Exception):
    """Raised when an operation exceeds scope limits."""
    pass


class LeaseRevokedViolation(Exception):
    """Raised when an operation is attempted on a revoked lease."""
    pass


@dataclass
class ExecutionLease:
    """
    Time-bounded, revocable permission record for bounded local work.
    
    Grants temporary permission to mutate files within the
    scope defined by a ChangeProposal and FileCellManifest.
    """
    lease_id: str
    cell_id: str
    proposal_id: str
    seed_id: str
    
    # Timing
    granted_at: str = ""
    expires_at: str = ""
    ttl_seconds: int = 300
    
    # Authority (subset of FileCellManifest)
    allowed_writes: List[str] = field(default_factory=list)
    allowed_reads: List[str] = field(default_factory=list)
    max_files_created: int = 5
    max_files_modified: int = 10
    max_lines_changed: int = 500
    
    # Status tracking
    status: str = "ACTIVE"  # ACTIVE, EXPIRED, REVOKED, COMPLETED
    
    # Revocation
    revoked: bool = False
    revoked_at: Optional[str] = None
    revoked_by: Optional[str] = None
    revocation_reason: Optional[str] = None
    
    # Mutation tracking (updated during execution)
    files_modified_count: int = 0
    files_created_count: int = 0
    lines_changed_count: int = 0
    
    # Integrity
    lease_hash: str = ""
    
    @classmethod
    def grant(cls, cell_id: str, proposal_id: str, seed_id: str,
              allowed_reads: List[str] = None,
              allowed_writes: List[str] = None,
              ttl_seconds: int = 300,
              max_files_modified: int = 10,
              max_files_created: int = 5,
              max_lines_changed: int = 500) -> 'ExecutionLease':
        """
        Grant a new execution lease.
        
        Args:
            cell_id: The FileCell this lease operates within
            proposal_id: The ChangeProposal authorizing this lease
            seed_id: The seed this lease serves
            ttl_seconds: Time-to-live (30-600 seconds)
        """
        # Enforce TTL bounds
        ttl_seconds = max(30, min(600, ttl_seconds))
        
        now = datetime.utcnow()
        expires = now + timedelta(seconds=ttl_seconds)
        
        lease = cls(
            lease_id=f"lease_{uuid.uuid4().hex[:16]}",
            cell_id=cell_id,
            proposal_id=proposal_id,
            seed_id=seed_id,
            granted_at=now.isoformat() + "Z",
            expires_at=expires.isoformat() + "Z",
            ttl_seconds=ttl_seconds,
            allowed_reads=allowed_reads or [],
            allowed_writes=allowed_writes or [],
            max_files_modified=max_files_modified,
            max_files_created=max_files_created,
            max_lines_changed=max_lines_changed,
        )
        lease._compute_hash()
        return lease
    
    def _compute_hash(self) -> str:
        """Compute integrity hash of this lease."""
        content = json.dumps({
            "lease_id": self.lease_id,
            "cell_id": self.cell_id,
            "proposal_id": self.proposal_id,
            "seed_id": self.seed_id,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
        }, sort_keys=True)
        self.lease_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        return self.lease_hash
    
    def is_active(self) -> bool:
        """Check if this lease is currently active (not expired, not revoked)."""
        if self.status != "ACTIVE":
            return False
        if self.revoked:
            return False
        
        # Check TTL
        try:
            expires = datetime.fromisoformat(self.expires_at.rstrip("Z"))
            if datetime.utcnow() > expires:
                self.status = "EXPIRED"
                return False
        except (ValueError, AttributeError):
            return False
        
        return True
    
    def check_write_authority(self) -> bool:
        """
        Check that this lease still permits a write operation.
        Raises appropriate violation if not.
        """
        if self.revoked:
            raise LeaseRevokedViolation(
                f"Lease {self.lease_id} was revoked at {self.revoked_at} "
                f"by {self.revoked_by}: {self.revocation_reason}"
            )
        
        if not self.is_active():
            raise LeaseExpiredViolation(
                f"Lease {self.lease_id} expired at {self.expires_at}"
            )
        
        if self.files_modified_count >= self.max_files_modified:
            raise LeaseScopeViolation(
                f"Lease {self.lease_id} exceeded max_files_modified "
                f"({self.files_modified_count}/{self.max_files_modified})"
            )
        
        if self.lines_changed_count >= self.max_lines_changed:
            raise LeaseScopeViolation(
                f"Lease {self.lease_id} exceeded max_lines_changed "
                f"({self.lines_changed_count}/{self.max_lines_changed})"
            )
        
        return True
    
    def record_modification(self, lines_changed: int = 0) -> None:
        """Record that a file was modified under this lease."""
        self.files_modified_count += 1
        self.lines_changed_count += lines_changed
    
    def record_creation(self) -> None:
        """Record that a file was created under this lease."""
        self.files_created_count += 1
        if self.files_created_count > self.max_files_created:
            raise LeaseScopeViolation(
                f"Lease {self.lease_id} exceeded max_files_created "
                f"({self.files_created_count}/{self.max_files_created})"
            )
    
    def revoke(self, revoked_by: str, reason: str) -> None:
        """Revoke this lease immediately."""
        self.revoked = True
        self.revoked_at = datetime.utcnow().isoformat() + "Z"
        self.revoked_by = revoked_by
        self.revocation_reason = reason
        self.status = "REVOKED"
    
    def complete(self) -> None:
        """Mark this lease as completed (seed finished within lease period)."""
        if self.is_active():
            self.status = "COMPLETED"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════
# LEASE MANAGER — Coordinates active leases
# ═══════════════════════════════════════════════════════════════════════════

class LeaseManager:
    """
    Manages the lifecycle of execution leases.
    Ensures one active lease per seed_id and handles
    granting, checking, revoking, and completing leases.
    """
    
    def __init__(self, audit_ledger=None):
        self.audit_ledger = audit_ledger
        self._active_leases: Dict[str, ExecutionLease] = {}
    
    def grant_lease(self, cell_id: str, proposal_id: str, seed_id: str,
                    allowed_reads: List[str] = None,
                    allowed_writes: List[str] = None,
                    ttl_seconds: int = 300,
                    **kwargs) -> ExecutionLease:
        """
        Grant a new execution lease for a seed.
        
        Raises if a lease already exists for this seed_id.
        """
        # One active lease per seed_id
        if seed_id in self._active_leases:
            existing = self._active_leases[seed_id]
            if existing.is_active():
                raise ValueError(
                    f"Active lease {existing.lease_id} already exists for seed {seed_id}"
                )
            # Expired/completed/revoked — clean up
            del self._active_leases[seed_id]
        
        lease = ExecutionLease.grant(
            cell_id=cell_id,
            proposal_id=proposal_id,
            seed_id=seed_id,
            allowed_reads=allowed_reads,
            allowed_writes=allowed_writes,
            ttl_seconds=ttl_seconds,
            **kwargs,
        )
        
        self._active_leases[seed_id] = lease
        
        # ── SCIA Event: execution_lease_granted ───────────────────────
        if self.audit_ledger:
            try:
                self.audit_ledger.record(
                    component="lease_manager",
                    operation="execution_lease_granted",
                    severity="CRITICAL",
                    detail={
                        "lease_id": lease.lease_id,
                        "cell_id": cell_id,
                        "proposal_id": proposal_id,
                        "seed_id": seed_id,
                        "ttl_seconds": lease.ttl_seconds,
                        "expires_at": lease.expires_at,
                        "max_files_modified": lease.max_files_modified,
                        "max_lines_changed": lease.max_lines_changed,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record execution_lease_granted: {e}")
        
        return lease
    
    def get_lease(self, seed_id: str) -> Optional[ExecutionLease]:
        """Get the active lease for a seed, or None."""
        lease = self._active_leases.get(seed_id)
        if lease and not lease.is_active():
            # Auto-emit expiry event
            if lease.status == "EXPIRED" and self.audit_ledger:
                try:
                    self.audit_ledger.record(
                        component="lease_manager",
                        operation="execution_lease_expired",
                        severity="WARNING",
                        detail={
                            "lease_id": lease.lease_id,
                            "seed_id": seed_id,
                            "expired_at": lease.expires_at,
                        },
                    )
                except Exception:
                    pass
            return None
        return lease
    
    def revoke_lease(self, seed_id: str, revoked_by: str, reason: str) -> bool:
        """Revoke the active lease for a seed."""
        lease = self._active_leases.get(seed_id)
        if not lease:
            return False
        
        lease.revoke(revoked_by=revoked_by, reason=reason)
        
        # ── SCIA Event: execution_lease_revoked ───────────────────────
        if self.audit_ledger:
            try:
                self.audit_ledger.record(
                    component="lease_manager",
                    operation="execution_lease_revoked",
                    severity="CRITICAL",
                    detail={
                        "lease_id": lease.lease_id,
                        "seed_id": seed_id,
                        "revoked_by": revoked_by,
                        "reason": reason,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record execution_lease_revoked: {e}")
        
        return True
    
    def complete_lease(self, seed_id: str) -> bool:
        """Mark a lease as completed."""
        lease = self._active_leases.get(seed_id)
        if not lease:
            return False
        
        lease.complete()
        
        # ── SCIA Event: execution_lease_completed ─────────────────────
        if self.audit_ledger:
            try:
                self.audit_ledger.record(
                    component="lease_manager",
                    operation="execution_lease_completed",
                    severity="INFO",
                    detail={
                        "lease_id": lease.lease_id,
                        "seed_id": seed_id,
                        "files_modified": lease.files_modified_count,
                        "files_created": lease.files_created_count,
                        "lines_changed": lease.lines_changed_count,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record execution_lease_completed: {e}")
        
        return True
