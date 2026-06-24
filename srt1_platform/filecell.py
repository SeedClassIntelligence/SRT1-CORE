import os
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class FileCellBoundaryViolation(Exception):
    """Raised when an execution component attempts to breach its FileCell boundary."""
    pass

@dataclass(frozen=True)
class FileCellManifest:
    """Immutable manifest defining the local boundary of a single workcell task."""
    cell_id: str
    task_intent: str
    allowed_reads: List[str]
    allowed_writes: List[str]
    forbidden_paths: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    output_contract: Dict[str, Any] = field(default_factory=dict)
    dependency_reasoning: str = ""
    
    @classmethod
    def generate(cls, task_intent: str, allowed_reads: List[str],
                 allowed_writes: List[str], forbidden_paths: List[str] = None,
                 dependencies: List[str] = None,
                 dependency_reasoning: str = ""):
        """Helper to generate a cell with canonicalized paths."""
        return cls(
            cell_id=f"cell_{uuid.uuid4().hex[:8]}",
            task_intent=task_intent,
            allowed_reads=[os.path.realpath(p) for p in allowed_reads],
            allowed_writes=[os.path.realpath(p) for p in allowed_writes],
            forbidden_paths=[os.path.realpath(p) for p in (forbidden_paths or [])],
            dependencies=dependencies or [],
            dependency_reasoning=dependency_reasoning,
        )

class FileCellGuard:
    """
    Enforces the FileCell boundaries, using canonical paths to prevent
    traversal, symlink escapes, and unauthorized access.
    """
    
    def __init__(self, audit_ledger=None, signing_client=None):
        self.audit_ledger = audit_ledger
        self.signing_client = signing_client

    def _canonicalize(self, path: str) -> str:
        """Fully resolve the path, following all symlinks."""
        return os.path.realpath(os.path.expanduser(path))

    def _is_path_allowed(self, target_path: str, allowed_roots: List[str]) -> bool:
        """Check if the target path is strictly within any of the allowed roots."""
        for root in allowed_roots:
            try:
                # commonpath raises ValueError if paths are on different drives (Windows)
                if os.path.commonpath([target_path, root]) == root:
                    return True
            except ValueError:
                continue
        return False

    def validate_read(self, path: str, manifest: FileCellManifest) -> bool:
        """
        Validate that a read operation is strictly within allowed_reads.
        (Note: writes do not automatically grant read permissions).
        """
        canonical_path = self._canonicalize(path)
        
        # Check forbidden first
        if self._is_path_allowed(canonical_path, manifest.forbidden_paths):
            self._emit_violation(manifest.cell_id, canonical_path, "read", "Path is explicitly forbidden.")
            raise FileCellBoundaryViolation(f"READ BLOCKED: {path} is explicitly forbidden in FileCell {manifest.cell_id}.")

        if not self._is_path_allowed(canonical_path, manifest.allowed_reads):
            self._emit_violation(manifest.cell_id, canonical_path, "read", "Path is outside allowed_reads.")
            raise FileCellBoundaryViolation(f"READ BLOCKED: {path} is outside allowed_reads scope for FileCell {manifest.cell_id}.")
            
        return True

    def validate_write(self, path: str, manifest: FileCellManifest) -> bool:
        """
        Validate that a write operation is strictly within allowed_writes.
        Reads NEVER imply write permission.
        """
        canonical_path = self._canonicalize(path)
        
        # Check forbidden first
        if self._is_path_allowed(canonical_path, manifest.forbidden_paths):
            self._emit_violation(manifest.cell_id, canonical_path, "write", "Path is explicitly forbidden.")
            raise FileCellBoundaryViolation(f"WRITE BLOCKED: {path} is explicitly forbidden in FileCell {manifest.cell_id}.")

        if not self._is_path_allowed(canonical_path, manifest.allowed_writes):
            self._emit_violation(manifest.cell_id, canonical_path, "write", "Path is outside allowed_writes scope.")
            raise FileCellBoundaryViolation(f"WRITE BLOCKED: {path} is outside allowed_writes scope for FileCell {manifest.cell_id}. Allowed reads DO NOT grant write permissions.")
            
        return True

    def _emit_violation(self, cell_id: str, attempted_path: str, action: str, reason: str):
        """Emit a boundary violation to optional external audit/trust hooks."""
        if not self.audit_ledger:
            return
            
        event_detail = {
            "cell_id": cell_id,
            "attempted_path": attempted_path,
            "action": action,
            "reason": reason,
            "violation_type": "filecell_boundary_escape"
        }

        # 1. Write to optional audit hook when configured.
        self.audit_ledger.record(
            component="filecell_guard",
            operation="filecell_boundary_violation",
            severity="CRITICAL",
            actor="local_workcell_actor",
            detail=event_detail
        )
        
        # 2. Trigger optional external trust hook when configured.
        if self.signing_client:
            try:
                self.signing_client.sign(
                    content=event_detail,
                    phase="governance_violation"
                )
            except Exception:
                pass
