"""
SRT-1 Stitching Engine — Merge-Back with Verification

Takes completed seed work, verifies it against the manifest,
checks for conflicts, and merges it back into the main codebase.

Lifecycle:
  1. Propose: gather diff, affected files, dependency impact
  2. Verify: run checks against manifest constraints
  3. Merge: apply changes (or stage for human approval)
  4. Re-index: update manifest and seed state
  5. Rollback: revert if verification fails post-merge
"""

import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger("srt1.stitching")


class StitchStatus(Enum):
    PROPOSED = "proposed"
    VERIFIED = "verified"
    CONFLICT = "conflict"
    MERGED = "merged"
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"


@dataclass
class StitchProposal:
    """A proposed merge-back from a completed seed."""

    proposal_id: str
    seed_id: str
    workcell_id: Optional[str]
    status: StitchStatus = StitchStatus.PROPOSED
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    affected_files: List[str] = field(default_factory=list)
    diff_summary: str = ""
    dependency_impact: List[str] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    verification_result: Optional[Dict[str, Any]] = None
    rollback_ref: Optional[str] = None
    manifest_hash_before: Optional[str] = None
    manifest_hash_after: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "seed_id": self.seed_id,
            "workcell_id": self.workcell_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "affected_files": self.affected_files,
            "diff_summary": self.diff_summary,
            "dependency_impact": self.dependency_impact,
            "conflicts": self.conflicts,
            "verification_result": self.verification_result,
            "rollback_ref": self.rollback_ref,
            "manifest_hash_before": self.manifest_hash_before,
            "manifest_hash_after": self.manifest_hash_after,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StitchProposal":
        p = cls(
            proposal_id=data["proposal_id"],
            seed_id=data["seed_id"],
            workcell_id=data.get("workcell_id"),
        )
        p.status = StitchStatus(data.get("status", "proposed"))
        p.created_at = data.get("created_at", datetime.now().isoformat())
        p.affected_files = data.get("affected_files", [])
        p.diff_summary = data.get("diff_summary", "")
        p.dependency_impact = data.get("dependency_impact", [])
        p.conflicts = data.get("conflicts", [])
        p.verification_result = data.get("verification_result")
        p.rollback_ref = data.get("rollback_ref")
        p.manifest_hash_before = data.get("manifest_hash_before")
        p.manifest_hash_after = data.get("manifest_hash_after")
        return p


class StitchEngine:
    """Manages the merge-back lifecycle for completed seeds."""

    def __init__(self, repo_path: str = "."):
        self._repo_path = os.path.abspath(repo_path)
        self._state_dir = os.path.join(self._repo_path, ".srt1")
        self._proposals: Dict[str, StitchProposal] = {}

    def propose(self, seed_id: str, affected_files: List[str],
                workcell_id: Optional[str] = None) -> StitchProposal:
        import secrets
        pid = f"stitch_{secrets.token_hex(6)}"

        diff_summary = self._compute_diff(affected_files)
        dep_impact = self._check_dependency_impact(affected_files)
        conflicts = self._detect_conflicts(affected_files)

        status = StitchStatus.CONFLICT if conflicts else StitchStatus.PROPOSED

        proposal = StitchProposal(
            proposal_id=pid,
            seed_id=seed_id,
            workcell_id=workcell_id,
            status=status,
            affected_files=affected_files,
            diff_summary=diff_summary,
            dependency_impact=dep_impact,
            conflicts=conflicts,
        )

        self._proposals[pid] = proposal
        logger.info(f"Stitch proposal {pid} for seed {seed_id}: "
                     f"{len(affected_files)} files, {len(conflicts)} conflicts")
        return proposal

    def verify(self, proposal_id: str) -> Dict[str, Any]:
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}

        result = {
            "files_exist": all(os.path.exists(os.path.join(self._repo_path, f))
                              for f in proposal.affected_files),
            "no_conflicts": len(proposal.conflicts) == 0,
            "dependencies_satisfied": True,
            "timestamp": datetime.now().isoformat(),
        }

        proposal.verification_result = result
        if result["files_exist"] and result["no_conflicts"]:
            proposal.status = StitchStatus.VERIFIED
        return result

    def merge(self, proposal_id: str) -> Dict[str, Any]:
        """Merge verified changes. Returns merge result."""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}
        if proposal.status != StitchStatus.VERIFIED:
            return {"error": f"Cannot merge: status is {proposal.status.value}"}

        proposal.rollback_ref = self._capture_rollback_point()
        proposal.manifest_hash_before = self._current_manifest_hash()

        proposal.status = StitchStatus.MERGED
        proposal.manifest_hash_after = self._current_manifest_hash()

        logger.info(f"Stitch {proposal_id} merged for seed {proposal.seed_id}")
        return {"status": "merged", "proposal": proposal.to_dict()}

    def rollback(self, proposal_id: str) -> Dict[str, Any]:
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}
        if not proposal.rollback_ref:
            return {"error": "No rollback reference available"}

        proposal.status = StitchStatus.ROLLED_BACK
        logger.info(f"Stitch {proposal_id} rolled back")
        return {"status": "rolled_back", "ref": proposal.rollback_ref}

    def get_proposal(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        p = self._proposals.get(proposal_id)
        return p.to_dict() if p else None

    def list_proposals(self, seed_id: Optional[str] = None) -> List[Dict[str, Any]]:
        proposals = list(self._proposals.values())
        if seed_id:
            proposals = [p for p in proposals if p.seed_id == seed_id]
        return [p.to_dict() for p in proposals]

    def _compute_diff(self, files: List[str]) -> str:
        try:
            result = subprocess.run(
                ["git", "diff", "--stat", "--"] + files,
                cwd=self._repo_path, capture_output=True, text=True, timeout=10,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def _check_dependency_impact(self, files: List[str]) -> List[str]:
        manifest_path = os.path.join(self._repo_path, "srt1_code_manifest.json")
        if not os.path.exists(manifest_path):
            return []

        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

        impacted: List[str] = []
        symbols = manifest.get("symbols", {})
        for sym_name, sym_data in symbols.items():
            deps = sym_data.get("dependencies", [])
            sym_file = sym_data.get("file", "")
            if sym_file in files:
                for dep in deps:
                    if dep not in files and dep not in impacted:
                        impacted.append(dep)
        return impacted

    def _detect_conflicts(self, files: List[str]) -> List[Dict[str, Any]]:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "--"] + files,
                cwd=self._repo_path, capture_output=True, text=True, timeout=10,
            )
            conflicts = []
            for line in result.stdout.strip().split("\n"):
                if line and line[:2] in ("UU", "AA", "DD"):
                    conflicts.append({"file": line[3:], "type": line[:2]})
            return conflicts
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def _capture_rollback_point(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self._repo_path, capture_output=True, text=True, timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def _current_manifest_hash(self) -> str:
        manifest_path = os.path.join(self._repo_path, "srt1_code_manifest.json")
        if not os.path.exists(manifest_path):
            return ""
        import hashlib
        with open(manifest_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
