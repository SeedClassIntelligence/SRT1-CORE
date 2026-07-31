"""Native SRT-1 WorkCell execution runtime contract.

This module is not an assistant adapter. It defines the SRT-1-owned execution
boundary that Codex-derived or open-weight code-agent capability must obey.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


EXECUTION_STATUSES = {
    "queued",
    "running",
    "blocked",
    "completed",
    "failed",
    "cancelled",
}

SECRET_FIELD_NAMES = {
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "password",
    "private_key",
    "secret",
    "session_token",
    "access_token",
    "refresh_token",
}


class NativeExecutionError(RuntimeError):
    """Base error for native execution runtime failures."""


class NativeExecutionBoundaryError(NativeExecutionError):
    """Raised when a native execution request or result escapes SRT-1 authority."""


def _now() -> str:
    return datetime.now().isoformat()


def _safe_slug(value: str) -> str:
    allowed = []
    for char in str(value or ""):
        if char.isalnum() or char in {"-", "_"}:
            allowed.append(char)
        else:
            allowed.append("_")
    return "".join(allowed).strip("_")[:96] or "execution"


def _normalize_rel(path: str) -> str:
    normalized = str(path or "").replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _is_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _contains_secret_field(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).strip().lower()
            if lowered in SECRET_FIELD_NAMES:
                return True
            if _contains_secret_field(item):
                return True
    elif isinstance(value, list):
        return any(_contains_secret_field(item) for item in value)
    return False


@dataclass
class NativeExecutionPackage:
    """SRT-1-owned execution package for one bounded WorkCell job."""

    queue_seed_id: str
    objective: str
    repo_path: str
    workcell_package_path: str
    allowed_paths: List[str]
    restricted_paths: List[str] = field(default_factory=list)
    verification_commands: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NativeExecutionResult:
    """Structured evidence returned by the native execution runtime."""

    execution_id: str
    queue_seed_id: str
    status: str
    summary: str = ""
    files_read: List[str] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    commands_run: List[Dict[str, Any]] = field(default_factory=list)
    tests_run: List[Dict[str, Any]] = field(default_factory=list)
    verification_evidence: List[Dict[str, Any]] = field(default_factory=list)
    proposed_changes: List[Dict[str, Any]] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    next_recommendation: str = ""
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_native_execution_dict(cls, data: Dict[str, Any]) -> "NativeExecutionResult":
        return cls(
            execution_id=str(data.get("execution_id") or ""),
            queue_seed_id=str(data.get("queue_seed_id") or ""),
            status=str(data.get("status") or ""),
            summary=str(data.get("summary") or ""),
            files_read=list(data.get("files_read") or []),
            files_changed=list(data.get("files_changed") or []),
            commands_run=list(data.get("commands_run") or []),
            tests_run=list(data.get("tests_run") or []),
            verification_evidence=list(data.get("verification_evidence") or []),
            proposed_changes=list(data.get("proposed_changes") or []),
            blockers=list(data.get("blockers") or []),
            risks=list(data.get("risks") or []),
            next_recommendation=str(data.get("next_recommendation") or ""),
            created_at=str(data.get("created_at") or _now()),
        )


class SRT1NativeExecutionRuntime:
    """Native WorkCell execution boundary owned by SRT-1."""

    def __init__(self, repo_path: str, runtime_dir: Optional[str] = None):
        self.repo_path = Path(repo_path).resolve()
        self.runtime_dir = Path(runtime_dir or self.repo_path / ".srt1" / "native_execution").resolve()
        if not _is_under(self.runtime_dir, self.repo_path):
            raise NativeExecutionBoundaryError("Native execution directory must stay inside repository")
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def create_execution(self, package: NativeExecutionPackage) -> str:
        """Create a native SRT-1 execution record for a bounded WorkCell package."""

        self._validate_package(package)
        execution_id = f"nexec_{_safe_slug(package.queue_seed_id)}"
        execution_dir = self._execution_dir(execution_id)
        execution_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(execution_dir / "request.json", package.to_dict())
        self._write_json(execution_dir / "state.json", {
            "execution_id": execution_id,
            "queue_seed_id": package.queue_seed_id,
            "status": "queued",
            "created_at": _now(),
            "updated_at": _now(),
            "authority": "SRT-1 WorkCell",
            "runtime_surface": "native_execution",
        })
        return execution_id

    def start(self, execution_id: str) -> Dict[str, Any]:
        """Mark an execution accepted by the native runtime boundary.

        This method does not run arbitrary code yet. It records that SRT-1 has
        admitted the WorkCell package into the native execution runtime.
        """

        state = self._load_state(execution_id)
        if state["status"] not in {"queued", "blocked"}:
            raise NativeExecutionError(f"Cannot start execution in {state['status']} state")
        state["status"] = "running"
        state["updated_at"] = _now()
        state["message"] = "Native execution accepted bounded WorkCell package."
        self._write_json(self._execution_dir(execution_id) / "state.json", state)
        return dict(state)

    def status(self, execution_id: str) -> Dict[str, Any]:
        """Return current native execution state."""

        return self._load_state(execution_id)

    def cancel(self, execution_id: str, reason: str = "") -> Dict[str, Any]:
        """Cancel a native execution without deleting its evidence."""

        state = self._load_state(execution_id)
        if state["status"] in {"completed", "cancelled"}:
            return dict(state)
        state["status"] = "cancelled"
        state["updated_at"] = _now()
        state["cancel_reason"] = reason or "cancelled by SRT-1"
        self._write_json(self._execution_dir(execution_id) / "state.json", state)
        return dict(state)

    def collect_result(self, execution_id: str) -> NativeExecutionResult:
        """Read, validate, and return a native execution result."""

        execution_dir = self._execution_dir(execution_id)
        result_path = execution_dir / "result.json"
        if not result_path.exists():
            raise NativeExecutionError("Native execution result is not available")
        result = NativeExecutionResult.from_native_execution_dict(self._read_json(result_path))
        request = NativeExecutionPackage(**self._read_json(execution_dir / "request.json"))
        self._validate_result(request, result)
        state = self._load_state(execution_id)
        state["status"] = result.status
        state["updated_at"] = _now()
        self._write_json(execution_dir / "state.json", state)
        return result

    def record_result(self, result: NativeExecutionResult) -> Dict[str, Any]:
        """Record a result produced by a local runner or subprocess runtime."""

        execution_dir = self._execution_dir(result.execution_id)
        if not execution_dir.exists():
            raise NativeExecutionError("Native execution does not exist")
        request = NativeExecutionPackage(**self._read_json(execution_dir / "request.json"))
        self._validate_result(request, result)
        self._write_json(execution_dir / "result.json", result.to_dict())
        state = self._load_state(result.execution_id)
        state["status"] = result.status
        state["updated_at"] = _now()
        state["message"] = result.summary
        self._write_json(execution_dir / "state.json", state)
        return dict(state)

    def _validate_package(self, package: NativeExecutionPackage) -> None:
        if not package.queue_seed_id:
            raise NativeExecutionBoundaryError("Native execution requires a queue_seed_id")
        if not package.objective:
            raise NativeExecutionBoundaryError("Native execution requires an objective")
        if not package.allowed_paths:
            raise NativeExecutionBoundaryError("Native execution requires validated WorkCell allowed paths")

        package_repo = Path(package.repo_path).resolve()
        if package_repo != self.repo_path:
            raise NativeExecutionBoundaryError("Package repo_path must match runtime repo_path")

        package_path = Path(package.workcell_package_path).resolve()
        if not _is_under(package_path, self.repo_path / ".srt1" / "workcells"):
            raise NativeExecutionBoundaryError("Execution requires a WorkCell package under .srt1/workcells")

        for path in package.allowed_paths:
            self._validate_repo_relative_path(path)

        for path in package.restricted_paths:
            self._validate_repo_relative_path(path)

        if _contains_secret_field(package.metadata):
            raise NativeExecutionBoundaryError("Native execution package metadata cannot include secrets")

    def _validate_result(self, package: NativeExecutionPackage, result: NativeExecutionResult) -> None:
        if result.execution_id != f"nexec_{_safe_slug(package.queue_seed_id)}":
            raise NativeExecutionBoundaryError("Result execution_id does not match WorkCell execution")
        if result.queue_seed_id != package.queue_seed_id:
            raise NativeExecutionBoundaryError("Result queue_seed_id does not match WorkCell package")
        if result.status not in EXECUTION_STATUSES:
            raise NativeExecutionBoundaryError(f"Invalid native execution status: {result.status}")
        if _contains_secret_field(result.to_dict()):
            raise NativeExecutionBoundaryError("Native execution result cannot include secrets")

        allowed = {_normalize_rel(path) for path in package.allowed_paths}
        restricted = {_normalize_rel(path) for path in package.restricted_paths}
        changed = {_normalize_rel(path) for path in result.files_changed}
        proposed = {
            _normalize_rel(change.get("file_path") or change.get("path") or "")
            for change in result.proposed_changes
        }
        touched = {path for path in changed | proposed if path}

        for path in touched:
            self._validate_repo_relative_path(path)
            if path in restricted:
                raise NativeExecutionBoundaryError(f"Native execution touched restricted path: {path}")
            if path not in allowed:
                raise NativeExecutionBoundaryError(f"Native execution touched path outside WorkCell scope: {path}")

        if result.status == "completed" and not result.verification_evidence and not result.tests_run:
            raise NativeExecutionBoundaryError("Completed native execution requires verification evidence or tests")

    def _validate_repo_relative_path(self, path: str) -> None:
        normalized = _normalize_rel(path)
        if not normalized or normalized.startswith("../") or normalized.startswith("/"):
            raise NativeExecutionBoundaryError(f"Invalid repository-relative path: {path}")
        absolute = (self.repo_path / normalized).resolve()
        if not _is_under(absolute, self.repo_path):
            raise NativeExecutionBoundaryError(f"Path escaped repository: {path}")

    def _execution_dir(self, execution_id: str) -> Path:
        path = (self.runtime_dir / _safe_slug(execution_id)).resolve()
        if not _is_under(path, self.runtime_dir):
            raise NativeExecutionBoundaryError("Execution path escaped native runtime directory")
        return path

    def _load_state(self, execution_id: str) -> Dict[str, Any]:
        state_path = self._execution_dir(execution_id) / "state.json"
        if not state_path.exists():
            raise NativeExecutionError("Native execution does not exist")
        return self._read_json(state_path)

    def _read_json(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        if not _is_under(path.resolve(), self.runtime_dir):
            raise NativeExecutionBoundaryError("Native execution write escaped runtime directory")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
