#!/usr/bin/env python3
"""
SRT-1 Self-Healing Engine - Governed Codebase Remediation
FILE: srt1_self_heal.py
SRT-1 TAG: SELF_HEALING :: GOVERNED_REMEDIATION
SCIA VERSION: 4.0.0
PURPOSE:
    Consumes the Code Manifest's curation report and verification results,
    then acts on the recommendations within strict governance boundaries.
    The indexer DETECTS. This module REMEDIATES.
WHAT IT CAN FIX (governed actions):
    1. DUPLICATE FILES     - Archive duplicates to .srt1/archive/, keep canonical
    2. STALE MANIFEST      - Re-index when file hashes don't match
    3. BROKEN TRUST CHAIN  - Re-index to rebuild the chain from scratch
    4. MISSING DOCSTRINGS  - Inject stub docstrings into undocumented functions
    5. IMPORT CONSOLIDATION - Generate a report of where duplicates are imported
WHAT IT WILL NOT DO (hard boundaries):
    - Never delete source files (archives only, with full rollback)
    - Never modify core SCIA IP (srt.py)
    - Never modify files tagged AUTH_SENSITIVE without explicit --force flag
    - Never act without producing an audit trail
    - Never run without a valid manifest to work from
SAFETY MODEL:
    - Every action is logged to .srt1/heal/heal_log.json
    - Every file modification creates a backup in .srt1/heal/backups/
    - --dry-run mode shows what WOULD happen without touching anything
    - --force required for high-risk actions
    - Full rollback via: python srt1_self_heal.py rollback <session_id>
Author : William Darnell Jernigan IV (Architect)
License: Apache License 2.0
"""
import os
import sys
import json
import shutil
import hashlib
import argparse
import ast
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
# Core SCIA IP imports
try:
    from srt1_code_indexer.srt import SRT
except ImportError:
    try:
        from srt import SRT
    except ImportError:
        sys.exit("[FATAL] Cannot import SRT.")

# ==========================================================================
# CONSTANTS
# ==========================================================================
PROTECTED_FILES = {"srt.py"}
HEAL_DIR = ".srt1/heal"
ARCHIVE_DIR = ".srt1/archive"
BACKUP_DIR = ".srt1/heal/backups"
# ==========================================================================
# HEAL ACTION TYPES
# ==========================================================================
class HealAction:
    """A single remediation action with full audit metadata."""
    def __init__(self, action_type: str, target: str, description: str,
                 risk_level: str = "low"):
        self.action_type = action_type
        self.target = target
        self.description = description
        self.risk_level = risk_level  # low, medium, high
        self.status = "pending"       # pending, executed, skipped, failed, rolled_back
        self.timestamp: Optional[str] = None
        self.backup_path: Optional[str] = None
        self.details: Dict[str, Any] = {}
        self.error: Optional[str] = None
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "target": self.target,
            "description": self.description,
            "risk_level": self.risk_level,
            "status": self.status,
            "timestamp": self.timestamp,
            "backup_path": self.backup_path,
            "details": self.details,
            "error": self.error,
        }
