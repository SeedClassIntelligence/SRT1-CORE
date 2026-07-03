#!/usr/bin/env python3
"""Core-safe Repository Activation registry.

Repository Activation is the first product bootstrapping layer: it records the
local repositories SRT-1 is allowed to manage before Repo Understanding creates
manifests, FileCells, and WorkCells.
"""

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now().isoformat()


def _repo_id_for_path(path: str) -> str:
    normalized = os.path.realpath(path).lower()
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]
    return f"repo_{digest}"


@dataclass
class RepositoryRecord:
    repo_id: str
    name: str
    path: str
    status: str = "registered"
    active: bool = False
    runtime_port: Optional[int] = None
    manifest_hash: Optional[str] = None
    file_count: int = 0
    workcell_count: int = 0
    filecell_count: int = 0
    freshness_state: str = "unknown"
    trust_state: Dict[str, str] = field(default_factory=lambda: {
        "signature": "unsigned",
        "verification": "unverified",
        "lineage": "missing",
    })
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    last_indexed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RepositoryActivationRegistry:
    """Local registry of repositories known to this SRT-1 runtime."""

    def __init__(self, state_dir: str):
        self.state_dir = os.path.realpath(state_dir)
        os.makedirs(self.state_dir, exist_ok=True)
        self.registry_file = os.path.join(self.state_dir, "repositories.json")
        self._repositories: Dict[str, RepositoryRecord] = {}
        self.active_repo_id: Optional[str] = None
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.registry_file):
            return
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.active_repo_id = data.get("active_repo_id")
            self._repositories = {
                item["repo_id"]: RepositoryRecord(**item)
                for item in data.get("repositories", [])
            }
        except Exception:
            self._repositories = {}
            self.active_repo_id = None

    def _save(self) -> None:
        data = {
            "version": 1,
            "updated_at": _now(),
            "active_repo_id": self.active_repo_id,
            "repositories": [repo.to_dict() for repo in self._repositories.values()],
        }
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)

    def _summary_from_manifest(
        self,
        manifest: Optional[Dict[str, Any]],
        workcell_count: Optional[int],
    ) -> Dict[str, Any]:
        manifest = manifest or {}
        manifest_hash = (manifest.get("integrity", {}) or {}).get("manifest_hash")
        files = manifest.get("file_manifest", []) or []
        count = len(files)
        return {
            "manifest_hash": manifest_hash,
            "file_count": count,
            "filecell_count": count,
            "workcell_count": workcell_count if workcell_count is not None else count,
            "freshness_state": "fresh" if manifest_hash else "unknown",
            "last_indexed_at": _now() if manifest_hash else None,
        }

    def register_current(
        self,
        repo_path: str,
        runtime_port: Optional[int] = None,
        manifest: Optional[Dict[str, Any]] = None,
        workcell_count: Optional[int] = None,
        activate: bool = True,
    ) -> RepositoryRecord:
        real_path = os.path.realpath(repo_path)
        if not os.path.isdir(real_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")

        repo_id = _repo_id_for_path(real_path)
        existing = self._repositories.get(repo_id)
        summary = self._summary_from_manifest(manifest, workcell_count)
        record = existing or RepositoryRecord(
            repo_id=repo_id,
            name=os.path.basename(real_path) or real_path,
            path=real_path,
        )
        record.name = os.path.basename(real_path) or real_path
        record.path = real_path
        record.runtime_port = runtime_port
        record.status = "ready" if summary["manifest_hash"] else "registered"
        record.manifest_hash = summary["manifest_hash"]
        record.file_count = summary["file_count"]
        record.filecell_count = summary["filecell_count"]
        record.workcell_count = summary["workcell_count"]
        record.freshness_state = summary["freshness_state"]
        record.last_indexed_at = summary["last_indexed_at"] or record.last_indexed_at
        record.updated_at = _now()
        self._repositories[repo_id] = record

        if activate:
            self.activate(repo_id, save=False)
        self._save()
        return record

    def register_path(
        self,
        repo_path: str,
        runtime_port: Optional[int] = None,
        activate: bool = False,
    ) -> RepositoryRecord:
        """Register a local repository path before a runtime is launched for it."""
        real_path = os.path.realpath(repo_path)
        if not os.path.isdir(real_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")

        repo_id = _repo_id_for_path(real_path)
        record = self._repositories.get(repo_id) or RepositoryRecord(
            repo_id=repo_id,
            name=os.path.basename(real_path) or real_path,
            path=real_path,
        )
        record.name = os.path.basename(real_path) or real_path
        record.path = real_path
        record.runtime_port = runtime_port
        record.status = record.status if record.manifest_hash else "registered"
        record.freshness_state = record.freshness_state or "unknown"
        record.updated_at = _now()
        self._repositories[repo_id] = record

        if activate:
            self.activate(repo_id, save=False)
        self._save()
        return record

    def activate(self, repo_id: str, save: bool = True) -> RepositoryRecord:
        if repo_id not in self._repositories:
            raise KeyError(f"Repository not registered: {repo_id}")
        for record in self._repositories.values():
            record.active = False
        active = self._repositories[repo_id]
        active.active = True
        active.updated_at = _now()
        self.active_repo_id = repo_id
        if save:
            self._save()
        return active

    def list_repositories(self) -> List[Dict[str, Any]]:
        return [repo.to_dict() for repo in self._repositories.values()]

    def active_repository(self) -> Optional[Dict[str, Any]]:
        if self.active_repo_id and self.active_repo_id in self._repositories:
            return self._repositories[self.active_repo_id].to_dict()
        active = next((repo for repo in self._repositories.values() if repo.active), None)
        return active.to_dict() if active else None

    def summary(self) -> Dict[str, Any]:
        repositories = self.list_repositories()
        active = self.active_repository()
        return {
            "status": "ready" if active else "not_registered",
            "active_repo_id": self.active_repo_id,
            "active_repository": active,
            "repositories": repositories,
            "count": len(repositories),
            "registry_file": self.registry_file,
        }
