# Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
# Author: William Darnell Jernigan IV (THE ORIGINAL SEED)
# Trust awareness: unsigned unless an external authority signs this artifact.

"""
verification.py — Post-Execution Verification
=================================================
Compares intended changes (from ChangeProposal) against actual file
mutations after a bounded local operation completes.

This closes the doctrine loop:
    SRT-1 sees → Context Isolation bounds → local operation acts → SRT-1 verifies

Without this module, changes inside or outside a FileCell could be
accepted without evidence comparison.

SCIA Contract: SCIA-CONTRACT-005
"""

import os
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set

logger = logging.getLogger("srt1.verification")


class VerificationResult:
    """Result of a post-execution verification check."""
    
    VERIFIED = "VERIFIED"
    PARTIAL_PASS = "PARTIAL_PASS"
    FAILED = "FAILED"
    
    def __init__(self):
        self.verdict: str = self.VERIFIED
        self.scope_violations: List[Dict[str, str]] = []
        self.collateral_damage: List[Dict[str, str]] = []
        self.structural_warnings: List[str] = []
        self.stats: Dict[str, Any] = {}
        self.timestamp: str = datetime.utcnow().isoformat() + "Z"
    
    def add_scope_violation(self, file_path: str, reason: str) -> None:
        """Record an unauthorized file modification."""
        self.scope_violations.append({"file": file_path, "reason": reason})
        self.verdict = self.FAILED
    
    def add_collateral_damage(self, file_path: str, reason: str) -> None:
        """Record a protected file that was unexpectedly modified."""
        self.collateral_damage.append({"file": file_path, "reason": reason})
        self.verdict = self.FAILED
    
    def add_structural_warning(self, warning: str) -> None:
        """Record a non-fatal structural warning."""
        self.structural_warnings.append(warning)
        if self.verdict == self.VERIFIED:
            self.verdict = self.PARTIAL_PASS
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "verdict": self.verdict,
            "timestamp": self.timestamp,
            "scope_violations": self.scope_violations,
            "collateral_damage": self.collateral_damage,
            "structural_warnings": self.structural_warnings,
            "stats": self.stats,
        }


