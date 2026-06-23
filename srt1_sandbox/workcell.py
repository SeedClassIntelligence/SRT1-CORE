"""
SRT-1 Workcell — Scoped Execution Environment

A workcell is a logical sandbox assigned to one seed/task.
It defines the scope of what an AI assistant can touch.

No Docker, no VM — just manifest-governed file-level isolation.
The workcell reads the Code Manifest to know what exists,
and enforces boundaries through context injection.
"""

import json
import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger("srt1.workcell")


class WorkcellScope(Enum):
    REPO = "repo"
    FOLDER = "folder"
    COMPONENT = "component"
    FILE = "file"
    PATCH = "patch"


@dataclass
class Workcell:
    """A scoped execution environment for one seed/task."""

    workcell_id: str
    seed_id: str
    scope: WorkcellScope
    root_path: str

    allowed_reads: List[str] = field(default_factory=list)
    allowed_writes: List[str] = field(default_factory=list)
    forbidden_paths: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    assigned_session: Optional[str] = None
    status: str = "idle"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verification_result: Optional[Dict[str, Any]] = None

    def can_read(self, path: str) -> bool:
        abs_path = os.path.abspath(path)
        if any(abs_path.startswith(os.path.abspath(f)) for f in self.forbidden_paths):
            return False
        if not self.allowed_reads:
            return True
        return any(abs_path.startswith(os.path.abspath(r)) for r in self.allowed_reads)

    def can_write(self, path: str) -> bool:
        abs_path = os.path.abspath(path)
        if any(abs_path.startswith(os.path.abspath(f)) for f in self.forbidden_paths):
            return False
        if not self.allowed_writes:
            return False
        return any(abs_path.startswith(os.path.abspath(w)) for w in self.allowed_writes)

    def check_access(self, path: str, mode: str = "read") -> Dict[str, Any]:
        if mode == "write":
            allowed = self.can_write(path)
        else:
            allowed = self.can_read(path)
        return {
            "path": path,
            "mode": mode,
            "allowed": allowed,
            "workcell_id": self.workcell_id,
            "scope": self.scope.value,
        }

    def to_context_packet(self) -> Dict[str, Any]:
        """Generate the context packet an assistant receives."""
        return {
            "workcell_id": self.workcell_id,
            "seed_id": self.seed_id,
            "scope": self.scope.value,
            "root_path": self.root_path,
            "allowed_reads": self.allowed_reads,
            "allowed_writes": self.allowed_writes,
            "forbidden_paths": self.forbidden_paths,
            "dependencies": self.dependencies,
            "status": self.status,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workcell_id": self.workcell_id,
            "seed_id": self.seed_id,
            "scope": self.scope.value,
            "root_path": self.root_path,
            "allowed_reads": self.allowed_reads,
            "allowed_writes": self.allowed_writes,
            "forbidden_paths": self.forbidden_paths,
            "dependencies": self.dependencies,
            "assigned_session": self.assigned_session,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "verification_result": self.verification_result,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workcell":
        return cls(
            workcell_id=data["workcell_id"],
            seed_id=data["seed_id"],
            scope=WorkcellScope(data["scope"]),
            root_path=data["root_path"],
            allowed_reads=data.get("allowed_reads", []),
            allowed_writes=data.get("allowed_writes", []),
            forbidden_paths=data.get("forbidden_paths", []),
            dependencies=data.get("dependencies", []),
            assigned_session=data.get("assigned_session"),
            status=data.get("status", "idle"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            verification_result=data.get("verification_result"),
        )


class WorkcellRegistry:
    """Registry of active workcells. Persisted to .srt1/workcells.json."""

    def __init__(self, repo_path: str = "."):
        self._repo_path = os.path.abspath(repo_path)
        self._state_dir = os.path.join(self._repo_path, ".srt1")
        self._state_file = os.path.join(self._state_dir, "workcells.json")
        self._workcells: Dict[str, Workcell] = {}
        self._load()

    def create(self, seed_id: str, scope: WorkcellScope,
               root_path: str = "",
               allowed_reads: Optional[List[str]] = None,
               allowed_writes: Optional[List[str]] = None,
               forbidden_paths: Optional[List[str]] = None,
               dependencies: Optional[List[str]] = None) -> Workcell:
        wc_id = f"wc_{secrets.token_hex(6)}"
        wc = Workcell(
            workcell_id=wc_id,
            seed_id=seed_id,
            scope=scope,
            root_path=root_path or self._repo_path,
            allowed_reads=allowed_reads or [],
            allowed_writes=allowed_writes or [],
            forbidden_paths=forbidden_paths or [],
            dependencies=dependencies or [],
        )
        self._workcells[wc_id] = wc
        self._save()
        logger.info(f"Created workcell {wc_id} for seed {seed_id} (scope={scope.value})")
        return wc

    def create_from_manifest(self, seed_id: str, manifest: Dict[str, Any],
                             task_files: List[str]) -> Workcell:
        """Create a workcell scoped to the files relevant to a task."""
        write_dirs: Set[str] = set()
        for f in task_files:
            write_dirs.add(os.path.dirname(os.path.join(self._repo_path, f)))

        dep_files: List[str] = []
        symbols = manifest.get("symbols", {})
        for f in task_files:
            for sym_name, sym_data in symbols.items():
                if sym_data.get("file") == f:
                    dep_files.extend(sym_data.get("dependencies", []))

        return self.create(
            seed_id=seed_id,
            scope=WorkcellScope.COMPONENT,
            allowed_reads=[self._repo_path],
            allowed_writes=list(write_dirs),
            dependencies=list(set(dep_files)),
        )

    def get(self, workcell_id: str) -> Optional[Workcell]:
        return self._workcells.get(workcell_id)

    def get_by_seed(self, seed_id: str) -> Optional[Workcell]:
        for wc in self._workcells.values():
            if wc.seed_id == seed_id:
                return wc
        return None

    def list_active(self) -> List[Dict[str, Any]]:
        return [wc.to_dict() for wc in self._workcells.values()
                if wc.status not in ("closed", "terminated")]

    def close(self, workcell_id: str, verification: Optional[Dict] = None) -> None:
        wc = self._workcells.get(workcell_id)
        if wc:
            wc.status = "closed"
            wc.verification_result = verification
            wc.updated_at = datetime.now().isoformat()
            self._save()

    def _load(self) -> None:
        if os.path.exists(self._state_file):
            try:
                with open(self._state_file, "r") as f:
                    data = json.load(f)
                for wc_data in data.get("workcells", []):
                    wc = Workcell.from_dict(wc_data)
                    self._workcells[wc.workcell_id] = wc
            except (json.JSONDecodeError, KeyError):
                logger.warning("Failed to load workcells state, starting fresh")

    def _save(self) -> None:
        os.makedirs(self._state_dir, exist_ok=True)
        data = {"workcells": [wc.to_dict() for wc in self._workcells.values()]}
        with open(self._state_file, "w") as f:
            json.dump(data, f, indent=2)
