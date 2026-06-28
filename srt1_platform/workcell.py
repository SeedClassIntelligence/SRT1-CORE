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
        self._write_filecells_json(workcell, execution)
        self._write_workcell_md(workcell, execution)
        self._write_runtime_state(workcell, execution)
        self._save()
        return execution

    def get_execution_for_seed(self, queue_seed_id: str) -> Optional[Dict[str, Any]]:
        execution = self._executions.get(f"wcx_{_safe_slug(queue_seed_id)}")
        return execution.to_dict() if execution else None

    def summary(self) -> Dict[str, Any]:
        executions = sorted(
            [ex.to_dict() for ex in self._executions.values()],
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
