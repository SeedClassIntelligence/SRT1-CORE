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
import tempfile
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

logger = logging.getLogger("srt1.change_proposal")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
            timestamp=_utc_now(),
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

class ChangeProposalStore:
    """Persist provider/developer ChangeProposal records without applying source changes."""

    def __init__(self, repo_path: str, proposals_dir: Optional[str] = None):
        self.repo_path = os.path.realpath(repo_path)
        self.proposals_dir = proposals_dir or os.path.join(self.repo_path, ".srt1", "proposals")
        os.makedirs(self.proposals_dir, exist_ok=True)

    def create_from_provider_result(
        self,
        queue_seed_id: str,
        objective: str,
        provider_result: Dict[str, Any],
        allowed_paths: List[str],
        srt_anchor_id: Optional[str] = None,
        source: str = "assistant_provider",
    ) -> Dict[str, Any]:
        proposal = ChangeProposal.create(
            seed_id=queue_seed_id,
            task=objective,
            source=source,
        )
        metadata = self._extract_provider_metadata(provider_result)
        proposed_changes = self._extract_changes(provider_result)
        if not proposed_changes and metadata.get("content"):
            proposed_changes = self._extract_changes_from_text(metadata["content"])
        for change in proposed_changes:
            file_path = str(change.get("file_path") or change.get("path") or "").strip()
            if not file_path:
                continue
            action = str(change.get("action") or "MODIFY").strip().upper()
            if action not in {"MODIFY", "CREATE", "DELETE"}:
                action = "MODIFY"
            proposal.add_change(
                file_path=file_path,
                action=action,
                scope=str(change.get("scope") or ""),
                estimated_lines=int(change.get("estimated_lines_changed") or change.get("estimated_lines") or 0),
                risk_tags=list(change.get("risk_tags") or []),
                rationale=str(change.get("rationale") or "Provider proposed change"),
            )
        proposal.compute_hash()
        boundary = self._validate_allowed_paths(proposal, allowed_paths)
        validator = ProposalValidator(workspace_root=self.repo_path)
        validation = validator.validate(proposal)
        status = "awaiting_review" if boundary["allowed"] and validation["approved"] else "rejected"
        record = {
            "proposal": proposal.to_dict(),
            "queue_seed_id": queue_seed_id,
            "srt_anchor_id": srt_anchor_id,
            "status": status,
            "provider_metadata": metadata,
            "provider_changes": proposed_changes,
            "boundary_validation": boundary,
            "proposal_validation": validation,
            "allowed_paths": list(allowed_paths or []),
            "created_at": _utc_now(),
            "applied": False,
            "apply_blocked_reason": "Human approval and write validation are required before source mutation.",
        }
        path = self._proposal_path(proposal.proposal_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, sort_keys=True, default=str)
        record["proposal_path"] = path
        return record

    def list_proposals(self, queue_seed_id: Optional[str] = None) -> Dict[str, Any]:
        records: List[Dict[str, Any]] = []
        if not os.path.exists(self.proposals_dir):
            return {"status": "ok", "proposals": [], "count": 0}
        for name in sorted(os.listdir(self.proposals_dir)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(self.proposals_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    record = json.load(f)
            except (OSError, ValueError):
                continue
            if queue_seed_id and record.get("queue_seed_id") != queue_seed_id:
                continue
            proposal = record.get("proposal") or {}
            records.append({
                "proposal_id": proposal.get("proposal_id"),
                "queue_seed_id": record.get("queue_seed_id"),
                "srt_anchor_id": record.get("srt_anchor_id"),
                "status": record.get("status"),
                "files_write": proposal.get("files_write", []),
                "files_create": proposal.get("files_create", []),
                "files_delete": proposal.get("files_delete", []),
                "created_at": record.get("created_at"),
                "applied": record.get("applied", False),
                "proposal_path": path,
                "boundary_allowed": (record.get("boundary_validation") or {}).get("allowed"),
            })
        return {"status": "ok", "proposals": records, "count": len(records)}

    def get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        path = self._proposal_path(proposal_id)
        if not os.path.exists(path):
            return {"status": "not_found", "proposal_id": proposal_id}
        with open(path, "r", encoding="utf-8") as f:
            record = json.load(f)
        record["status_code"] = "ok"
        record["proposal_path"] = path
        return record

    def review_proposal(self, proposal_id: str, action: str, actor: str = "human", reason: str = "") -> Dict[str, Any]:
        record = self.get_proposal(proposal_id)
        if record.get("status") == "not_found":
            return record
        action = str(action or "").strip().lower()
        transitions = {
            "approve": "approved",
            "reject": "rejected",
            "return": "returned",
            "revise": "returned",
        }
        if action not in transitions:
            return {"status": "invalid_action", "proposal_id": proposal_id, "error": "Supported actions: approve, reject, return."}
        if action == "approve":
            boundary = record.get("boundary_validation") or {}
            validation = record.get("proposal_validation") or {}
            if not boundary.get("allowed") or not validation.get("approved"):
                return {
                    "status": "blocked",
                    "proposal_id": proposal_id,
                    "error": "Only boundary-valid proposals can be approved.",
                }
        previous_status = record.get("status")
        record["status"] = transitions[action]
        record.setdefault("review_events", []).append({
            "action": action,
            "actor": actor or "human",
            "reason": reason or "",
            "previous_status": previous_status,
            "status": record["status"],
            "timestamp": _utc_now(),
        })
        record["updated_at"] = _utc_now()
        path = self._proposal_path(proposal_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, sort_keys=True, default=str)
        return {
            "status": record["status"],
            "proposal_id": proposal_id,
            "queue_seed_id": record.get("queue_seed_id"),
            "proposal": record.get("proposal"),
            "event": record["review_events"][-1],
            "applied": False,
        }

    def apply_proposal(self, proposal_id: str, actor: str = "human") -> Dict[str, Any]:
        """Atomically apply deterministic content and roll back unless evidence is VERIFIED."""
        record = self.get_proposal(proposal_id)
        if record.get("status") == "not_found":
            return record
        if record.get("status") != "approved":
            return {"status": "blocked", "proposal_id": proposal_id, "error": "Proposal must be approved before apply."}
        if record.get("applied"):
            return {"status": "blocked", "proposal_id": proposal_id, "error": "Proposal has already been applied."}
        boundary = record.get("boundary_validation") or {}
        validation = record.get("proposal_validation") or {}
        if not boundary.get("allowed") or not validation.get("approved"):
            return {"status": "blocked", "proposal_id": proposal_id, "error": "Proposal boundary validation failed."}

        changes = record.get("provider_changes") or []
        prepared = []
        allowed_paths = set(boundary.get("allowed_paths") or [])
        for change in changes:
            file_path = str(change.get("file_path") or change.get("path") or "").strip()
            action = str(change.get("action") or "MODIFY").strip().upper()
            content = change.get("new_content")
            if content is None:
                content = change.get("content")
            if action not in {"MODIFY", "CREATE"}:
                return {"status": "blocked", "proposal_id": proposal_id, "error": f"Action {action} is not supported by the safe apply gate yet."}
            if content is None:
                return {"status": "blocked", "proposal_id": proposal_id, "error": f"Change for {file_path} lacks new_content/content."}
            rel_path = self._normalize_rel(file_path)
            if rel_path not in allowed_paths:
                return {"status": "blocked", "proposal_id": proposal_id, "error": f"{rel_path} is outside allowed paths."}
            abs_path = os.path.realpath(os.path.join(self.repo_path, rel_path))
            try:
                inside_repo = os.path.commonpath([self.repo_path, abs_path]) == self.repo_path
            except ValueError:
                inside_repo = False
            if not inside_repo:
                return {"status": "blocked", "proposal_id": proposal_id, "error": f"{rel_path} escapes repository root."}
            if os.path.lexists(abs_path) and os.path.islink(abs_path):
                return {"status": "blocked", "proposal_id": proposal_id, "error": f"Symbolic-link targets are not applyable: {rel_path}."}
            if action == "MODIFY" and not os.path.exists(abs_path):
                return {"status": "blocked", "proposal_id": proposal_id, "error": f"Cannot modify missing file {rel_path}."}
            current_hash = self._hash_path(abs_path)
            expected_hash = change.get("original_hash") or change.get("base_hash") or change.get("expected_hash")
            if expected_hash and expected_hash != current_hash:
                return {"status": "blocked", "proposal_id": proposal_id, "error": f"{rel_path} changed after the proposal was created."}
            prepared.append({
                "path": rel_path,
                "abs_path": abs_path,
                "action": action,
                "content": str(content),
                "before_hash": current_hash,
                "backup": self._read_bytes(abs_path),
                "temp_path": None,
            })

        if not prepared:
            return {"status": "blocked", "proposal_id": proposal_id, "error": "No applyable changes found."}

        from srt1_platform.verification import PostExecutionVerifier
        verifier = PostExecutionVerifier(workspace_root=self.repo_path)
        files_write = [item["path"] for item in prepared if item["action"] == "MODIFY"]
        files_create = [item["path"] for item in prepared if item["action"] == "CREATE"]
        target_paths = set(files_write + files_create)
        files_must_not_change = [path for path in self._repository_files() if path not in target_paths]
        verifier.capture_snapshot(proposal_id, files_to_watch=files_write + files_create, files_must_not_change=files_must_not_change)
        rollback_performed = False
        verification_data: Dict[str, Any]
        try:
            for item in prepared:
                parent = os.path.dirname(item["abs_path"])
                os.makedirs(parent, exist_ok=True)
                handle, temp_path = tempfile.mkstemp(prefix=".srt1-apply-", dir=parent)
                item["temp_path"] = temp_path
                with os.fdopen(handle, "w", encoding="utf-8", newline="") as temp_file:
                    temp_file.write(item["content"])

            for item in prepared:
                if self._hash_path(item["abs_path"]) != item["before_hash"]:
                    raise RuntimeError(f"{item['path']} changed while the proposal was being prepared")
            for item in prepared:
                os.replace(item["temp_path"], item["abs_path"])
                item["temp_path"] = None

            verification = verifier.verify(
                proposal_id,
                files_write=files_write,
                files_create=files_create,
                files_must_not_change=files_must_not_change,
            )
            verification_data = verification.to_dict()
            record["applied"] = verification.verdict == "VERIFIED"
            if not record["applied"]:
                self._restore_prepared(prepared)
                rollback_performed = True
        except Exception as exc:
            self._restore_prepared(prepared)
            rollback_performed = True
            record["applied"] = False
            verification_data = {
                "verdict": "FAILED",
                "evidence_id": "verify_" + hashlib.sha256(str(exc).encode("utf-8")).hexdigest()[:16],
                "timestamp": _utc_now(),
                "scope_violations": [],
                "collateral_damage": [],
                "structural_warnings": [str(exc)],
                "stats": {"proposal_id": proposal_id, "rollback_performed": True},
            }
        finally:
            for item in prepared:
                temp_path = item.get("temp_path")
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

        record["status"] = "completed" if record["applied"] else "returned"
        record["apply_result"] = {
            "actor": actor or "human",
            "timestamp": _utc_now(),
            "files_changed": [item["path"] for item in prepared] if record["applied"] else [],
            "attempted_files": [item["path"] for item in prepared],
            "rollback_performed": rollback_performed,
            "verification": verification_data,
        }
        record["updated_at"] = _utc_now()
        self._persist_record(proposal_id, record)
        return {
            "status": record["status"],
            "proposal_id": proposal_id,
            "queue_seed_id": record.get("queue_seed_id"),
            "applied": record["applied"],
            "files_changed": record["apply_result"]["files_changed"],
            "rollback_performed": rollback_performed,
            "verification": verification_data,
        }

    @staticmethod
    def _hash_path(path: str) -> Optional[str]:
        try:
            with open(path, "rb") as source:
                return hashlib.sha256(source.read()).hexdigest()
        except OSError:
            return None

    @staticmethod
    def _read_bytes(path: str) -> Optional[bytes]:
        try:
            with open(path, "rb") as source:
                return source.read()
        except OSError:
            return None

    def _restore_prepared(self, prepared: List[Dict[str, Any]]) -> None:
        for item in reversed(prepared):
            backup = item.get("backup")
            target = item["abs_path"]
            if backup is None:
                if os.path.exists(target):
                    os.remove(target)
                continue
            parent = os.path.dirname(target)
            handle, temp_path = tempfile.mkstemp(prefix=".srt1-rollback-", dir=parent)
            try:
                with os.fdopen(handle, "wb") as temp_file:
                    temp_file.write(backup)
                os.replace(temp_path, target)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def _repository_files(self) -> List[str]:
        excluded = {".git", ".srt1", "__pycache__", "node_modules", "build", "dist"}
        files: List[str] = []
        for root, dirs, names in os.walk(self.repo_path):
            dirs[:] = [name for name in dirs if name not in excluded]
            for name in names:
                absolute = os.path.realpath(os.path.join(root, name))
                if os.path.islink(absolute):
                    continue
                files.append(os.path.relpath(absolute, self.repo_path).replace("\\", "/"))
                if len(files) >= 5000:
                    return files
        return files

    def _persist_record(self, proposal_id: str, record: Dict[str, Any]) -> None:
        path = self._proposal_path(proposal_id)
        handle, temp_path = tempfile.mkstemp(prefix=".proposal-", dir=self.proposals_dir)
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as temp_file:
                json.dump(record, temp_file, indent=2, sort_keys=True, default=str)
            os.replace(temp_path, path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _proposal_path(self, proposal_id: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in proposal_id)
        return os.path.join(self.proposals_dir, f"{safe}.json")

    def _validate_allowed_paths(self, proposal: ChangeProposal, allowed_paths: List[str]) -> Dict[str, Any]:
        allowed = {self._normalize_rel(path) for path in allowed_paths or [] if path}
        targets = [
            self._normalize_rel(path)
            for path in proposal.files_write + proposal.files_create + proposal.files_delete
        ]
        violations = [path for path in targets if path not in allowed]
        return {
            "allowed": bool(targets) and not violations,
            "targets": targets,
            "allowed_paths": sorted(allowed),
            "violations": violations,
        }

    def _normalize_rel(self, path: str) -> str:
        raw = str(path or "").replace("\\", "/").strip()
        if os.path.isabs(raw):
            raw = os.path.relpath(os.path.realpath(raw), self.repo_path)
        return raw.replace("\\", "/").strip("/")

    def _extract_provider_metadata(self, provider_result: Dict[str, Any]) -> Dict[str, Any]:
        result = provider_result.get("result") if isinstance(provider_result, dict) else None
        content = ""
        if isinstance(result, dict):
            choices = result.get("choices") or []
            if choices:
                message = choices[0].get("message") or {}
                content = str(message.get("content") or "")
        return {
            "provider": provider_result.get("provider") if isinstance(provider_result, dict) else None,
            "model": provider_result.get("model") if isinstance(provider_result, dict) else None,
            "endpoint": provider_result.get("endpoint") if isinstance(provider_result, dict) else None,
            "content": content,
        }

    def _extract_changes(self, provider_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not isinstance(provider_result, dict):
            return []
        for key in ("proposed_changes", "changes"):
            value = provider_result.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        result = provider_result.get("result")
        if isinstance(result, dict):
            for key in ("proposed_changes", "changes"):
                value = result.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    def _extract_changes_from_text(self, content: str) -> List[Dict[str, Any]]:
        text = str(content or "").strip()
        if not text:
            return []
        candidates = [text]
        if "```" in text:
            parts = text.split("```")
            candidates.extend(part.strip() for part in parts if part.strip())
        for candidate in candidates:
            cleaned = candidate.strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                parsed = json.loads(cleaned)
            except (TypeError, ValueError):
                continue
            if isinstance(parsed, dict):
                for key in ("proposed_changes", "changes"):
                    value = parsed.get(key)
                    if isinstance(value, list):
                        return [item for item in value if isinstance(item, dict)]
            if isinstance(parsed, list):
                return [item for item in parsed if isinstance(item, dict)]
        return []
