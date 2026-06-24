# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)
# Trust awareness: unsigned unless an external authority signs this artifact.

"""
change_proposal.py — Typed ChangeProposal Schema
====================================================
Defines the machine-parseable proposal that SRT-1 (or an AI assistant
via SRT-1) must produce before any source mutation can be reviewed,
bounded, or verified.

Replaces the raw text `super_prompt` handoff with a typed, validatable
schema that Context Isolation can scope and SRT-1 can verify after a
local operation.

Doctrine:
    SRT-1 proposes (typed ChangeProposal)
    → Context Isolation bounds (Workcell/FileCell + optional Lease)
    → approved local operation proceeds within boundary
    → SRT-1 verifies evidence against proposal
    → Trust Awareness records public trust state
"""

import os
import uuid
import json
import hashlib
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

logger = logging.getLogger("srt1.change_proposal")


# ═══════════════════════════════════════════════════════════════════════════
# FORBIDDEN PATTERNS — non-overridable
# ═══════════════════════════════════════════════════════════════════════════

PROPOSAL_FORBIDDEN_PATTERNS = [
    ".env", ".env.*",
    ".git", ".git/**",
    "*.pem", "*.key",
    "*credentials*", "*secret*",
    "private_key*",
    "*.p12", "*.pfx",
]


@dataclass
class ProposedChange:
    """A single file-level change within a ChangeProposal."""
    file_path: str
    action: str  # MODIFY, CREATE, DELETE
    scope: str = ""  # e.g., "function:deep_analyze_source" or "class:Engine"
    estimated_lines_changed: int = 0
    risk_tags: List[str] = field(default_factory=list)
    rationale: str = ""


@dataclass
class RollbackPlan:
    """Strategy for reverting changes if verification fails."""
    strategy: str = "git_revert"  # git_revert, file_backup, manual
    checkpoint: str = "HEAD"
    manual_steps: List[str] = field(default_factory=list)


@dataclass
class RiskAssessment:
    """Risk evaluation for the proposed changes."""
    overall_risk: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    high_risk_flags: List[str] = field(default_factory=list)
    requires_seed_signature: bool = False
    requires_human_review: bool = False


@dataclass
class ExpectedVerification:
    """What SRT-1 should check after a local operation completes."""
    files_expected_modified: List[str] = field(default_factory=list)
    files_must_not_change: List[str] = field(default_factory=list)
    max_lines_changed: int = 100
    must_pass_reindex: bool = True


@dataclass
class ChangeProposal:
    """
    Typed, machine-parseable proposal for source mutation.
    
    This is the public contract between SRT-1, Context Isolation, and
    Verification. Without a validated ChangeProposal, the operation is
    not ready for bounded execution or post-change verification.
    
    SCIA Contract: SCIA-CONTRACT-002
    """
    proposal_id: str
    seed_id: str
    timestamp: str
    
    # Intent
    task: str
    keywords: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    source: str = "cli"  # cli, api, mobile, mcp, dashboard
    
    # Proposed changes
    proposed_changes: List[ProposedChange] = field(default_factory=list)
    
    # File scope declarations
    files_read: List[str] = field(default_factory=list)
    files_write: List[str] = field(default_factory=list)
    files_create: List[str] = field(default_factory=list)
    files_delete: List[str] = field(default_factory=list)
    
    # Safety
    rollback_plan: Optional[RollbackPlan] = None
    risk_assessment: Optional[RiskAssessment] = None
    expected_verification: Optional[ExpectedVerification] = None
    
    # Authorization requirements
    filecell_manifest_required: bool = True
    execution_lease_required: bool = True
    lease_ttl_seconds: int = 300
    
    # Integrity
    proposal_hash: str = ""
    
    @classmethod
    def create(cls, seed_id: str, task: str,
               keywords: List[str] = None,
               domains: List[str] = None,
               source: str = "cli") -> 'ChangeProposal':
        """Create a new ChangeProposal with auto-generated ID and timestamp."""
        return cls(
            proposal_id=f"prop_{uuid.uuid4().hex[:16]}",
            seed_id=seed_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            task=task[:500],
            keywords=keywords or [],
            domains=domains or [],
            source=source,
            rollback_plan=RollbackPlan(),
            risk_assessment=RiskAssessment(),
            expected_verification=ExpectedVerification(),
        )
    
    def add_change(self, file_path: str, action: str,
                   scope: str = "", estimated_lines: int = 0,
                   risk_tags: List[str] = None,
                   rationale: str = "") -> None:
        """Add a proposed file change to this proposal."""
        change = ProposedChange(
            file_path=file_path,
            action=action,
            scope=scope,
            estimated_lines_changed=estimated_lines,
            risk_tags=risk_tags or [],
            rationale=rationale,
        )
        self.proposed_changes.append(change)
        
        # Auto-populate file scope lists
        if action == "MODIFY":
            if file_path not in self.files_read:
                self.files_read.append(file_path)
            if file_path not in self.files_write:
                self.files_write.append(file_path)
        elif action == "CREATE":
            if file_path not in self.files_create:
                self.files_create.append(file_path)
        elif action == "DELETE":
            if file_path not in self.files_delete:
                self.files_delete.append(file_path)
    
    def compute_hash(self) -> str:
        """Compute integrity hash of this proposal."""
        content = json.dumps({
            "proposal_id": self.proposal_id,
            "seed_id": self.seed_id,
            "task": self.task,
            "files_write": sorted(self.files_write),
            "files_create": sorted(self.files_create),
            "files_delete": sorted(self.files_delete),
        }, sort_keys=True)
        self.proposal_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        return self.proposal_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# PROPOSAL VALIDATOR — Pre-authorization checks