# ==========================================================================
# SELF-HEALING ENGINE
# ==========================================================================
class SCIARemediationEngine:
    """
    Governed self-healing engine for the SRT-1 codebase.
    Reads the manifest, identifies actionable issues, plans remediation
    actions, executes them within governance boundaries, and produces
    a complete audit trail.
    """
    def __init__(self, repo_path: str, manifest_path: Optional[str] = None,
                 dry_run: bool = False, force: bool = False):
        self.repo_path = os.path.abspath(repo_path)
        self.manifest_path = manifest_path or os.path.join(
            self.repo_path, "srt1_code_manifest.json"
        )
        self.dry_run = dry_run
        self.force = force
        self.manifest: Dict[str, Any] = {}
        self.actions: List[HealAction] = []
        self.session_id = (
            f"heal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
            f"{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
        )
        self.srt_tool = SRT()
        # Ensure directories
        for d in [HEAL_DIR, ARCHIVE_DIR, BACKUP_DIR]:
            full = os.path.join(self.repo_path, d)
            os.makedirs(full, exist_ok=True)
        # Load manifest
        self._load_manifest()
    def _load_manifest(self) -> None:
        """Load the Code Manifest."""
        if not os.path.isfile(self.manifest_path):
            raise FileNotFoundError(
                f"No manifest found at {self.manifest_path}. "
                f"Run: python srt1_code_indexer.py --repo_path {self.repo_path}"
            )
        with open(self.manifest_path, "r", encoding="utf-8") as fh:
            self.manifest = json.load(fh)
    # ------------------------------------------------------------------
    # DIAGNOSIS
    # ------------------------------------------------------------------
    def diagnose(self) -> Dict[str, Any]:
        """
        Analyze the manifest and verification results to build an action plan.
        Returns a diagnosis report with all planned actions.
        """
        print()
        print("--- [SRT-1 Self-Healing] Diagnosing ---")
        print(f"    Session: {self.session_id}")
        print(f"    Mode:    {'DRY RUN' if self.dry_run else 'LIVE'}")
        print()
        self._diagnose_duplicate_files()
        self._diagnose_stale_files()
        self._diagnose_trust_chain()
        self._diagnose_missing_docstrings()
        self._diagnose_functional_overlaps()
        # Summary
        by_type: Dict[str, int] = {}
        by_risk: Dict[str, int] = {}
        for a in self.actions:
            by_type[a.action_type] = by_type.get(a.action_type, 0) + 1
            by_risk[a.risk_level] = by_risk.get(a.risk_level, 0) + 1
        report = {
            "session_id": self.session_id,
            "diagnosed_at": datetime.now().isoformat(),
            "manifest_path": self.manifest_path,
            "total_actions": len(self.actions),
            "by_type": by_type,
            "by_risk": by_risk,
            "actions": [a.to_dict() for a in self.actions],
            "dry_run": self.dry_run,
        }
        print(f"  Diagnosis complete: {len(self.actions)} action(s) planned.")
        for t, c in by_type.items():
            print(f"    {t}: {c}")
        if by_risk.get("high", 0) > 0:
            print(f"    HIGH RISK: {by_risk['high']} (requires --force)")
        print()
        return report
    def _diagnose_duplicate_files(self) -> None:
        """Plan archival of duplicate files."""
        dups = self.manifest.get("curation_report", {}).get("duplicate_files", [])
        for dup in dups:
            canonical = min(dup["files"], key=len)
            for f in dup["files"]:
                if f == canonical:
                    continue
                basename = os.path.basename(f)
                if basename in PROTECTED_FILES:
                    continue
                self.actions.append(HealAction(
                    action_type="ARCHIVE_DUPLICATE",
                    target=f,
                    description=(
                        f"Archive duplicate '{f}' (identical to '{canonical}')"
                    ),
                    risk_level="medium",
                ))
    def _diagnose_stale_files(self) -> None:
        """Check for files that changed since the manifest was generated."""
        for entry in self.manifest.get("file_manifest", []):
            fp = entry.get("file_path", "")
            if not fp:
                continue
            if os.path.basename(fp) == "srt1_code_manifest.json":
                continue
            full = os.path.join(self.repo_path, fp)
            if not os.path.exists(full):
                self.actions.append(HealAction(
                    action_type="FLAG_MISSING_FILE",
                    target=fp,
                    description=f"File '{fp}' is in manifest but missing from disk.",
                    risk_level="low",
                ))
                continue
            recorded_hash = entry.get("content_hash", "")
            if not recorded_hash:
                continue
            try:
                with open(full, "rb") as fh:
                    current_hash = hashlib.sha256(fh.read()).hexdigest()
                if current_hash != recorded_hash:
                    self.actions.append(HealAction(
                        action_type="REINDEX_STALE",
                        target=fp,
                        description=(
                            f"File '{fp}' has changed since last index. "
                            f"Manifest is stale."
                        ),
                        risk_level="low",
                    ))
            except OSError:
                pass
    def _diagnose_trust_chain(self) -> None:
        """
        Check trust chain integrity.

        The indexer (v4.0) writes trust_chain as a flat list of link dicts,
        each containing: stage, stage_hash, prior_hash, chained.
        Index 0 is the genesis link (prior_hash == None).
        """
        chain = self.manifest.get("trust_chain", [])

        # Pre-v4.0 manifest: no chain at all
        if not chain:
            self.actions.append(HealAction(
                action_type="REBUILD_TRUST_CHAIN",
                target="manifest",
                description="No trust chain found (pre-v4.0 manifest). Re-index required.",
                risk_level="low",
            ))
            return

        # Handle legacy dict format {"genesis_hash": ..., "links": [...]}
        if isinstance(chain, dict):
            links = chain.get("links", [])
            genesis = chain.get("genesis_hash", "")
            expected_genesis = hashlib.sha256(b"SRT-1 SCIA Trust Chain v4.0 genesis").hexdigest()
            if genesis != expected_genesis:
                self.actions.append(HealAction(
                    action_type="REBUILD_TRUST_CHAIN",
                    target="manifest",
                    description="Genesis hash mismatch (legacy format). Re-index required.",
                    risk_level="high",
                ))
                return
            prior = expected_genesis
            for i, link in enumerate(links):
                if link.get("prior_hash") != prior:
                    self.actions.append(HealAction(
                        action_type="REBUILD_TRUST_CHAIN",
                        target=f"chain_link_{i}_{link.get('stage', '?')}",
                        description=(
                            f"Trust chain broken at stage '{link.get('stage')}' "
                            f"(link {i}). Re-index required."
                        ),
                        risk_level="high",
                    ))
                    return
                prior = link.get("stage_hash", "")
            return

        # Current flat-list format (v4.0)
        # chain[0] is genesis, subsequent links must chain correctly
        for i in range(1, len(chain)):
            link = chain[i]
            prev = chain[i - 1]
            if link.get("prior_hash") != prev.get("stage_hash"):
                self.actions.append(HealAction(
                    action_type="REBUILD_TRUST_CHAIN",
                    target=f"chain_link_{i}_{link.get('stage', '?')}",
                    description=(
                        f"Trust chain broken at stage '{link.get('stage')}' "
                        f"(link {i}): prior_hash mismatch. Re-index required."
                    ),
                    risk_level="high",
                ))
                return

    def _diagnose_missing_docstrings(self) -> None:
        """
        Find public functions without docstrings.

        Handles both manifest layouts:
          - dict keyed by file path: {file_path: [symbol, ...]}
          - flat list of symbol dicts with a "file" key
        """
        symbol_table = self.manifest.get("symbol_table", {})

        # Normalise to iterable of (file_path, symbol_list) pairs
        if isinstance(symbol_table, dict):
            items = symbol_table.items()
        else:
            # Flat list — group by file
            grouped: Dict[str, List] = {}
            for sym in symbol_table:
                grouped.setdefault(sym.get("file", ""), []).append(sym)
            items = grouped.items()

        for fp, symbols in items:
            if os.path.basename(fp) in PROTECTED_FILES:
                continue
            for sym in symbols:
                if sym.get("type") not in ("function", "method", None):
                    # Skip classes and non-callables
                    if sym.get("type") == "class":
                        continue
                if sym.get("name", "").startswith("_"):
                    continue  # Skip private/dunder
                ds = sym.get("docstring_first_line", "") or sym.get("docstring", "")
                if ds and ds != "No docstring provided.":
                    continue
                risk = "low"
                reflection = sym.get("reflection", {})
                risk_tags = reflection.get("risk_profile", [])
                if any(t in risk_tags for t in (
                    "AUTH_SENSITIVE", "WRITES_TO_DB", "DYNAMIC_EXECUTION"
                )):
                    risk = "high"
                self.actions.append(HealAction(
                    action_type="ADD_STUB_DOCSTRING",
                    target=f"{fp}::{sym['name']}",
                    description=(
                        f"Public function '{sym['name']}' in {fp} "
                        f"has no docstring."
                    ),
                    risk_level=risk,
                ))

    def _diagnose_functional_overlaps(self) -> None:
        """
        Flag functional overlaps that need consolidation.

        Handles both manifest layouts:
          - list of {instances: [{function, file, line}, ...]}
          - list of {name, locations: [...]}  (older format)
          - list of plain strings (function names only)
        """
        overlaps = self.manifest.get("curation_report", {}).get(
            "functional_overlaps", []
        )
        for overlap in overlaps:
            if isinstance(overlap, str):
                # Plain function name string — minimal report
                self.actions.append(HealAction(
                    action_type="CONSOLIDATION_REPORT",
                    target=overlap,
                    description=f"Function '{overlap}' flagged as duplicate across files.",
                    risk_level="medium",
                ))
                continue

            # Dict with instances list
            instances = overlap.get("instances", [])
            func_name = overlap.get("name", "?")
            if instances:
                func_name = instances[0].get("function", func_name)
                if len(instances) < 2:
                    continue
                locations = [
                    f"{i.get('file', '?')}:{i.get('line', '?')}"
                    for i in instances
                ]
            else:
                # Fallback: locations key
                locations = overlap.get("locations", [])
                if len(locations) < 2:
                    continue

            self.actions.append(HealAction(
                action_type="CONSOLIDATION_REPORT",
                target=func_name,
                description=(
                    f"Function '{func_name}' exists in {len(locations)} locations: "
                    f"{', '.join(str(l) for l in locations[:5])}"
                    f"{'...' if len(locations) > 5 else ''}"
                ),
                risk_level="medium",
            ))

    # ------------------------------------------------------------------
    # EXECUTION
    # ------------------------------------------------------------------
    def heal(self) -> Dict[str, Any]:
        """
        Execute all planned actions within governance boundaries.
        Returns the heal session report.
        """
        if not self.actions:
            self.diagnose()
        print("--- [SRT-1 Self-Healing] Executing ---")
        executed = 0
        skipped = 0
        failed = 0
        needs_reindex = False
        for action in self.actions:
            # Governance gate: high-risk requires --force
            if action.risk_level == "high" and not self.force:
                action.status = "skipped"
                action.details["reason"] = "High-risk action requires --force flag."
                skipped += 1
                print(f"  [SKIP] {action.action_type}: {action.target} (requires --force)")
                continue
            # Dry run gate
            if self.dry_run:
                action.status = "skipped"
                action.details["reason"] = "Dry run mode."
                skipped += 1
                print(f"  [DRY]  {action.action_type}: {action.target}")
                continue
            # Execute based on type
            try:
                if action.action_type == "ARCHIVE_DUPLICATE":
                    self._execute_archive(action)
                    needs_reindex = True
                elif action.action_type == "REINDEX_STALE":
                    needs_reindex = True
                    action.status = "executed"
                    action.timestamp = datetime.now().isoformat()
                elif action.action_type == "REBUILD_TRUST_CHAIN":
                    needs_reindex = True
                    action.status = "executed"
                    action.timestamp = datetime.now().isoformat()
                elif action.action_type == "ADD_STUB_DOCSTRING":
                    self._execute_add_docstring(action)
                    needs_reindex = True
                elif action.action_type == "CONSOLIDATION_REPORT":
                    action.status = "executed"
                    action.timestamp = datetime.now().isoformat()
                    action.details["note"] = (
                        "Consolidation report generated. Manual review required."
                    )
                elif action.action_type == "FLAG_MISSING_FILE":
                    action.status = "executed"
                    action.timestamp = datetime.now().isoformat()
                    action.details["note"] = (
                        "File confirmed missing. No automated action taken."
                    )
                else:
                    action.status = "skipped"
                    action.details["reason"] = f"Unknown action type: {action.action_type}"
                    skipped += 1
                    continue
                if action.status == "executed":
                    executed += 1
                    print(f"  [DONE] {action.action_type}: {action.target}")
            except Exception as exc:
                action.status = "failed"
                action.error = str(exc)
                action.timestamp = datetime.now().isoformat()
                failed += 1
                print(f"  [FAIL] {action.action_type}: {action.target} ({exc})")
        # Re-index if anything changed
        if needs_reindex and not self.dry_run:
            print()
            print("  Re-indexing to rebuild manifest and trust chain...")
            self._reindex()
        # Build session report
        report = self._build_report(executed, skipped, failed)
        # Save audit log
        self._save_audit_log(report)
        print()
        print(f"--- [SRT-1 Self-Healing] Complete ---")
        print(f"    Executed: {executed}  Skipped: {skipped}  Failed: {failed}")
        if needs_reindex and not self.dry_run:
            print(f"    Manifest re-indexed and trust chain rebuilt.")
        print(f"    Audit log: {os.path.join(self.repo_path, HEAL_DIR, 'heal_log.json')}")
        print()
        return report
    def _execute_archive(self, action: HealAction) -> None:
        """Archive a duplicate file to .srt1/archive/."""
        src = os.path.join(self.repo_path, action.target)
        if not os.path.exists(src):
            action.status = "skipped"
            action.details["reason"] = "File does not exist."
            return
        # Create backup first
        backup_name = (
            action.target.replace(os.sep, "_").replace("/", "_")
            + f"_{self.session_id}"
        )
        backup_path = os.path.join(self.repo_path, BACKUP_DIR, backup_name)
        shutil.copy2(src, backup_path)
        action.backup_path = backup_path
        # Move to archive (handle name collision)
        archive_dest = os.path.join(
            self.repo_path, ARCHIVE_DIR, os.path.basename(src)
        )
        if os.path.exists(archive_dest):
            base, ext = os.path.splitext(os.path.basename(src))
            archive_dest = os.path.join(
                self.repo_path, ARCHIVE_DIR,
                f"{base}_{self.session_id[:12]}{ext}"
            )
        shutil.move(src, archive_dest)
        action.status = "executed"
        action.timestamp = datetime.now().isoformat()
        action.details["archived_to"] = archive_dest
        action.details["backup_at"] = backup_path
        self.srt_tool.add_reflection(
            reflection_type="self_heal",
            content=json.dumps({
                "action": "ARCHIVE_DUPLICATE",
                "file": action.target,
                "archived_to": archive_dest,
            }),
            metadata={"session": self.session_id},
        )
    def _execute_add_docstring(self, action: HealAction) -> None:
        """Add a stub docstring to an undocumented public function."""
        parts = action.target.split("::")
        if len(parts) != 2:
            action.status = "failed"
            action.error = f"Invalid target format: {action.target}"
            return
        file_path, func_name = parts
        full_path = os.path.join(self.repo_path, file_path)
        if not os.path.exists(full_path):
            action.status = "skipped"
            action.details["reason"] = "File does not exist."
            return
        if os.path.basename(file_path) in PROTECTED_FILES:
            action.status = "skipped"
            action.details["reason"] = "Protected file."
            return
        # Read and parse
        with open(full_path, "r", encoding="utf-8", errors="replace") as fh:
            source = fh.read()
        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError:
            action.status = "failed"
            action.error = "Syntax error in file."
            return
        # Find the function
        target_node = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == func_name:
                    target_node = node
                    break
        if not target_node:
            action.status = "skipped"
            action.details["reason"] = f"Function '{func_name}' not found in AST."
            return
        # Check if it already has a docstring
        if ast.get_docstring(target_node):
            action.status = "skipped"
            action.details["reason"] = "Docstring already exists."
            return
        # Backup first
        backup_name = (
            file_path.replace(os.sep, "_").replace("/", "_")
            + f"_{self.session_id}"
        )
        backup_path = os.path.join(self.repo_path, BACKUP_DIR, backup_name)
        shutil.copy2(full_path, backup_path)
        action.backup_path = backup_path
        # Build the stub docstring from reflection data
        reflection = {}
        symbol_table = self.manifest.get("symbol_table", {})
        sym_list = (
            symbol_table.get(file_path, [])
            if isinstance(symbol_table, dict)
            else [s for s in symbol_table if s.get("file") == file_path]
        )
        for sym in sym_list:
            if sym["name"] == func_name:
                reflection = sym.get("reflection", {})
                break
        role = reflection.get("architectural_role", "GENERAL")
        risk = reflection.get("risk_profile", ["LOW_RISK"])
        params = [
            arg.arg for arg in target_node.args.args
            if arg.arg != "self"
        ]
        # Detect indentation from the function body
        lines = source.splitlines(True)
        body_start = (
            target_node.body[0].lineno
            if target_node.body
            else target_node.lineno + 1
        )
        body_line = lines[body_start - 1] if body_start <= len(lines) else ""
        indent = ""
        for ch in body_line:
            if ch in (" ", "\t"):
                indent += ch
            else:
                break
        if not indent:
            indent = "    "  # fallback

        stub_lines = [f'{indent}"""TODO: Document this function.']
        if role != "GENERAL":
            stub_lines.append("")
            stub_lines.append(f"{indent}Architectural Role: {role}")
        if risk and risk != ["LOW_RISK"]:
            stub_lines.append(f"{indent}Risk Profile: {', '.join(risk)}")
        if params:
            stub_lines.append("")
            stub_lines.append(f"{indent}Args:")
            for param in params:
                stub_lines.append(f"{indent}    {param}: TODO")
        stub_lines.append(f'{indent}"""')
        stub_docstring = "\n".join(stub_lines) + "\n"

        # Insert the docstring before the first body statement
        insert_idx = body_start - 1  # 0-indexed
        lines.insert(insert_idx, stub_docstring)
        with open(full_path, "w", encoding="utf-8") as fh:
            fh.writelines(lines)
        action.status = "executed"
        action.timestamp = datetime.now().isoformat()
        action.details["stub_added"] = True
        action.details["backup_at"] = backup_path
        self.srt_tool.add_reflection(
            reflection_type="self_heal",
            content=json.dumps({
                "action": "ADD_STUB_DOCSTRING",
                "file": file_path,
                "function": func_name,
                "role": role,
            }),
            metadata={"session": self.session_id},
        )
    def _reindex(self) -> None:
        """Re-run the indexer to rebuild the manifest and trust chain."""
        try:
            try:
                from srt1_code_indexer.indexer import SRT1CodeIndexer
            except ImportError:
                from srt1_code_indexer import SRT1CodeIndexer
            indexer = SRT1CodeIndexer(self.repo_path)
            indexer.index_repository()
        except Exception as exc:
            print(f"    [WARN] Re-index failed: {exc}")
            print(
                f"    Run manually: "
                f"python srt1_code_indexer.py --repo_path {self.repo_path}"
            )
    # ------------------------------------------------------------------
    # ROLLBACK
    # ------------------------------------------------------------------
    def rollback(self, target_session: Optional[str] = None) -> Dict[str, Any]:
        """
        Roll back actions from a healing session by restoring backups.
        If no session specified, rolls back the most recent session.
        """
        log_path = os.path.join(self.repo_path, HEAL_DIR, "heal_log.json")
        if not os.path.exists(log_path):
            return {"error": "No heal log found.", "rolled_back": 0}
        with open(log_path, "r", encoding="utf-8") as fh:
            log = json.load(fh)
        sessions = log.get("sessions", [])
        if not sessions:
            return {"error": "No sessions in heal log.", "rolled_back": 0}
        # Find the target session
        target = None
        if target_session:
            for s in sessions:
                if s["session_id"] == target_session:
                    target = s
                    break
        else:
            target = sessions[-1]
        if not target:
            return {"error": f"Session '{target_session}' not found.", "rolled_back": 0}
        print(f"--- [SRT-1] Rolling back session: {target['session_id']} ---")
        rolled_back = 0
        for action in target.get("actions", []):
            if action["status"] != "executed":
                continue
            backup = action.get("backup_path")
            if not backup or not os.path.exists(backup):
                continue
            target_path = action["target"]
            if action["action_type"] == "ARCHIVE_DUPLICATE":
                dest = os.path.join(self.repo_path, target_path)
                dest_dir = os.path.dirname(dest)
                if dest_dir:
                    os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(backup, dest)
                rolled_back += 1
                print(f"  [RESTORED] {target_path}")
            elif action["action_type"] == "ADD_STUB_DOCSTRING":
                parts = target_path.split("::")
                if parts:
                    dest = os.path.join(self.repo_path, parts[0])
                    shutil.copy2(backup, dest)
                    rolled_back += 1
                    print(f"  [RESTORED] {parts[0]}")
        # Mark session as rolled back
        target["rolled_back"] = True
        target["rolled_back_at"] = datetime.now().isoformat()
        target["files_restored"] = rolled_back
        with open(log_path, "w", encoding="utf-8") as fh:
            json.dump(log, fh, indent=2, default=str)
        print(f"  Rolled back {rolled_back} action(s).")
        return {"session_id": target["session_id"], "rolled_back": rolled_back}
    # ------------------------------------------------------------------
    # REPORTING
    # ------------------------------------------------------------------
    def _build_report(self, executed: int, skipped: int, failed: int) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "completed_at": datetime.now().isoformat(),
            "repo_path": self.repo_path,
            "dry_run": self.dry_run,
            "force": self.force,
            "total_actions": len(self.actions),
            "executed": executed,
            "skipped": skipped,
            "failed": failed,
            "actions": [a.to_dict() for a in self.actions],
            "reflections": self.srt_tool.get_reflections("self_heal"),
        }
    def _save_audit_log(self, report: Dict[str, Any]) -> None:
        """Append the session report to the heal log."""
        log_path = os.path.join(self.repo_path, HEAL_DIR, "heal_log.json")
        log: Dict[str, Any] = {"sessions": []}
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as fh:
                    log = json.load(fh)
            except (json.JSONDecodeError, IOError):
                log = {"sessions": []}
        log["sessions"].append(report)
        log["last_updated"] = datetime.now().isoformat()
        with open(log_path, "w", encoding="utf-8") as fh:
            json.dump(log, fh, indent=2, default=str)
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print a human-readable summary of the heal session."""
        print()
        print("=" * 60)
        print("  SRT-1 SELF-HEALING REPORT")
        print("=" * 60)
        print(f"  Session:  {report['session_id']}")
        print(f"  Mode:     {'DRY RUN' if report['dry_run'] else 'LIVE'}")
        print(f"  Executed: {report['executed']}")
        print(f"  Skipped:  {report['skipped']}")
        print(f"  Failed:   {report['failed']}")
        print()
        for a in report["actions"]:
            icon = {
                "executed": "OK", "skipped": "--", "failed": "XX",
                "pending": "??", "rolled_back": "RB",
            }.get(a["status"], "??")
            risk = {"low": " ", "medium": "!", "high": "!!"}.get(
                a["risk_level"], "?"
            )
            print(f"  [{icon}] [{risk}] {a['action_type']}: {a['target']}")
            if a.get("error"):
                print(f"          Error: {a['error']}")
            if a.get("details", {}).get("reason"):
                print(f"          Reason: {a['details']['reason']}")
        print("=" * 60)
# ==========================================================================
# CLI
# ==========================================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="SRT-1 Self-Healing Engine - Governed Codebase Remediation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Diagnose (see what would be fixed):\n"
            "    python srt1_self_heal.py diagnose --repo_path .\n\n"
            "  Dry run (show actions without executing):\n"
            "    python srt1_self_heal.py heal --repo_path . --dry-run\n\n"
            "  Heal (execute safe actions):\n"
            "    python srt1_self_heal.py heal --repo_path .\n\n"
            "  Heal with force (include high-risk actions):\n"
            "    python srt1_self_heal.py heal --repo_path . --force\n\n"
            "  Rollback last session:\n"
            "    python srt1_self_heal.py rollback --repo_path .\n\n"
            "  Rollback specific session:\n"
            "    python srt1_self_heal.py rollback --repo_path . "
            "--session heal_20260314_...\n"
        ),
    )
    sub = parser.add_subparsers(dest="command")
    # Diagnose
    d = sub.add_parser("diagnose", help="Analyze manifest and show action plan")
    d.add_argument("--repo_path", required=True, help="Repository path")
    d.add_argument(
        "--manifest", help="Path to manifest (default: repo/srt1_code_manifest.json)"
    )
    # Heal
    h = sub.add_parser("heal", help="Execute remediation actions")
    h.add_argument("--repo_path", required=True, help="Repository path")
    h.add_argument("--manifest", help="Path to manifest")
    h.add_argument(
        "--dry-run", action="store_true", help="Show actions without executing"
    )
    h.add_argument(
        "--force", action="store_true", help="Execute high-risk actions"
    )
    # Rollback
    r = sub.add_parser("rollback", help="Roll back a healing session")
    r.add_argument("--repo_path", required=True, help="Repository path")
    r.add_argument(
        "--session", help="Session ID to rollback (default: most recent)"
    )
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    if args.command == "diagnose":
        engine = SCIARemediationEngine(
            repo_path=args.repo_path,
            manifest_path=getattr(args, "manifest", None),
        )
        report = engine.diagnose()
        report["executed"] = 0
        report["skipped"] = report["total_actions"]
        report["failed"] = 0
        engine.print_summary(report)
    elif args.command == "heal":
        engine = SCIARemediationEngine(
            repo_path=args.repo_path,
            manifest_path=getattr(args, "manifest", None),
            dry_run=args.dry_run,
            force=args.force,
        )
        report = engine.heal()
        engine.print_summary(report)
    elif args.command == "rollback":
        engine = SCIARemediationEngine(repo_path=args.repo_path)
        result = engine.rollback(target_session=getattr(args, "session", None))
        if result.get("error"):
            print(f"  {result['error']}")
        else:
            print(
                f"  Rolled back {result['rolled_back']} action(s) "
                f"from {result['session_id']}"
            )
if __name__ == "__main__":
    main()
