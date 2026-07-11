#!/usr/bin/env python3
"""Core-safe WorkCell registry and execution package support.

WorkCells are persistent bounded architectural environments. Seeds activate
temporary WorkCell executions inside those environments. This module writes
only SRT-1 runtime metadata under `.srt1/workcells`; it does not mutate source
files or perform execution.
"""

import json
import hashlib
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from srt1_platform.filecell import (
    FileCellBoundaryViolation,
    FileCellGuard,
    FileCellManifest,
)


def _now() -> str:
    return datetime.now().isoformat()


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip().lower()).strip("-")
    return slug[:80] or "repository"


def _workcell_id_for_path(path: str) -> str:
    digest = hashlib.sha1(path.replace("\\", "/").encode("utf-8")).hexdigest()[:10]
    slug = _safe_slug(os.path.basename(path) or path)
    return f"workcell_file_{slug}_{digest}"


@dataclass
class WorkCell:
    """Persistent bounded architectural environment."""

    workcell_id: str
    name: str
    purpose: str
    repo_path: str
    owned_paths: List[str] = field(default_factory=list)
    related_paths: List[str] = field(default_factory=list)
    restricted_paths: List[str] = field(default_factory=list)
    authority_scope: List[str] = field(default_factory=lambda: ["repo understanding", "context isolation"])
    default_verification_rules: List[str] = field(default_factory=lambda: [
        "Stay inside approved WorkCell boundary.",
        "Preserve public/Core private-boundary exclusions.",
        "Run relevant tests before completion.",
    ])
    default_runtime_port: Optional[int] = None
    filecell_summary: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    freshness_state: str = "unknown"
    trust_state: Dict[str, str] = field(default_factory=lambda: {
        "signature": "unsigned",
        "verification": "unverified",
        "lineage": "missing",
    })

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkCellExecution:
    """Seed-activated runtime package inside a persistent WorkCell."""

    workcell_execution_id: str
    workcell_id: str
    queue_seed_id: str
    srt_anchor_id: Optional[str]
    objective: str
    status: str = "ready"
    runtime_port: Optional[int] = None
    assigned_agent: str = "unassigned"
    manifest_hash: Optional[str] = None
    trust_state: Dict[str, str] = field(default_factory=lambda: {
        "signature": "unsigned",
        "verification": "unverified",
        "lineage": "missing",
    })
    verification_state: str = "unverified"
    package_path: Optional[str] = None
    package_status: Dict[str, Any] = field(default_factory=dict)
    activity_events: List[Dict[str, Any]] = field(default_factory=list)
    activity_event_count: int = 0
    execution_jobs: List[Dict[str, Any]] = field(default_factory=list)
    current_execution_job_id: Optional[str] = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkCellRegistry:
    """Persistent WorkCell registry plus seed-activated execution records."""

    def __init__(self, repo_path: str, registry_dir: Optional[str] = None):
        self.repo_path = os.path.realpath(repo_path)
        self.registry_dir = registry_dir or os.path.join(self.repo_path, ".srt1", "workcells")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_file = os.path.join(self.registry_dir, "workcell_registry.json")
        self._workcells: Dict[str, WorkCell] = {}
        self._executions: Dict[str, WorkCellExecution] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.registry_file):
            return
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._workcells = {
                item["workcell_id"]: WorkCell(**item)
                for item in data.get("workcells", [])
            }
            self._executions = {
                item["workcell_execution_id"]: WorkCellExecution(**item)
                for item in data.get("executions", [])
            }
            for execution in self._executions.values():
                if execution.activity_event_count < len(execution.activity_events):
                    execution.activity_event_count = len(execution.activity_events)
        except Exception:
            self._workcells = {}
            self._executions = {}

    def _save(self) -> None:
        data = {
            "repo_path": self.repo_path,
            "updated_at": _now(),
            "workcells": [wc.to_dict() for wc in self._workcells.values()],
            "executions": [ex.to_dict() for ex in self._executions.values()],
        }
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)

    def _find_file_entry(self, manifest: Dict[str, Any], path: str) -> Dict[str, Any]:
        target = path.replace("\\", "/")
        for entry in manifest.get("file_manifest", []) or []:
            entry_path = (entry.get("file_path") or entry.get("path") or "").replace("\\", "/")
            if entry_path == target:
                return entry
        return {}

    def _symbols_for_path(self, manifest: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
        symbol_table = manifest.get("symbol_table", {}) or {}
        candidates = [
            path,
            path.replace("\\", "/"),
            path.replace("/", "\\"),
        ]
        for candidate in candidates:
            if candidate in symbol_table:
                return symbol_table.get(candidate) or []
        target = path.replace("\\", "/")
        for table_path, symbols in symbol_table.items():
            if str(table_path).replace("\\", "/") == target:
                return symbols or []
        return []

    def _build_filecell_summary(self, path: str, manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        manifest = manifest or {}
        entry = self._find_file_entry(manifest, path)
        symbols = self._symbols_for_path(manifest, path)
        manifest_hash = manifest.get("integrity", {}).get("manifest_hash")

        roles: Dict[str, int] = {}
        risks: Dict[str, int] = {}
        dependencies = []
        compact_symbols = []
        for symbol in symbols:
            reflection = symbol.get("reflection", {}) or {}
            role = reflection.get("architectural_role", "GENERAL")
            roles[role] = roles.get(role, 0) + 1
            for risk in reflection.get("risk_profile", []) or []:
                risks[risk] = risks.get(risk, 0) + 1
            for dependency in symbol.get("dependencies", []) or []:
                if dependency not in dependencies:
                    dependencies.append(dependency)
            compact_symbols.append({
                "name": symbol.get("name"),
                "type": symbol.get("type"),
                "line": symbol.get("line"),
                "dependencies": (symbol.get("dependencies", []) or [])[:10],
                "architectural_role": role,
                "risk_profile": reflection.get("risk_profile", []) or [],
            })

        return {
            "filecell_id": f"filecell_{hashlib.sha1(path.replace('\\', '/').encode('utf-8')).hexdigest()[:12]}",
            "path": path,
            "manifest_hash": manifest_hash,
            "file_hash": entry.get("hash") or entry.get("sha256") or entry.get("content_hash"),
            "size": entry.get("size"),
            "extension": entry.get("extension") or os.path.splitext(path)[1],
            "parser": entry.get("parser") or ("ast" if path.endswith(".py") else "structural"),
            "symbol_count": len(symbols),
            "symbols": compact_symbols[:50],
            "dependencies": dependencies[:50],
            "architectural_roles": roles,
            "risk_tags": risks,
            "freshness_state": "fresh" if manifest_hash else "unknown",
            "trust_state": {
                "signature": "unsigned",
                "verification": "unverified",
                "lineage": "missing",
            },
        }

    def populate_from_manifest(self, manifest: Optional[Dict[str, Any]] = None) -> List[WorkCell]:
        """Populate one persistent WorkCell for every repository file."""
        manifest = manifest or {}
        file_entries = manifest.get("file_manifest", []) or []
        manifest_hash = manifest.get("integrity", {}).get("manifest_hash")
        workcells = []

        for entry in file_entries:
            path = entry.get("file_path") or entry.get("path")
            if not path:
                continue
            workcell_id = _workcell_id_for_path(path)
            existing = self._workcells.get(workcell_id)
            if existing:
                existing.updated_at = _now()
                existing.owned_paths = [path]
                existing.filecell_summary = self._build_filecell_summary(path, manifest)
                existing.freshness_state = "fresh" if manifest_hash else existing.freshness_state
                workcells.append(existing)
                continue

            workcell = WorkCell(
                workcell_id=workcell_id,
                name=path,
                purpose=f"Smallest safe execution boundary for {path}.",
                repo_path=self.repo_path,
                owned_paths=[path],
                restricted_paths=[
                    ".git/",
                    ".srt1/seeds/",
                    ".srt1/runtime/",
                    "memory/",
                    "scia_memory/",
                    "scia_security/",
                ],
                filecell_summary=self._build_filecell_summary(path, manifest),
                freshness_state="fresh" if manifest_hash else "unknown",
            )
            self._workcells[workcell_id] = workcell
            workcells.append(workcell)

        if workcells:
            self._save()
        return workcells

    def infer_workcell(self, objective: str, manifest: Optional[Dict[str, Any]] = None) -> WorkCell:
        """Return the best file-scoped WorkCell for a seed objective."""
        manifest = manifest or {}
        workcells = self.populate_from_manifest(manifest)
        objective_lc = (objective or "").lower()

        best_match = None
        best_score = 0
        for workcell in workcells:
            path = workcell.owned_paths[0] if workcell.owned_paths else ""
            path_lc = path.lower().replace("\\", "/")
            name_lc = os.path.basename(path_lc)
            stem_lc = os.path.splitext(name_lc)[0]
            score = 0
            if path_lc and path_lc in objective_lc:
                score = 100
            elif name_lc and name_lc in objective_lc:
                score = 75
            elif stem_lc and re.search(rf"\b{re.escape(stem_lc)}\b", objective_lc):
                score = 40
            if score > best_score:
                best_score = score
                best_match = workcell

        if best_match:
            return best_match

        workcell_id = "workcell_repository"
        existing = self._workcells.get(workcell_id)
        if existing:
            existing.updated_at = _now()
            existing.freshness_state = "fresh" if manifest.get("integrity", {}).get("manifest_hash") else existing.freshness_state
            self._save()
            return existing

        repo_name = os.path.basename(self.repo_path) or "Repository"
        workcell = WorkCell(
            workcell_id=workcell_id,
            name=f"{repo_name} Repository WorkCell",
            purpose="Degraded fallback when no file-scoped WorkCell evidence is available.",
            repo_path=self.repo_path,
            owned_paths=[],
            restricted_paths=[
                ".git/",
                ".srt1/seeds/",
                ".srt1/runtime/",
                "memory/",
                "scia_memory/",
                "scia_security/",
            ],
            freshness_state="fresh" if manifest.get("integrity", {}).get("manifest_hash") else "unknown",
        )
        self._workcells[workcell_id] = workcell
        self._save()
        return workcell

    def activate_execution(
        self,
        queue_seed_id: str,
        objective: str,
        manifest: Optional[Dict[str, Any]] = None,
        srt_anchor_id: Optional[str] = None,
        runtime_port: Optional[int] = None,
        assigned_agent: str = "unassigned",
    ) -> WorkCellExecution:
        if not queue_seed_id:
            raise ValueError("queue_seed_id is required to activate a WorkCell execution")

        workcell = self.infer_workcell(objective=objective, manifest=manifest)
        execution_id = f"wcx_{_safe_slug(queue_seed_id)}"
        manifest_hash = (manifest or {}).get("integrity", {}).get("manifest_hash")
        package_path = os.path.join(self.registry_dir, queue_seed_id)

        execution = self._executions.get(execution_id)
        if execution:
            execution.updated_at = _now()
            execution.srt_anchor_id = srt_anchor_id or execution.srt_anchor_id
            execution.objective = objective or execution.objective
            execution.runtime_port = runtime_port
            execution.manifest_hash = manifest_hash or execution.manifest_hash
        else:
            execution = WorkCellExecution(
                workcell_execution_id=execution_id,
                workcell_id=workcell.workcell_id,
                queue_seed_id=queue_seed_id,
                srt_anchor_id=srt_anchor_id,
                objective=objective,
                runtime_port=runtime_port,
                assigned_agent=assigned_agent,
                manifest_hash=manifest_hash,
                package_path=package_path,
            )
            self._executions[execution_id] = execution

        os.makedirs(package_path, exist_ok=True)
        if not execution.activity_events:
            self._append_activity_event(
                execution,
                event_type="execution.created",
                status="ready",
                actor="srt1",
                message="WorkCell execution package created.",
            )
        self._write_filecells_json(workcell, execution)
        self._write_workcell_md(workcell, execution)
        self._write_runtime_state(workcell, execution)
        execution.package_status = self._build_package_status(execution)
        self._write_runtime_state(workcell, execution)
        self._save()
        return execution

    def get_execution_for_seed(self, queue_seed_id: str) -> Optional[Dict[str, Any]]:
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return None
        data = execution.to_dict()
        data["package_status"] = self._build_package_status(execution)
        data["current_execution_job"] = self._current_execution_job(execution)
        return data

    def start_execution_job(
        self,
        queue_seed_id: str,
        provider: str = "execution_bridge",
        adapter: str = "assistant_adapter",
        cancellable: bool = True,
        hard_cancellable: bool = False,
        runtime_port: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register one assistant/provider execution job for an active WorkCell."""
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {"status": "not_found", "queue_seed_id": queue_seed_id}

        created_at = _now()
        job_id = "wcj_" + hashlib.sha1(
            "|".join([
                execution.workcell_execution_id,
                str(provider or ""),
                str(adapter or ""),
                created_at,
                str(len(execution.execution_jobs)),
            ]).encode("utf-8")
        ).hexdigest()[:12]
        job = {
            "job_id": job_id,
            "queue_seed_id": queue_seed_id,
            "workcell_execution_id": execution.workcell_execution_id,
            "provider": str(provider or "execution_bridge"),
            "adapter": str(adapter or "assistant_adapter"),
            "status": "running",
            "cancellable": bool(cancellable),
            "hard_cancellable": bool(hard_cancellable),
            "stop_requested": False,
            "pause_requested": False,
            "cancel_requested": False,
            "provider_acknowledged": False,
            "runtime_port": runtime_port,
            "started_at": created_at,
            "updated_at": created_at,
            "completed_at": None,
            "metadata": self._sanitize_activity_value(metadata or {}),
        }
        execution.execution_jobs.append(job)
        execution.execution_jobs = execution.execution_jobs[-50:]
        execution.current_execution_job_id = job_id
        execution.status = "running"
        self._append_activity_event(
            execution,
            event_type="execution_job.started",
            status="running",
            actor="execution_bridge",
            message="Assistant execution job registered for WorkCell.",
            metadata={
                "job_id": job_id,
                "provider": job["provider"],
                "adapter": job["adapter"],
                "cancellable": job["cancellable"],
                "hard_cancellable": job["hard_cancellable"],
            },
        )
        self._write_runtime_state(self._workcells[execution.workcell_id], execution)
        self._save()
        return {
            "status": "registered",
            "queue_seed_id": queue_seed_id,
            "job": job,
        }

    def update_execution_job(
        self,
        queue_seed_id: str,
        job_id: Optional[str] = None,
        status: Optional[str] = None,
        provider_acknowledged: Optional[bool] = None,
        result: Optional[Dict[str, Any]] = None,
        error: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update the current assistant/provider job without owning provider internals."""
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {"status": "not_found", "queue_seed_id": queue_seed_id}
        job = self._find_execution_job(execution, job_id)
        if not job:
            return {"status": "not_found", "queue_seed_id": queue_seed_id, "job_id": job_id}

        now = _now()
        if status:
            job["status"] = str(status)
        if provider_acknowledged is not None:
            job["provider_acknowledged"] = bool(provider_acknowledged)
        if result is not None:
            job["result"] = self._sanitize_activity_value(result)
        if error:
            job["error"] = self._sanitize_activity_value(str(error))
        if metadata:
            existing = job.get("metadata") if isinstance(job.get("metadata"), dict) else {}
            existing.update(self._sanitize_activity_value(metadata))
            job["metadata"] = existing
        job["updated_at"] = now
        if job.get("status") in {"dispatched", "failed", "blocked", "completed", "cancelled"}:
            job["completed_at"] = job.get("completed_at") or now
        self._append_activity_event(
            execution,
            event_type="execution_job.updated",
            status=str(job.get("status") or "updated"),
            actor="execution_bridge",
            message=f"Assistant execution job {job.get('status', 'updated')}.",
            metadata={
                "job_id": job.get("job_id"),
                "provider_acknowledged": job.get("provider_acknowledged"),
                "error": job.get("error", ""),
            },
        )
        self._write_runtime_state(self._workcells[execution.workcell_id], execution)
        self._save()
        return {
            "status": "updated",
            "queue_seed_id": queue_seed_id,
            "job": job,
        }

    def acknowledge_execution_job(
        self,
        queue_seed_id: str,
        job_id: Optional[str] = None,
        acknowledgement: str = "acknowledged",
        actor: str = "assistant_runtime",
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record a provider/runtime acknowledgement for the active WorkCell job."""
        allowed = {
            "acknowledged",
            "stopping",
            "stopped",
            "paused",
            "resumed",
            "failed",
            "completed",
        }
        ack = str(acknowledgement or "acknowledged").strip().lower()
        if ack not in allowed:
            return {
                "status": "invalid_acknowledgement",
                "queue_seed_id": queue_seed_id,
                "error": "Supported acknowledgements: acknowledged, stopping, stopped, paused, resumed, failed, completed.",
            }
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {"status": "not_found", "queue_seed_id": queue_seed_id}
        job = self._find_execution_job(execution, job_id)
        if not job:
            return {"status": "not_found", "queue_seed_id": queue_seed_id, "job_id": job_id}

        job["provider_acknowledged"] = True
        job["acknowledgement"] = ack
        job["updated_at"] = _now()
        if ack in {"stopping", "stopped"}:
            job["stop_requested"] = True
        if ack == "paused":
            job["pause_requested"] = True
        if ack == "failed":
            job["status"] = "failed"
            job["completed_at"] = job.get("completed_at") or job["updated_at"]
            execution.status = "returned"
        elif ack == "completed":
            job["status"] = "completed"
            job["completed_at"] = job.get("completed_at") or job["updated_at"]
            job["review_required"] = True
            job["verification_required"] = True
            execution.status = "awaiting_review"
        elif ack == "stopped":
            job["status"] = "stopped"
            job["completed_at"] = job.get("completed_at") or job["updated_at"]
            execution.status = "terminated"
        elif ack in {"stopping", "paused"}:
            job["status"] = ack
            if ack == "paused":
                execution.status = "paused"
        elif ack == "resumed":
            job["status"] = "running"
            execution.status = "running"

        event = self._append_activity_event(
            execution,
            event_type="execution_job.acknowledged",
            status=ack,
            actor=actor,
            message=message or f"Assistant runtime acknowledged job as {ack}.",
            metadata={
                "job_id": job.get("job_id"),
                "acknowledgement": ack,
                "job_status": job.get("status"),
                "metadata": self._sanitize_activity_value(metadata or {}),
            },
        )
        self._write_runtime_state(self._workcells[execution.workcell_id], execution)
        self._save()
        return {
            "status": "acknowledged",
            "acknowledgement": ack,
            "queue_seed_id": queue_seed_id,
            "job": job,
            "execution": execution.to_dict(),
            "event": event,
        }

    def record_execution_event(
        self,
        queue_seed_id: str,
        event_type: str,
        status: str,
        actor: str = "srt1",
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        execution_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Append observable activity without granting execution authority."""
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {
                "status": "not_found",
                "queue_seed_id": queue_seed_id,
                "error": "WorkCell execution not found",
            }

        event = self._append_activity_event(
            execution,
            event_type=event_type,
            status=status,
            actor=actor,
            message=message,
            metadata=metadata,
        )
        if execution_status:
            execution.status = str(execution_status)
        self._write_runtime_state(self._workcells[execution.workcell_id], execution)
        self._save()
        return {
            "status": "recorded",
            "queue_seed_id": queue_seed_id,
            "workcell_execution_id": execution.workcell_execution_id,
            "event": event,
        }

    def get_execution_activity(
        self,
        queue_seed_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Return a bounded page from the complete append-only activity log."""
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {
                "status": "not_found",
                "queue_seed_id": queue_seed_id,
                "events": [],
            }

        limit = max(1, min(int(limit or 100), 200))
        offset = max(0, int(offset or 0))
        log_path = self._activity_log_path(execution)
        events: List[Dict[str, Any]] = []
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as activity_file:
                for line in activity_file:
                    try:
                        events.append(json.loads(line))
                    except (TypeError, ValueError):
                        continue
        else:
            events = list(execution.activity_events)

        total = len(events)
        end = max(0, total - offset)
        start = max(0, end - limit)
        page = list(reversed(events[start:end]))
        return {
            "status": "ok",
            "queue_seed_id": queue_seed_id,
            "workcell_execution_id": execution.workcell_execution_id,
            "events": page,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": start > 0,
            "next_offset": offset + len(page) if start > 0 else None,
        }

    def control_execution(
        self,
        queue_seed_id: str,
        action: str,
        actor: str = "human",
        reason: str = "",
    ) -> Dict[str, Any]:
        """Apply an explicit human/runtime state transition to one WorkCell."""
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {"status": "not_found", "queue_seed_id": queue_seed_id}

        action = str(action or "").strip().lower()
        transitions = {
            "pause": ({"ready", "running", "dispatched"}, "pause_requested"),
            "resume": ({"paused", "pause_requested"}, "running"),
            "stop": ({"ready", "running", "dispatched", "paused", "pause_requested", "returned"}, "stop_requested"),
            "cancel": (
                {"ready", "running", "dispatched", "paused", "pause_requested", "stop_requested", "returned"},
                "cancelled",
            ),
            "reject": ({"ready", "running", "dispatched", "paused", "pause_requested", "awaiting_review"}, "returned"),
        }
        if action == "approve":
            if execution.verification_state != "verified":
                return {
                    "status": "blocked",
                    "queue_seed_id": queue_seed_id,
                    "error": "Approval requires verified WorkCell evidence.",
                }
            allowed, target = ({"awaiting_review", "ready", "running"}, "completed")
        elif action in transitions:
            allowed, target = transitions[action]
        else:
            return {
                "status": "invalid_action",
                "queue_seed_id": queue_seed_id,
                "error": "Supported actions: pause, resume, stop, cancel, approve, reject.",
            }

        previous_status = execution.status
        if execution.status not in allowed:
            return {
                "status": "blocked",
                "queue_seed_id": queue_seed_id,
                "error": f"Cannot {action} a WorkCell in {execution.status} state.",
            }

        execution.status = target
        current_job = self._current_execution_job(execution)
        if current_job and action in {"pause", "stop", "cancel"}:
            current_job[f"{action}_requested"] = True
            current_job["provider_acknowledged"] = False
            current_job["status"] = f"{action}_requested"
            current_job["updated_at"] = _now()
        decision_messages = {
            "approve": "Human accepted verified WorkCell completion.",
            "reject": "Human returned WorkCell for revision.",
        }
        event = self._append_activity_event(
            execution,
            event_type=f"execution.{action}",
            status=target,
            actor=actor,
            message=reason or decision_messages.get(action) or f"WorkCell execution {action} requested.",
            metadata={
                "requested_action": action,
                "previous_status": previous_status,
                "requires_runtime_ack": action in {"pause", "stop", "cancel"},
                "execution_job_id": current_job.get("job_id") if current_job else None,
                "hard_cancellable": current_job.get("hard_cancellable") if current_job else False,
                "verification_state": execution.verification_state,
                "human_decision": action if action in {"approve", "reject"} else None,
            },
        )
        self._write_runtime_state(self._workcells[execution.workcell_id], execution)
        self._save()
        return {
            "status": target,
            "queue_seed_id": queue_seed_id,
            "execution": execution.to_dict(),
            "event": event,
        }

    def record_verification(
        self,
        queue_seed_id: str,
        verified: bool,
        actor: str = "verification",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {"status": "not_found", "queue_seed_id": queue_seed_id}
        execution.verification_state = "verified" if verified else "failed"
        execution.trust_state["verification"] = execution.verification_state
        execution.status = "awaiting_review" if verified else "returned"
        return self.record_execution_event(
            queue_seed_id=queue_seed_id,
            event_type="verification.completed",
            status=execution.verification_state,
            actor=actor,
            message="Verification passed." if verified else "Verification failed.",
            metadata=details,
        )

    def validate_execution_writes(
        self,
        queue_seed_id: str,
        proposed_paths: List[str],
        actor: str = "assistant_runtime",
    ) -> Dict[str, Any]:
        """Fail closed unless every proposed write stays inside the WorkCell scope."""
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {
                "status": "not_found",
                "queue_seed_id": queue_seed_id,
                "allowed": False,
                "approved_paths": [],
                "violations": ["WorkCell execution not found"],
            }
        workcell = self._workcells.get(execution.workcell_id)
        if not workcell:
            return {
                "status": "not_found",
                "queue_seed_id": queue_seed_id,
                "allowed": False,
                "approved_paths": [],
                "violations": ["Persistent WorkCell not found"],
            }

        repo_root = self.repo_path
        allowed_writes = [
            self._resolve_repo_path(path)
            for path in workcell.owned_paths
            if path
        ]
        forbidden_paths = [
            self._resolve_repo_path(path)
            for path in workcell.restricted_paths
            if path
        ]
        manifest = FileCellManifest.generate(
            task_intent=execution.objective,
            allowed_reads=allowed_writes,
            allowed_writes=allowed_writes,
            forbidden_paths=forbidden_paths,
        )
        guard = FileCellGuard()
        approved_paths: List[str] = []
        violations: List[Dict[str, Any]] = []

        for path in proposed_paths or []:
            absolute_path = self._resolve_repo_path(path)
            try:
                guard.validate_write(absolute_path, manifest)
                approved_paths.append(os.path.relpath(absolute_path, repo_root).replace("\\", "/"))
            except FileCellBoundaryViolation as exc:
                violations.append({
                    "path": str(path),
                    "absolute_path": absolute_path,
                    "reason": str(exc),
                })

        allowed = not violations and bool(proposed_paths)
        status = "allowed" if allowed else "blocked"
        if violations:
            self._append_activity_event(
                execution,
                event_type="boundary.write_blocked",
                status="blocked",
                actor=actor,
                message="Proposed assistant write escaped the WorkCell boundary.",
                metadata={"violations": violations},
            )
            execution.status = "returned"
            self._write_runtime_state(workcell, execution)
            self._save()

        return {
            "status": status,
            "queue_seed_id": queue_seed_id,
            "workcell_execution_id": execution.workcell_execution_id,
            "allowed": allowed,
            "approved_paths": approved_paths,
            "violations": violations,
        }

    def _activity_log_path(self, execution: WorkCellExecution) -> str:
        package_path = os.path.realpath(
            execution.package_path or os.path.join(self.registry_dir, execution.queue_seed_id)
        )
        registry_root = os.path.realpath(self.registry_dir)
        if package_path != registry_root and not package_path.startswith(registry_root + os.sep):
            raise ValueError("Activity log path escaped WorkCell registry boundary")
        os.makedirs(package_path, exist_ok=True)
        return os.path.join(package_path, "activity.jsonl")

    def _resolve_repo_path(self, path: str) -> str:
        candidate = str(path or "")
        if os.path.isabs(candidate):
            resolved = os.path.realpath(candidate)
        else:
            resolved = os.path.realpath(os.path.join(self.repo_path, candidate))
        return resolved

    def _sanitize_activity_value(self, value: Any, key: str = "", depth: int = 0) -> Any:
        sensitive = (
            "api_key", "apikey", "authorization", "cookie", "password",
            "private_key", "secret", "session_token", "access_token", "refresh_token",
        )
        if any(marker in key.lower() for marker in sensitive):
            return "[REDACTED]"
        if depth >= 5:
            return "[TRUNCATED]"
        if isinstance(value, dict):
            return {
                str(item_key)[:120]: self._sanitize_activity_value(item_value, str(item_key), depth + 1)
                for item_key, item_value in list(value.items())[:100]
            }
        if isinstance(value, (list, tuple)):
            return [self._sanitize_activity_value(item, key, depth + 1) for item in list(value)[:100]]
        if isinstance(value, str):
            text = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1[REDACTED]", value)
            return text[:4000]
        if value is None or isinstance(value, (bool, int, float)):
            return value
        return str(value)[:1000]

    def _current_execution_job(self, execution: WorkCellExecution) -> Optional[Dict[str, Any]]:
        return self._find_execution_job(execution, execution.current_execution_job_id)

    def _find_execution_job(
        self,
        execution: WorkCellExecution,
        job_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        jobs = execution.execution_jobs or []
        if not jobs:
            return None
        target = job_id or execution.current_execution_job_id
        if target:
            for job in reversed(jobs):
                if job.get("job_id") == target:
                    return job
        return jobs[-1]

    def _append_activity_event(
        self,
        execution: WorkCellExecution,
        event_type: str,
        status: str,
        actor: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not event_type or not status:
            raise ValueError("event_type and status are required")

        created_at = _now()
        event_key = "|".join([
            execution.workcell_execution_id,
            str(event_type),
            str(actor or "unknown"),
            created_at,
            str(len(execution.activity_events)),
        ])
        event = {
            "event_id": f"wce_{hashlib.sha1(event_key.encode('utf-8')).hexdigest()[:12]}",
            "event_type": str(event_type),
            "status": str(status),
            "actor": self._sanitize_activity_value(str(actor or "unknown")),
            "message": self._sanitize_activity_value(str(message or "")),
            "metadata": self._sanitize_activity_value(metadata or {}),
            "created_at": created_at,
        }
        log_path = self._activity_log_path(execution)
        with open(log_path, "a", encoding="utf-8") as activity_file:
            activity_file.write(json.dumps(event, sort_keys=True) + "\n")
        execution.activity_events.append(event)
        execution.activity_events = execution.activity_events[-200:]
        execution.activity_event_count += 1
        execution.updated_at = event["created_at"]
        return event

    def repair_execution_package(self, queue_seed_id: str) -> Dict[str, Any]:
        """Regenerate local WorkCell package files for an existing execution."""
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {
                "status": "not_found",
                "queue_seed_id": queue_seed_id,
                "error": "WorkCell execution not found",
            }

        workcell = self._workcells.get(execution.workcell_id)
        if not workcell:
            return {
                "status": "not_found",
                "queue_seed_id": queue_seed_id,
                "workcell_execution_id": execution.workcell_execution_id,
                "error": "Persistent WorkCell not found",
            }

        package_path = execution.package_path or os.path.join(self.registry_dir, queue_seed_id)
        execution.package_path = package_path
        execution.updated_at = _now()

        before = self._build_package_status(execution)
        os.makedirs(package_path, exist_ok=True)
        self._write_filecells_json(workcell, execution)
        self._write_workcell_md(workcell, execution)
        self._write_runtime_state(workcell, execution)
        execution.package_status = self._build_package_status(execution)
        self._append_activity_event(
            execution,
            event_type="package.repaired",
            status="ready" if execution.package_status.get("assistant_ready") else "degraded",
            actor="srt1",
            message="WorkCell execution package regenerated.",
        )
        self._write_runtime_state(workcell, execution)
        self._save()

        return {
            "status": "repaired" if execution.package_status.get("assistant_ready") else "degraded",
            "queue_seed_id": queue_seed_id,
            "workcell_execution_id": execution.workcell_execution_id,
            "workcell_id": execution.workcell_id,
            "package_path": package_path,
            "before": before,
            "after": execution.package_status,
            "execution": execution.to_dict(),
        }

    def read_workcell_md(self, queue_seed_id: str) -> Dict[str, Any]:
        """Read the generated workcell.md instructions for an execution package."""
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        if not execution:
            return {
                "status": "not_found",
                "queue_seed_id": queue_seed_id,
                "error": "WorkCell execution not found",
            }

        package_status = self._build_package_status(execution)
        path = package_status.get("workcell_md_path")
        if not path or not package_status.get("workcell_md_exists"):
            return {
                "status": "missing",
                "queue_seed_id": queue_seed_id,
                "workcell_execution_id": execution.workcell_execution_id,
                "package_status": package_status,
                "error": "workcell.md is missing",
            }

        package_root = os.path.realpath(execution.package_path or self.registry_dir)
        target = os.path.realpath(path)
        if not target.startswith(package_root + os.sep):
            return {
                "status": "blocked",
                "queue_seed_id": queue_seed_id,
                "workcell_execution_id": execution.workcell_execution_id,
                "error": "Package preview path escaped WorkCell package boundary",
            }

        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "status": "ok",
            "queue_seed_id": queue_seed_id,
            "workcell_execution_id": execution.workcell_execution_id,
            "workcell_id": execution.workcell_id,
            "path": target,
            "content": content,
            "size": len(content),
            "package_status": package_status,
        }

    def summary(self) -> Dict[str, Any]:
        execution_dicts = []
        for execution in self._executions.values():
            item = execution.to_dict()
            item["package_status"] = self._build_package_status(execution)
            execution_dicts.append(item)
        executions = sorted(
            execution_dicts,
            key=lambda ex: ex.get("updated_at") or ex.get("created_at") or "",
            reverse=True,
        )
        return {
            "registry_path": self.registry_file,
            "workcell_count": len(self._workcells),
            "execution_count": len(self._executions),
            "workcells": [wc.to_dict() for wc in self._workcells.values()],
            "executions": executions,
            "active_executions": [
                ex for ex in executions
                if ex.get("status") not in {"completed", "terminated"}
            ],
        }

    def _build_package_status(self, execution: WorkCellExecution) -> Dict[str, Any]:
        package_path = execution.package_path
        if not package_path:
            return {
                "assistant_ready": False,
                "package_exists": False,
                "missing_files": ["package_path"],
            }

        expected = {
            "workcell_md": os.path.join(package_path, "workcell.md"),
            "filecells_json": os.path.join(package_path, "filecells.json"),
            "runtime_state_json": os.path.join(package_path, "runtime_state.json"),
        }
        exists = {name: os.path.exists(path) for name, path in expected.items()}
        missing = [name for name, present in exists.items() if not present]
        return {
            "assistant_ready": os.path.isdir(package_path) and not missing,
            "package_exists": os.path.isdir(package_path),
            "package_path": package_path,
            "workcell_md_exists": exists["workcell_md"],
            "workcell_md_path": expected["workcell_md"],
            "filecells_json_exists": exists["filecells_json"],
            "filecells_json_path": expected["filecells_json"],
            "runtime_state_json_exists": exists["runtime_state_json"],
            "runtime_state_json_path": expected["runtime_state_json"],
            "missing_files": missing,
        }

    def _write_runtime_state(self, workcell: WorkCell, execution: WorkCellExecution) -> None:
        if not execution.package_path:
            return
        state_path = os.path.join(execution.package_path, "runtime_state.json")
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({
                "workcell": workcell.to_dict(),
                "execution": execution.to_dict(),
                "filecells": [workcell.filecell_summary] if workcell.filecell_summary else [],
            }, f, indent=2, sort_keys=True)

    def _write_filecells_json(self, workcell: WorkCell, execution: WorkCellExecution) -> None:
        if not execution.package_path:
            return
        path = os.path.join(execution.package_path, "filecells.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "queue_seed_id": execution.queue_seed_id,
                "workcell_id": workcell.workcell_id,
                "filecells": [workcell.filecell_summary] if workcell.filecell_summary else [],
            }, f, indent=2, sort_keys=True)

    def _write_workcell_md(self, workcell: WorkCell, execution: WorkCellExecution) -> None:
        if not execution.package_path:
            return
        path = os.path.join(execution.package_path, "workcell.md")
        allowed_paths = workcell.owned_paths[:20] or ["Not available yet; use manifest evidence before expanding scope."]
        restricted_paths = workcell.restricted_paths or ["Not available"]
        filecell = workcell.filecell_summary or {}
        roles = ", ".join(filecell.get("architectural_roles", {}).keys()) or "unknown"
        risks = ", ".join(filecell.get("risk_tags", {}).keys()) or "unknown"
        lines = [
            f"# {workcell.name}",
            "",
            "## Active Objective",
            execution.objective or "Not specified",
            "",
            "## Identity",
            f"- workcell_id: {workcell.workcell_id}",
            f"- workcell_execution_id: {execution.workcell_execution_id}",
            f"- queue_seed_id: {execution.queue_seed_id}",
            f"- srt_anchor_id: {execution.srt_anchor_id or 'none'}",
            f"- runtime_port: {execution.runtime_port or 'repository-runtime'}",
            f"- assigned_agent: {execution.assigned_agent}",
            "",
            "## Operating Rule",
            "Begin inside this WorkCell package. Do not broaden context because files are nearby.",
            "Broaden scope only when dependency evidence, verification needs, or human approval requires it.",
            "",
            "## Attached FileCell",
            f"- filecell_id: {filecell.get('filecell_id', 'unknown')}",
            f"- path: {filecell.get('path', 'unknown')}",
            f"- parser: {filecell.get('parser', 'unknown')}",
            f"- symbols: {filecell.get('symbol_count', 0)}",
            f"- roles: {roles}",
            f"- risks: {risks}",
            "",
            "## Allowed / Relevant Paths",
            *[f"- {item}" for item in allowed_paths],
            "",
            "## Restricted Paths",
            *[f"- {item}" for item in restricted_paths],
            "",
            "## Verification Requirements",
            *[f"- {item}" for item in workcell.default_verification_rules],
            "",
            "## Trust And Freshness",
            f"- manifest_hash: {execution.manifest_hash or 'unknown'}",
            f"- signature: {execution.trust_state.get('signature', 'unsigned')}",
            f"- verification: {execution.verification_state}",
            f"- lineage: {execution.trust_state.get('lineage', 'missing')}",
            f"- filecell_freshness: {workcell.freshness_state}",
            "",
            "## Completion Requirements",
            "- Stay inside the WorkCell boundary.",
            "- Preserve related contracts.",
            "- Run relevant tests or mark verification as degraded.",
            "- Return work for human review before final acceptance.",
            "",
        ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