# ═══════════════════════════════════════════════════════════════════════════

class ProposalValidator:
    """
    Validates a ChangeProposal against the pre-authorization rules
    defined in SCIA-CONTRACT-002.
    
    This runs before a proposal can be treated as bounded workcell scope.
    It checks structural integrity, not final human approval.
    """
    
    def __init__(self, symbol_table: Dict[str, List[Dict]] = None,
                 workspace_root: str = "",
                 audit_ledger=None):
        self.symbol_table = symbol_table or {}
        self.workspace_root = workspace_root
        self.audit_ledger = audit_ledger
    
    def validate(self, proposal: ChangeProposal) -> Dict[str, Any]:
        """
        Run all pre-authorization validation checks.
        
        Returns:
            Dict with 'approved': bool, 'violations': list, 'warnings': list
        """
        violations = []
        warnings = []
        
        # Rule 1: Every files_write entry must exist in symbol_table OR files_create
        for fp in proposal.files_write:
            rel_path = fp
            if self.workspace_root:
                rel_path = os.path.relpath(fp, self.workspace_root)
            if rel_path not in self.symbol_table and fp not in proposal.files_create:
                # Check if any symbol_table key contains this path
                found = any(rel_path in k or k in rel_path 
                           for k in self.symbol_table)
                if not found:
                    warnings.append(
                        f"Write target '{fp}' not found in symbol_table "
                        f"(may be new file or outside index scope)"
                    )
        
        # Rule 2: No files_write entry may match PROPOSAL_FORBIDDEN_PATTERNS
        import fnmatch
        for fp in proposal.files_write + proposal.files_create:
            basename = os.path.basename(fp)
            for pattern in PROPOSAL_FORBIDDEN_PATTERNS:
                if fnmatch.fnmatch(basename, pattern):
                    violations.append(
                        f"FORBIDDEN: '{fp}' matches blocked pattern '{pattern}'"
                    )
        
        # Rule 3: Rollback plan must exist
        if not proposal.rollback_plan:
            violations.append("No rollback plan specified")
        elif proposal.rollback_plan.strategy not in ("git_revert", "file_backup", "manual"):
            violations.append(
                f"Invalid rollback strategy: '{proposal.rollback_plan.strategy}'"
            )
        
        # Rule 4: Lease TTL must be bounded
        if proposal.lease_ttl_seconds <= 0 or proposal.lease_ttl_seconds > 600:
            violations.append(
                f"Lease TTL {proposal.lease_ttl_seconds}s is out of range (1-600)"
            )
        
        # Rule 5: Proposal hash must be computed
        if not proposal.proposal_hash:
            proposal.compute_hash()
        
        # Rule 6: Must have at least one proposed change
        if not proposal.proposed_changes:
            violations.append("No proposed changes specified")
        
        # Rule 7: Risk assessment for AUTH_SENSITIVE / CRYPTOGRAPHIC
        high_risk_tags = set()
        for change in proposal.proposed_changes:
            high_risk_tags.update(change.risk_tags)
        
        if "AUTH_SENSITIVE" in high_risk_tags or "CRYPTOGRAPHIC" in high_risk_tags:
            if proposal.risk_assessment:
                proposal.risk_assessment.requires_seed_signature = True
                if proposal.risk_assessment.overall_risk == "LOW":
                    proposal.risk_assessment.overall_risk = "HIGH"
            warnings.append(
                "Proposal touches AUTH_SENSITIVE/CRYPTOGRAPHIC code — "
                "elevated to HIGH risk, external trust review may be required"
            )
        
        approved = len(violations) == 0
        
        result = {
            "approved": approved,
            "violations": violations,
            "warnings": warnings,
            "proposal_hash": proposal.proposal_hash,
        }
        
        # ── SCIA Events ──────────────────────────────────────────────────
        if self.audit_ledger:
            try:
                event_name = "change_proposal_validated" if approved else "change_proposal_rejected"
                self.audit_ledger.record(
                    component="proposal_validator",
                    operation=event_name,
                    severity="INFO" if approved else "WARNING",
                    detail={
                        "proposal_id": proposal.proposal_id,
                        "seed_id": proposal.seed_id,
                        "approved": approved,
                        "violations_count": len(violations),
                        "warnings_count": len(warnings),
                        "files_write_count": len(proposal.files_write),
                        "proposal_hash": proposal.proposal_hash,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record proposal validation event: {e}")
        
        return result