class PostExecutionVerifier:
    """
    Verifies that actual mutations match the ChangeProposal.
    
    Lifecycle:
        1. capture_snapshot() — before a bounded local operation
        2. operation proceeds inside approved boundary
        3. verify() — after the operation completes
    """
    
    def __init__(self, workspace_root: str, audit_ledger=None):
        self.workspace_root = os.path.abspath(workspace_root)
        self.audit_ledger = audit_ledger
        self._pre_snapshots: Dict[str, Dict[str, str]] = {}  # proposal_id -> {path: hash}
    
    @staticmethod
    def _hash_file(path: str) -> Optional[str]:
        """Compute SHA-256 hash of a file, or None if file doesn't exist."""
        try:
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except (OSError, IOError):
            return None
    
    def capture_snapshot(self, proposal_id: str,
                         files_to_watch: List[str],
                         files_must_not_change: List[str] = None) -> Dict[str, str]:
        """
        Capture file hashes before a bounded local operation.
        
        Args:
            proposal_id: The ChangeProposal ID
            files_to_watch: Files that are expected to change
            files_must_not_change: Files that must remain identical
        
        Returns:
            Dict of {absolute_path: sha256_hash}
        """
        snapshot = {}
        all_files = set(files_to_watch)
        if files_must_not_change:
            all_files.update(files_must_not_change)
        
        for file_path in all_files:
            abs_path = os.path.join(self.workspace_root, file_path) \
                if not os.path.isabs(file_path) else file_path
            abs_path = os.path.realpath(abs_path)
            
            file_hash = self._hash_file(abs_path)
            if file_hash:
                snapshot[abs_path] = file_hash
            else:
                snapshot[abs_path] = "__NOT_FOUND__"
        
        self._pre_snapshots[proposal_id] = snapshot
        
        # ── SCIA Event: post_execution_snapshot_taken ─────────────────
        if self.audit_ledger:
            try:
                self.audit_ledger.record(
                    component="verifier",
                    operation="post_execution_snapshot_taken",
                    severity="INFO",
                    detail={
                        "proposal_id": proposal_id,
                        "files_watched": len(files_to_watch),
                        "files_protected": len(files_must_not_change or []),
                        "snapshot_entries": len(snapshot),
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record snapshot event: {e}")
        
        return snapshot
    
    def verify(self, proposal_id: str,
               files_write: List[str],
               files_create: List[str] = None,
               files_delete: List[str] = None,
               files_must_not_change: List[str] = None,
               max_lines_changed: int = 100) -> VerificationResult:
        """
        Verify post-execution state against the ChangeProposal.
        
        Args:
            proposal_id: The ChangeProposal ID
            files_write: Files authorized for modification
            files_create: Files authorized for creation
            files_delete: Files authorized for deletion
            files_must_not_change: Files that must remain identical
            max_lines_changed: Maximum total lines changed allowed
        
        Returns:
            VerificationResult with verdict and details
        """
        result = VerificationResult()
        files_create = files_create or []
        files_delete = files_delete or []
        files_must_not_change = files_must_not_change or []
        
        pre_snapshot = self._pre_snapshots.get(proposal_id, {})
        
        # Build post-execution snapshot
        post_snapshot: Dict[str, str] = {}
        all_paths = set(pre_snapshot.keys())
        for file_path in files_write + files_create + files_must_not_change:
            abs_path = os.path.join(self.workspace_root, file_path) \
                if not os.path.isabs(file_path) else file_path
            abs_path = os.path.realpath(abs_path)
            all_paths.add(abs_path)
        
        for abs_path in all_paths:
            file_hash = self._hash_file(abs_path)
            post_snapshot[abs_path] = file_hash if file_hash else "__NOT_FOUND__"
        
        # ── Step 1: Scope Validation ──────────────────────────────────────
        # Find all files that actually changed
        authorized_write_abs: Set[str] = set()
        for fp in files_write:
            abs_path = os.path.join(self.workspace_root, fp) \
                if not os.path.isabs(fp) else fp
            authorized_write_abs.add(os.path.realpath(abs_path))
        
        authorized_create_abs: Set[str] = set()
        for fp in files_create:
            abs_path = os.path.join(self.workspace_root, fp) \
                if not os.path.isabs(fp) else fp
            authorized_create_abs.add(os.path.realpath(abs_path))
        
        files_actually_changed = []
        for abs_path in all_paths:
            pre_hash = pre_snapshot.get(abs_path, "__NOT_FOUND__")
            post_hash = post_snapshot.get(abs_path, "__NOT_FOUND__")
            
            if pre_hash != post_hash:
                files_actually_changed.append(abs_path)
                
                # Check if this change was authorized
                if abs_path not in authorized_write_abs and \
                   abs_path not in authorized_create_abs:
                    result.add_scope_violation(
                        abs_path,
                        f"File modified but not in authorized files_write or files_create"
                    )
        
        # ── Step 2: Collateral Damage Check ───────────────────────────────
        for fp in files_must_not_change:
            abs_path = os.path.join(self.workspace_root, fp) \
                if not os.path.isabs(fp) else fp
            abs_path = os.path.realpath(abs_path)
            
            pre_hash = pre_snapshot.get(abs_path)
            post_hash = post_snapshot.get(abs_path)
            
            if pre_hash and post_hash and pre_hash != post_hash:
                result.add_collateral_damage(
                    abs_path,
                    f"Protected file was modified (pre={pre_hash[:12]}... post={post_hash[:12]}...)"
                )
        
        # ── Step 3: Structural Integrity ──────────────────────────────────
        # Check that modified .py files still parse
        for abs_path in files_actually_changed:
            if abs_path.endswith(".py"):
                try:
                    with open(abs_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    compile(source, abs_path, "exec")
                except SyntaxError as e:
                    result.add_structural_warning(
                        f"Syntax error in {abs_path}: {e}"
                    )
                except (OSError, IOError):
                    pass
        
        # ── Step 4: Stats ─────────────────────────────────────────────────
        result.stats = {
            "proposal_id": proposal_id,
            "files_expected_to_change": len(files_write) + len(files_create),
            "files_actually_changed": len(files_actually_changed),
            "files_protected": len(files_must_not_change),
            "scope_violations": len(result.scope_violations),
            "collateral_damage_count": len(result.collateral_damage),
            "structural_warnings": len(result.structural_warnings),
        }
        
        # ── SCIA Events ──────────────────────────────────────────────────
        if self.audit_ledger:
            try:
                if result.verdict == VerificationResult.VERIFIED:
                    self.audit_ledger.record(
                        component="verifier",
                        operation="verification_passed",
                        severity="CRITICAL",
                        detail=result.stats,
                    )
                elif result.verdict == VerificationResult.PARTIAL_PASS:
                    self.audit_ledger.record(
                        component="verifier",
                        operation="verification_passed",
                        severity="WARNING",
                        detail={**result.stats, "partial": True,
                                "warnings": result.structural_warnings},
                    )
                else:
                    self.audit_ledger.record(
                        component="verifier",
                        operation="verification_failed",
                        severity="CRITICAL",
                        detail={
                            **result.stats,
                            "scope_violations": result.scope_violations,
                            "collateral_damage": result.collateral_damage,
                        },
                    )
            except Exception as e:
                logger.warning(f"Failed to record verification event: {e}")
        
        return result
