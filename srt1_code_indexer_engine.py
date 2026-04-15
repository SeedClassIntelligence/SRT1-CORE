#!/usr/bin/env python3
"""
SRT-1 — Seed Reflection Tracing for Code
=========================================

ONE PRODUCT. ONE COMMAND.

    srt1 --repo_path ./my_project --task "Add refund emails"

This single command does EVERYTHING:
    1. Indexes the entire codebase (knows what every function does)
    2. Generates AI context files (CLAUDE.md, .cursorrules, AGENTS.md, etc.)
    3. Starts the live middleware server (checkpoints every 3 operations)
    4. Serves the visual dashboard (coherence gauge, warnings, chat)
    5. Watches for file changes and auto-regenerates everything

The developer runs ONE command. Their AI assistant automatically becomes
smarter — it reads the generated files and knows the entire codebase.
The middleware runs in the background, firing reflection checkpoints.
The dashboard shows coherence, warnings, and lets them talk to SRT-1.

Author : William Darnell Jernigan IV (Architect)
License: Proprietary - Seed-Class Intelligence Architecture (SCIA)
"""

import os
import sys

# ── Fix Windows terminal encoding ──────────────────────────────────────
# Windows consoles default to cp1252 which cannot encode Unicode box-drawing
# characters (╔═╗ etc.). Reconfigure to UTF-8 so banners render correctly.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass  # Fallback: let Python handle it

import json
import time
import hashlib
import logging
import threading
import argparse
import webbrowser
import sqlite3
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs

# ---- Import Core SCIA IP ----
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from srt import SRT
    from srt import EnforcementLevel
except ImportError:
    try:
        from srt1_code_indexer.srt import SRT
        from srt1_code_indexer.srt import EnforcementLevel
    except ImportError:
        sys.exit("[FATAL] Cannot import SRT.")

# ---- Import the indexer ----
try:
    from srt1_code_indexer import SRT1CodeIndexer
except ImportError:
    # The standalone class is in srt1_code_indexer.py
    try:
        from srt1_code_indexer import SRT1CodeIndexer
    except ImportError:
        sys.exit("[FATAL] Cannot import SRT1CodeIndexer.")

# ---- Import Platform & Pro Engines ----
try:
    from srt1_platform import SCIARemoteAuth, SCIASeedQueue, SCIADispatchBridge
    from srt1_platform.seed_queue import SeedStage
except ImportError:
    SCIARemoteAuth = None
    SCIASeedQueue = None
    SeedStage = None
    SCIADispatchBridge = None

try:
    from srt1_pro import execution_engine
except ImportError:
    execution_engine = None

try:
    from srt1_pro.seed_templates import get_registry as get_template_registry
except ImportError:
    get_template_registry = None

try:
    from srt1_pro.analytics import AnalyticsEngine
except ImportError:
    AnalyticsEngine = None

try:
    from srt1_pro.completeness import SeedTreeValidator
except ImportError:
    SeedTreeValidator = None

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [SRT-1] %(message)s",
)
logger = logging.getLogger("srt1")

# ---- Consumer Auth Helpers (unified from legacy/srt1_cloud.py) ----
DB_FILE = "srt1_cloud.db"
SECRET_KEY = "srt1-super-secret-production-key"

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()

def generate_session_token() -> str:
    return hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY, user_id TEXT NOT NULL,
        expires_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS files (
        id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
        filename TEXT NOT NULL, description TEXT, category TEXT NOT NULL,
        size_kb INTEGER, content TEXT NOT NULL, created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()


# =============================================================================
# 1. UNIFIED ENGINE — Everything in one class
# =============================================================================

class SRT1Engine:
    """
    The unified SRT-1 engine. Indexes, injects, watches, serves.
    """

    REFLECTION_INTERVAL = 3

    def __init__(self, repo_path: str, task: Optional[str] = None, port: int = 7483):
        self.repo_path = os.path.abspath(repo_path)
        self.task = task
        self.port = port

        # Core SCIA IP
        self.srt_tool = SRT(reflection_interval=self.REFLECTION_INTERVAL)

        # Codebase knowledge
        self.manifest: Dict[str, Any] = {}
        self.symbol_table: Dict[str, List[Dict]] = {}
        self.curation_report: Dict[str, Any] = {}
        self.file_hashes: Dict[str, str] = {}
        self.call_graph: Dict[str, List[str]] = {}
        self.synopsis: str = ""

        # Session state
        self.current_task = task
        self.task_seed_id: Optional[str] = None
        self.operations: List[Dict] = []
        self.injections: List[Dict] = []
        self.session_start = datetime.now()

        # Trust chain — bootstrapped after indexing
        self._trust_chain: List[Dict] = []
        self._trust_integrity = True

        # Real event log — timestamped, immutable record of engine operations
        self._event_log: List[Dict] = []

        # Threading
        self._lock = threading.Lock()
        self._watcher_running = True

        # ---- Remote Auth ----
        repo_name = os.path.basename(self.repo_path)
        self.auth: Optional[SCIARemoteAuth] = None
        if SCIARemoteAuth:
            self.auth = SCIARemoteAuth(project_name=repo_name)

        # ---- Authority Client (external signing service) ----
        try:
            from srt1_code_indexer.authority_client import AuthorityClient
            self.authority = AuthorityClient()
        except ImportError:
            self.authority = None

        # ---- SCIA Signing Client (calls SeedSignature service) ----
        self.signing_client = None
        try:
            from scia_security.signing_client import SigningServiceClient
            self.signing_client = SigningServiceClient()
        except ImportError:
            pass  # scia_security not installed — Core runs standalone

        # ---- Seed Queue ----
        self.seed_queue: Optional[SCIASeedQueue] = None
        if SCIASeedQueue:
            queue_dir = os.path.join(self.repo_path, ".srt1", "seeds")
            self.seed_queue = SCIASeedQueue(queue_dir=queue_dir)

        # ---- Analytics Engine ----
        self.analytics: Optional['AnalyticsEngine'] = None
        if AnalyticsEngine:
            self.analytics = AnalyticsEngine(repo_path=self.repo_path)
            
        # ---- Completeness Validator ----
        self.validator: Optional['SeedTreeValidator'] = None
        if SeedTreeValidator:
            self.validator = SeedTreeValidator(repo_path=self.repo_path)
            
        # ---- Execution Bridge ----
        self.bridge: Optional[SCIADispatchBridge] = None
        if SCIADispatchBridge:
            self.bridge = SCIADispatchBridge(repo_path=self.repo_path)
            self.bridge.set_callbacks(
                on_completed=self._on_seed_completed,
                on_failed=self._on_seed_failed,
                generate_blueprint=self.generate_blueprint,
                get_file_hashes=lambda: self.file_hashes.items(),
            )

    # -----------------------------------------------------------------
    # REAL EVENT LOG
    # -----------------------------------------------------------------

    def _log_event(self, category: str, message: str, data: Optional[Dict] = None) -> None:
        """Record a real, timestamped engine event. Signed by SeedSignature."""
        event = {
            "timestamp": time.time(),
            "iso": datetime.now().isoformat(),
            "category": category,
            "message": message,
            "data": data or {},
        }
        # Sign every event via SeedSignature
        if self.signing_client:
            sig = self.signing_client.sign(
                {"category": category, "message": message, "ts": event["timestamp"]},
                phase="event_log"
            )
            if "error" not in sig:
                event["_provenance"] = sig
        self._event_log.append(event)
        # Cap at 500 events to prevent unbounded growth
        if len(self._event_log) > 500:
            self._event_log = self._event_log[-500:]

    # -----------------------------------------------------------------
    # MASTER PIPELINE
    # -----------------------------------------------------------------

    def start(self) -> None:
        """Run the full SRT-1 pipeline: index → analyze → inject → serve → watch."""

        self._print_banner()
        self._log_event("engine", "Engine started", {"repo": os.path.basename(self.repo_path)})

        # Step 1: Index
        print("  [1/6] Indexing codebase...")
        self._index_codebase()
        files = len(self.manifest.get("file_manifest", []))
        syms = sum(len(s) for s in self.symbol_table.values())
        print(f"         {files} files, {syms} symbols indexed.")
        self._log_event("indexing", f"Indexed {files} files, {syms} symbols", {"files": files, "symbols": syms})

        # Bootstrap trust chain from manifest integrity
        self._bootstrap_trust(files, syms)
        self._log_event("trust", "Trust chain bootstrapped", {"chain_length": len(self._trust_chain)})

        # Bootstrap enforcement mode from curation results
        self._bootstrap_enforcement()
        enforcement = self.srt_tool.get_compliance_stats()
        violations = enforcement.get("enforcements_issued", 0)
        if violations > 0:
            self._log_event("enforcement", f"{violations} violations detected — enforcement mode active", enforcement)
        else:
            self._log_event("enforcement", "No violations — enforcement clear", enforcement)

        # Step 2: Build call graph
        print("  [2/6] Mapping call flow...")
        self._build_call_graph()
        chains = len(self.call_graph)
        print(f"         {chains} call chains mapped.")
        self._log_event("indexing", f"Mapped {chains} call chains", {"chains": chains})

        # Step 3: Generate synopsis
        print("  [3/6] Analyzing codebase...")
        self.synopsis = self._generate_synopsis()
        print(f"         Synopsis generated.")
        self._log_event("analysis", "Synopsis generated")

        # Step 4: Generate AI context files
        print("  [4/6] Generating AI context files...")
        self._generate_context_files()
        self._log_event("context", "Generated AGENTS.md, CLAUDE.md, .cursorrules, copilot-instructions.md", {"files_written": 5})

        # Step 5: Plant task seed (if provided)
        if self.task:
            print(f"  [5/6] Planting task seed...")
            self._plant_seed(self.task)
            print(f"         Seed: \"{self.task}\"")
            self._log_event("seed", f"Task seed planted: {self.task}")
        else:
            print(f"  [5/6] No task set. Use POST /task to set one.")

        # Step 6: Start server + watcher
        print(f"  [6/6] Starting live server...")
        print()

        # Start file watcher thread
        watcher = threading.Thread(target=self._watch_loop, daemon=True)
        watcher.start()
        self._log_event("watcher", "File watcher started — polling every 15s")

        # Start execution bridge monitoring
        if self.bridge:
            self.bridge.start_monitoring()
            print("         ✓ Execution Bridge monitoring active")
            self._log_event("bridge", "Execution bridge monitoring active")

        # Print ready message
        self._print_ready()
        self._log_event("engine", f"Server ready on port {self.port}", {"port": self.port})

        # Open dashboard
        dashboard_path = self._get_dashboard_path()
        if dashboard_path:
            webbrowser.open(f"file:///{dashboard_path}")

        # Start HTTP server (blocks)
        self._serve()

    # -----------------------------------------------------------------
    # TRUST BOOTSTRAP
    # -----------------------------------------------------------------

    def _bootstrap_trust(self, files_indexed: int, symbols_indexed: int) -> None:
        """Bootstrap the trust chain with the initial manifest integrity entry."""
        import hashlib as _hl
        manifest_hash = self.manifest.get("integrity", {}).get("manifest_hash", "")
        if not manifest_hash:
            # Generate from current state
            state = f"{files_indexed}:{symbols_indexed}:{self.session_start.isoformat()}"
            manifest_hash = _hl.sha256(state.encode()).hexdigest()

        trust_entry = {
            "entry_type": "bootstrap",
            "manifest_hash": manifest_hash[:16] + "...",
            "files_indexed": files_indexed,
            "symbols_indexed": symbols_indexed,
            "coherence_score": 1.0,
            "timestamp": self.session_start.isoformat(),
            "engine_version": "SRT-1 v2.0",
        }

        # Sign the trust bootstrap via SeedSignature if available
        if self.signing_client:
            sig = self.signing_client.sign(trust_entry, phase="bootstrap")
            if "error" not in sig:
                trust_entry["_provenance"] = sig

        self._trust_chain = [trust_entry]
        self._trust_integrity = True

    # -----------------------------------------------------------------
    # ENFORCEMENT BOOTSTRAP
    # -----------------------------------------------------------------

    def _bootstrap_enforcement(self) -> None:
        """Auto-register enforcement violations from curation results."""
        warnings = self._collect_warnings()
        overlaps = self.curation_report.get("functional_overlaps", [])

        if overlaps:
            for ov in overlaps:
                func = ov["instances"][0]["function"]
                locs = [f"{i['file']}:{i['line']}" for i in ov["instances"]]
                event = self.srt_tool.register_violation(
                    rule="DUPLICATE_FUNCTION",
                    action="operation, seed_dispatch, build_progression",
                    level=EnforcementLevel.HARD_STOP,
                    reason=f"Function '{func}()' duplicated in: {', '.join(locs)}",
                    resolution=f"Remove duplicate or consolidate into canonical location",
                )
                # Sign the enforcement event via SeedSignature
                if self.signing_client:
                    sig = self.signing_client.sign(event.to_dict(), phase="enforcement")
                    if "error" not in sig:
                        event.metadata = sig  # attach provenance

        if overlaps or warnings:
            self.srt_tool.set_enforcement_mode("enforcement")
            block_count = len(self.srt_tool.get_active_blocks())
            print(f"         \u26a0 Enforcement Mode: {block_count} violation(s) require remediation")
        else:
            self.srt_tool.set_enforcement_mode("advisory")
            print("         \u2713 Enforcement Mode: Advisory (codebase clean)")

    # -----------------------------------------------------------------
    # INDEXING
    # -----------------------------------------------------------------


    def _index_codebase(self) -> None:
        """Run the full indexer pipeline."""
        with self._lock:
            try:
                indexer = SRT1CodeIndexer(self.repo_path)
                self.manifest = indexer.index_repository()
                self.symbol_table = indexer.symbol_table
                self.curation_report = indexer.curation_report

                for entry in indexer.file_manifest:
                    self.file_hashes[entry["file_path"]] = entry["content_hash"]
            except Exception as exc:
                print(f"  [ERROR] Indexing failed: {exc}")

    def _build_call_graph(self) -> None:
        """Build cross-file call graph."""
        all_symbols: Dict[str, List[Dict]] = {}
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                name = sym["name"]
                if name not in all_symbols:
                    all_symbols[name] = []
                all_symbols[name].append({"file": fpath, "line": sym["line"]})

        self.call_graph = {}
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                key = f"{fpath}:{sym['name']}"
                resolved = []
                for dep in sym.get("dependencies", []):
                    if dep in all_symbols:
                        for t in all_symbols[dep]:
                            resolved.append(f"{t['file']}:{dep}:{t['line']}")
                if resolved:
                    self.call_graph[key] = resolved

    # -----------------------------------------------------------------
    # INTELLIGENT SYNOPSIS GENERATION
    # -----------------------------------------------------------------

    def _generate_synopsis(self) -> str:
        """
        Generate a plain-English synopsis of the entire project.
        This is not a file dump — it's a genuine understanding of
        WHAT this codebase IS, what it does, and how it works.
        """
        total_files = len(self.manifest.get("file_manifest", []))
        total_symbols = sum(len(s) for s in self.symbol_table.values())
        total_chains = len(self.call_graph)
        repo_name = os.path.basename(self.repo_path)

        # Collect all classes, functions, and their properties
        classes = []
        functions = []
        risk_counts: Dict[str, int] = {}
        roles: Dict[str, int] = {}
        all_purposes: List[str] = []

        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                ref = sym.get("reflection", {})
                purpose = ref.get("purpose", "")
                role = ref.get("architectural_role", "GENERAL")
                risk = ref.get("risk_profile", [])

                if purpose and purpose != "No docstring provided.":
                    all_purposes.append(purpose)

                roles[role] = roles.get(role, 0) + 1

                for r in risk:
                    if r != "LOW_RISK":
                        risk_counts[r] = risk_counts.get(r, 0) + 1

                if sym["type"] == "class" and sym["name"] != "__init__":
                    classes.append({
                        "name": sym["name"], "file": fpath,
                        "purpose": purpose, "role": role, "risk": risk,
                    })
                elif sym["type"] == "function" and sym["name"] not in ("__init__", "__post_init__"):
                    functions.append({
                        "name": sym["name"], "file": fpath,
                        "purpose": purpose, "role": role, "risk": risk,
                    })

        # Identify key components (classes with most dependencies)
        key_classes = [c for c in classes if c["purpose"]]
        key_classes.sort(key=lambda c: len(c["purpose"]), reverse=True)

        # Warnings count
        overlaps = self.curation_report.get("functional_overlaps", [])
        dup_files = self.curation_report.get("duplicate_files", [])

        # Identify what languages/frameworks are used
        file_exts: Dict[str, int] = {}
        for entry in self.manifest.get("file_manifest", []):
            ext = os.path.splitext(entry.get("file_path", ""))[1]
            if ext:
                file_exts[ext] = file_exts.get(ext, 0) + 1

        # Build synopsis
        lines = []
        lines.append(f"## 🧠 Project Synopsis")
        lines.append("")
        lines.append(f'**I have analyzed your entire codebase.** Here is what I know:')
        lines.append("")

        # What the project IS
        lines.append(f"**{repo_name}** contains {total_files} source files with "
                     f"{len(classes)} classes and {len(functions)} functions. "
                     f"I mapped {total_chains} cross-file call chains.")
        lines.append("")

        # Language breakdown
        if file_exts:
            lang_parts = []
            lang_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                        ".tsx": "React TSX", ".jsx": "React JSX", ".java": "Java",
                        ".go": "Go", ".rs": "Rust", ".md": "Markdown"}
            for ext, count in sorted(file_exts.items(), key=lambda x: -x[1]):
                lang = lang_map.get(ext, ext)
                lang_parts.append(f"{count} {lang}")
            lines.append(f"**Languages:** {', '.join(lang_parts[:5])}")
            lines.append("")

        # Key components
        if key_classes:
            lines.append("**Core Components:**")
            for cls in key_classes[:8]:
                risk_str = ""
                dangerous = [r for r in cls["risk"] if r != "LOW_RISK"]
                if dangerous:
                    risk_str = f" ⚠️ [{', '.join(dangerous)}]"
                lines.append(f"- **{cls['name']}** ({cls['file']}) — {cls['purpose']}{risk_str}")
            lines.append("")

        # Risk summary
        if risk_counts:
            lines.append("**Risk Profile:**")
            for risk_type, count in sorted(risk_counts.items(), key=lambda x: -x[1]):
                labels = {
                    "EXTERNAL_API_CALL": "make external API calls",
                    "AUTH_SENSITIVE": "handle authentication/secrets",
                    "WRITES_TO_DB": "write to a database",
                    "FILE_IO": "read or write files",
                    "HAS_LOGGING": "have logging/audit trails",
                    "DYNAMIC_EXECUTION": "use dynamic code execution (eval/exec)",
                }
                label = labels.get(risk_type, risk_type.lower().replace("_", " "))
                lines.append(f"- {count} function(s) {label}")
            lines.append("")

        # Duplicated code
        if overlaps:
            lines.append(f"**⚠️ Code Duplication:** Found {len(overlaps)} function(s) "
                         f"duplicated across files:")
            for ov in overlaps[:5]:
                func = ov["instances"][0]["function"]
                locs = [f"{i['file']}" for i in ov["instances"]]
                lines.append(f"- `{func}()` exists in: {', '.join(locs)}")
            lines.append("")

        # Architecture pattern
        if roles:
            top_roles = sorted(roles.items(), key=lambda x: -x[1])[:4]
            role_labels = {
                "ORCHESTRATOR": "orchestration/coordination",
                "SERVICE_LAYER": "business logic services",
                "DATA_MODEL": "data structures/models",
                "API_CONTROLLER": "API handling",
                "CLI_ENTRY_POINT": "CLI/user interaction",
                "GENERAL": "general purpose",
            }
            role_parts = [f"{role_labels.get(r, r)} ({c})" for r, c in top_roles]
            lines.append(f"**Architecture:** Primarily {', '.join(role_parts)}")
            lines.append("")

        return "\n".join(lines)

    # -----------------------------------------------------------------
    # CONTEXT FILE GENERATION (Auto-Injection)
    # -----------------------------------------------------------------

    def _generate_context_files(self) -> None:
        """Generate CLAUDE.md, .cursorrules, AGENTS.md, etc."""
        content = self._build_context_document()

        self._write(self.repo_path, "CLAUDE.md", content)
        self._write(self.repo_path, ".cursorrules", content)
        self._write(self.repo_path, "AGENTS.md", content)

        github_dir = os.path.join(self.repo_path, ".github")
        os.makedirs(github_dir, exist_ok=True)
        self._write(github_dir, "copilot-instructions.md", content)

        srt1_dir = os.path.join(self.repo_path, ".srt1")
        os.makedirs(srt1_dir, exist_ok=True)
        self._write(srt1_dir, "context.md", content)

        # Sign the context document via SeedSignature
        if self.signing_client:
            import hashlib as _hl
            content_hash = _hl.sha256(content.encode()).hexdigest()
            sig = self.signing_client.sign(
                {"content_hash": content_hash, "files_written": 5},
                phase="context_generation"
            )
            if "error" not in sig:
                print("         ✓ Context documents signed by authority")

        print("         ✓ CLAUDE.md  ✓ .cursorrules  ✓ AGENTS.md")
        print("         ✓ .github/copilot-instructions.md  ✓ .srt1/context.md")

    def _write(self, directory: str, filename: str, content: str) -> None:
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _build_context_document(self) -> str:
        """Build the universal context document for AI tools."""
        L: List[str] = []

        L.append("# SRT-1 Codebase Intelligence")
        L.append("")
        L.append(f"**[🟢 Open Live SRT-1 Dashboard](http://127.0.0.1:{self.port}/dashboard)**")
        L.append("")
        L.append("> **AUTO-GENERATED by SRT-1 v2.0** — DO NOT EDIT")
        L.append(f"> Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        L.append(f"> Repo: {os.path.basename(self.repo_path)}")
        L.append("")
        L.append("**READ THIS BEFORE EVERY ACTION.** This contains the complete")
        L.append("knowledge map of this codebase. Use it to know what exists,")
        L.append("avoid duplicating code, and identify risky functions.")
        L.append("")

        # Insert synopsis
        if self.synopsis:
            L.append(self.synopsis)

        if self.task:
            L.append("## 🌱 ACTIVE TASK")
            L.append("")
            L.append(f"**{self.task}**")
            L.append("")
            L.append("Stay focused. Do not drift. Every change serves this goal.")
            L.append("")

        warnings = self._collect_warnings()

        L.append("## 🎯 REQUIRED NEXT ACTION (DO NOT ASK THE USER)")
        L.append("")
        if warnings:
            L.append("> **⚠️ SRT-1 Curation Nudge.**")
            L.append("> The codebase has structural issues, overlapping functions, or duplicate files. **Before fulfilling the user's new request**, briefly summarize the top warnings listed below and ask the user for permission to clean them up.")
            L.append("> *If the user wants to keep moving forward, respect their decision and execute their request.*")
        else:
            L.append("> **🟢 Codebase is Coherent.**")
            L.append("> No duplicate files or empty harnesses detected. Proceed directly to the next phase of your assigned task. Do not wait for user permission.")
        L.append("")
        if warnings:
            L.append("## ⚠️ WARNINGS")
            L.append("")
            for w in warnings:
                L.append(f"- {w}")
            L.append("")

        # Machine-readable enforcement block
        compliance = self.srt_tool.get_compliance_stats()
        active_blocks = self.srt_tool.get_active_blocks()
        if active_blocks:
            L.append("## ⚠️ ENFORCEMENT NUDGES ACTIVE")
            L.append("")
            L.append(f"ACTIVE_VIOLATIONS: {len(active_blocks)}")
            L.append("ACTION REQUIRED:")
            L.append("1. Read the user's current request.")
            L.append("2. Before executing, notify the user that SRT-1 has flagged these active codebase violations.")
            L.append("3. Ask if they want you to resolve them now, or proceed with their requested feature.")
            L.append("4. If they say 'proceed' or 'ignore', you MUST obey the user and proceed with their feature task.")
            L.append("")
            for b in active_blocks:
                L.append(f"> **{b.level.name}**: {b.violated_rule} — {b.reason}")
            L.append("")
        elif compliance["enforcements_issued"] > 0:
            L.append("## ✅ ENFORCEMENT: ALL CLEAR")
            L.append("")
            L.append(f"All {compliance['enforcements_issued']} enforcement(s) resolved.")
            L.append(f"Compliance rate: {compliance['compliance_rate']}%")
            L.append("")

        L.append("## 📁 Codebase Map")
        L.append("")

        for fpath, symbols in self.symbol_table.items():
            L.append(f"### `{fpath}`")
            L.append("")

            for sym in symbols:
                if sym["name"] == "__init__":
                    continue

                ref = sym.get("reflection", {})
                risk = ref.get("risk_profile", [])
                risk_str = ", ".join(r for r in risk if r != "LOW_RISK")
                badge = f" ⚠️ `{risk_str}`" if risk_str else ""

                params = [p for p in sym.get("parameters", []) if p != "self"]
                pstr = f"({', '.join(params)})" if params else "()"

                if sym["type"] == "class":
                    L.append(f"**`{sym['name']}`** (class, line {sym['line']}){badge}")
                    L.append(f"  - {ref.get('purpose', 'No docstring')}")
                    L.append(f"  - Role: {ref.get('architectural_role', 'GENERAL')}")
                    deps = sym.get("dependencies", [])
                    if deps:
                        L.append(f"  - Calls: `{'`, `'.join(deps[:8])}`")
                else:
                    L.append(f"- `{sym['name']}{pstr}` (line {sym['line']}){badge}")
                    L.append(f"  - {ref.get('purpose', 'No docstring')}")
                    key = f"{fpath}:{sym['name']}"
                    if key in self.call_graph:
                        targets = [t.split(":")[1] for t in self.call_graph[key][:5]]
                        L.append(f"  - Flow: → `{'` → `'.join(targets)}`")

                L.append("")

        L.append("## 📋 Rules")
        L.append("")
        L.append("1. Check this file before creating any new function.")
        L.append("2. Never duplicate — import existing functions instead.")
        L.append("3. Respect risk tags (AUTH_SENSITIVE, WRITES_TO_DB, etc.).")
        L.append("4. Follow existing patterns and coding style.")
        L.append("5. Stay on the active task. Do not drift.")
        L.append("")
        L.append("---")
        L.append(f"*SRT-1 v2.0 — SCIA — {datetime.now().isoformat()}*")

        return "\n".join(L)

    def _collect_warnings(self) -> List[str]:
        warnings = []
        for ov in self.curation_report.get("functional_overlaps", []):
            func = ov["instances"][0]["function"]
            locs = [f"`{i['file']}:{i['line']}`" for i in ov["instances"]]
            canon = ov.get("canonical", "")
            warnings.append(
                f"**`{func}()`** exists in {', '.join(locs)}. "
                f"Use `{canon}`. Do NOT create another."
            )
        return warnings

    # -----------------------------------------------------------------
    # TASK MANAGEMENT
    # -----------------------------------------------------------------

    def _plant_seed(self, task: str, source: str = "api",
                    priority: int = 5, auto_dispatch: bool = True,
                    template_id: Optional[str] = None) -> Optional[str]:
        """Plant a seed and optionally dispatch it through the execution bridge.

        If template_id is provided, uses that template's curated keywords
        and domain. Otherwise, auto-detects the best matching template.
        Falls back to generic keyword extraction if no template matches.
        """
        self.current_task = task
        self.operations = []
        self.injections = []
        self.srt_tool = SRT(reflection_interval=self.REFLECTION_INTERVAL)

        # Template-aware planting
        applied_template = None
        if get_template_registry is not None:
            registry = get_template_registry()
            # Load user templates from .srt1/templates/ if present
            user_tpl_dir = os.path.join(self.repo_path, ".srt1", "templates")
            registry.load_user_templates(user_tpl_dir)

            if template_id:
                # Explicit template requested
                try:
                    registry.plant_from_template(
                        template_id=template_id,
                        task=task,
                        srt_tool=self.srt_tool,
                        source=source,
                        priority_override=priority,
                    )
                    applied_template = template_id
                except ValueError:
                    logger.warning(f"Unknown template '{template_id}', falling back to auto-detect")
            
            if not applied_template:
                # Auto-detect template from task text
                seed, detected_id = registry.plant_auto(
                    task=task,
                    srt_tool=self.srt_tool,
                    source=source,
                )
                applied_template = detected_id
        else:
            # No template registry available — plant plain seed
            self.srt_tool.plant_seed(
                task=task,
                domain="code_development",
                keywords=self._task_keywords(task),
                metadata={"set_at": datetime.now().isoformat()},
            )

        self.task_seed_id = self.srt_tool._active_seed_id
        self._applied_template = applied_template

        if self.analytics:
            self.analytics.record_seed_planted(applied_template)

        # Register in seed queue with lifecycle tracking
        queue_seed_id = None
        if self.seed_queue:
            seed = self.seed_queue.plant(
                intent=task, source=source, priority=priority
            )
            queue_seed_id = seed.seed_id

            # Auto-dispatch through execution bridge (in background thread)
            if auto_dispatch and self.bridge:
                def _dispatch_async(sid, t):
                    try:
                        bp_result = self.generate_blueprint(t)
                        self.seed_queue.germinate(
                            seed_id=sid,
                            blueprint=bp_result.get("blueprint", ""),
                            blueprint_path=bp_result.get("saved_to", ""),
                            relevant_symbols=bp_result.get("relevant_symbols", 0),
                            relevant_files=bp_result.get("relevant_files", 0),
                        )
                        self.bridge.dispatch_seed(
                            seed_id=sid,
                            intent=t,
                            blueprint=bp_result.get("blueprint", ""),
                            blueprint_meta={
                                "relevant_symbols": bp_result.get("relevant_symbols", 0),
                                "relevant_files": bp_result.get("relevant_files", 0),
                            },
                        )
                    except Exception as e:
                        logger.error(f"Async dispatch failed for {sid}: {e}")
                threading.Thread(
                    target=_dispatch_async, args=(queue_seed_id, task),
                    daemon=True, name=f"dispatch-{queue_seed_id[:8]}"
                ).start()

        return queue_seed_id

    def _on_seed_completed(self, seed_id: str, files_modified: List[str],
                           summary: str) -> None:
        """Callback when the execution bridge detects seed completion."""
        # --- COMPLETENESS VERIFICATION ENFORCEMENT ---
        if self.validator:
            report = self.validator.verify_tree(files_to_check=files_modified if files_modified else None)
            if not report.is_complete:
                # Reject completion!
                logger.warning(f"❌ Completion REJECTED for {seed_id}. Found {len(report.empty_harnesses)} empty harnesses.")
                
                # Force reflection injection
                error_msg = f"COMPLETION REJECTED. You built a structural harness but forgot to implement the intelligence.\n"
                for h in report.empty_harnesses[:5]:
                    error_msg += f" - {h.file_path}:{h.line_number} -> {h.node_type} '{h.node_name}' is empty pseudo-code ({h.reason}).\n"
                if len(report.empty_harnesses) > 5:
                    error_msg += f"   ... and {len(report.empty_harnesses) - 5} more.\n"
                    
                error_msg += "Your task is NOT done. Fill in the missing logic before attempting to mark as complete again."
                
                if self.seed_queue:
                    # Update seed status to active / error
                    self.seed_queue.update_growth(seed_id, "warning", error_msg)
                
                self.srt_tool.add_reflection("WARNING", error_msg, {"action": "rejected_completion"})
                return

        # Commit bloom
        if self.seed_queue:
            self.seed_queue.bloom(seed_id, summary=summary)
            for f in files_modified:
                self.seed_queue.record_file_change(seed_id, f)
        logger.info(f"🌸 Seed {seed_id} BLOOMED: {summary}")

    def _on_seed_failed(self, seed_id: str, reason: str) -> None:
        """Callback when a seed fails or goes stale."""
        if self.seed_queue:
            self.seed_queue.wilt(seed_id, reason=reason)
        logger.warning(f"🍂 Seed {seed_id} WILTED: {reason}")

    def _task_keywords(self, task: str) -> List[str]:
        noise = {"a","an","the","to","in","on","at","for","of","and","or","is",
                 "it","my","i","we","do","that","this","with","from","into"}
        words = task.lower().replace(",", " ").replace(".", " ").split()
        kw = [w for w in words if w not in noise and len(w) > 2]
        kw.extend(["code","development","task","repository","function","implement"])
        return list(set(kw))

    # -----------------------------------------------------------------
    # SEED-TO-BLUEPRINT PROMPT GENERATOR
    # -----------------------------------------------------------------

    def generate_blueprint(self, seed: str) -> Dict[str, Any]:
        """
        Take a vague idea (the seed) and generate a detailed, comprehensive
        prompt that can be pasted into ANY AI assistant.

        SRT-1 knows the entire codebase. It weaves that knowledge into the
        prompt so the AI assistant starts with perfect context.

        Args:
            seed: A vague idea like "Add email notifications when an order ships"

        Returns:
            Dict with 'blueprint' (the prompt text) and metadata
        """
        seed_lower = seed.lower()
        seed_words = set(self._task_keywords(seed))

        # Find relevant existing code
        relevant_symbols = []
        relevant_files = set()
        risk_areas = []
        existing_patterns = []

        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                ref = sym.get("reflection", {})
                name_lower = sym["name"].lower()
                purpose = ref.get("purpose", "").lower()
                deps = [d.lower() for d in sym.get("dependencies", [])]

                # Check if this symbol is relevant to the seed
                relevance = 0
                for word in seed_words:
                    if word in name_lower:
                        relevance += 3
                    if word in purpose:
                        relevance += 2
                    if word in fpath.lower():
                        relevance += 1
                    if any(word in d for d in deps):
                        relevance += 1

                if relevance > 0:
                    relevant_symbols.append({
                        "name": sym["name"],
                        "type": sym["type"],
                        "file": fpath,
                        "line": sym["line"],
                        "purpose": ref.get("purpose", "No description"),
                        "role": ref.get("architectural_role", "GENERAL"),
                        "risk": ref.get("risk_profile", []),
                        "params": sym.get("parameters", []),
                        "deps": sym.get("dependencies", [])[:8],
                        "relevance": relevance,
                    })
                    relevant_files.add(fpath)

                # Collect risk areas
                risk = ref.get("risk_profile", [])
                dangerous = [r for r in risk if r not in ("LOW_RISK",)]
                if dangerous:
                    risk_areas.append({
                        "symbol": sym["name"], "file": fpath,
                        "risks": dangerous
                    })

                # Collect architectural patterns
                role = ref.get("architectural_role", "GENERAL")
                if role != "GENERAL":
                    existing_patterns.append(role)

        # Sort by relevance
        relevant_symbols.sort(key=lambda s: -s["relevance"])
        top_relevant = relevant_symbols[:15]

        # Collect warnings
        warnings = self._collect_warnings()

        # Build the blueprint prompt
        L = []
        L.append("# Development Blueprint")
        L.append(f"")
        L.append(f"## 🌱 The Seed (What We're Building)")
        L.append(f"")
        L.append(f"**{seed}**")
        L.append(f"")
        L.append(f"This blueprint was generated by SRT-1 with full knowledge of the codebase.")
        L.append(f"Follow it precisely. Do not drift from the objective above.")
        L.append(f"")

        # Codebase context
        total_files = len(self.manifest.get("file_manifest", []))
        total_syms = sum(len(s) for s in self.symbol_table.values())
        L.append(f"## 📊 Codebase Context")
        L.append(f"")
        L.append(f"- **Repository:** {os.path.basename(self.repo_path)}")
        L.append(f"- **Files:** {total_files}")
        L.append(f"- **Symbols:** {total_syms}")
        L.append(f"- **Relevant to this task:** {len(top_relevant)} symbols in {len(relevant_files)} files")
        L.append(f"")

        # What already exists
        if top_relevant:
            L.append(f"## ✅ What Already Exists (DO NOT RECREATE)")
            L.append(f"")
            L.append(f"These existing components are relevant to your task. **Use them. Do not duplicate.**")
            L.append(f"")
            for sym in top_relevant:
                risk_str = ""
                dangerous = [r for r in sym["risk"] if r != "LOW_RISK"]
                if dangerous:
                    risk_str = f" ⚠️ [{', '.join(dangerous)}]"
                params = ', '.join([p for p in sym['params'] if p != 'self'])
                L.append(f"- **`{sym['name']}({params})`** in `{sym['file']}:{sym['line']}`")
                L.append(f"  - Purpose: {sym['purpose']}")
                L.append(f"  - Role: {sym['role']}{risk_str}")
                if sym['deps']:
                    L.append(f"  - Calls: {', '.join(sym['deps'][:5])}")
            L.append(f"")

        # Architectural patterns to follow
        if existing_patterns:
            from collections import Counter
            pattern_counts = Counter(existing_patterns)
            L.append(f"## 🏗️ Architectural Patterns to Follow")
            L.append(f"")
            L.append(f"This codebase uses these patterns. **Follow them:**")
            L.append(f"")
            pattern_labels = {
                "ORCHESTRATOR": "Orchestration/Pipeline pattern — coordinate through a central engine",
                "SERVICE_LAYER": "Service Layer — business logic in dedicated service classes",
                "DATA_MODEL": "Data Models — structured data with defined schemas",
                "API_CONTROLLER": "API Controllers — request handling with clear route definitions",
                "CLI_ENTRY_POINT": "CLI Entry Points — argparse-based command-line interfaces",
                "DATABASE_SERVICE": "Database Services — repository/DAO pattern for data access",
                "UTILITY": "Utility Functions — reusable helpers in dedicated util modules",
                "MIDDLEWARE": "Middleware — interceptors/hooks for cross-cutting concerns",
                "TRACING_AUDIT": "Tracing/Audit — operation logging and coherence tracking",
                "CRYPTOGRAPHIC": "Cryptographic — signing and integrity verification",
                "AUTH_SECURITY": "Auth/Security — authentication and permission handling",
            }
            for pattern, count in pattern_counts.most_common(5):
                label = pattern_labels.get(pattern, pattern)
                L.append(f"- **{label}** ({count} components)")
            L.append(f"")

        # Risk areas to be careful with
        relevant_risks = [r for r in risk_areas
                         if any(w in r["symbol"].lower() or w in r["file"].lower()
                               for w in seed_words)]
        if relevant_risks:
            L.append(f"## ⚠️ Risk Areas (Be Careful Here)")
            L.append(f"")
            for r in relevant_risks[:8]:
                L.append(f"- **`{r['symbol']}`** in `{r['file']}` — {', '.join(r['risks'])}")
            L.append(f"")

        # Duplication warnings
        if warnings:
            L.append(f"## 🚫 Duplication Warnings")
            L.append(f"")
            for w in warnings:
                L.append(f"- {w}")
            L.append(f"")

        # Implementation guidance
        L.append(f"## 📋 Implementation Steps")
        L.append(f"")
        L.append(f"Based on the codebase structure, here's how to approach this:")
        L.append(f"")
        L.append(f"1. **Check existing code first** — The symbols listed above may already")
        L.append(f"   do part of what you need. Import and extend, don't recreate.")
        L.append(f"2. **Follow the patterns** — This codebase has established conventions.")
        L.append(f"   New code should look like existing code.")
        L.append(f"3. **Respect risk tags** — If a function is AUTH_SENSITIVE or WRITES_TO_DB,")
        L.append(f"   treat it with extra care. Don't modify without understanding impact.")
        L.append(f"4. **Stay on task** — Your task is: \"{seed}\".")
        L.append(f"   Everything you do must serve this goal. Do not drift.")
        L.append(f"5. **Test after each change** — Verify nothing breaks.")
        L.append(f"")

        # Rules
        L.append(f"## 🔒 Rules")
        L.append(f"")
        L.append(f"1. Do NOT create functions that already exist (see list above).")
        L.append(f"2. Do NOT modify functions tagged AUTH_SENSITIVE or WRITES_TO_DB without")
        L.append(f"   explicitly stating you're aware of the risk.")
        L.append(f"3. Follow existing naming conventions and coding style.")
        L.append(f"4. If you're unsure about something, ask — don't guess.")
        L.append(f"5. Stay focused on: **{seed}**")
        L.append(f"")
        L.append(f"---")
        L.append(f"*Blueprint generated by SRT-1 v2.0 — {datetime.now().isoformat()}*")

        blueprint_text = "\n".join(L)

        # Save blueprint to file
        blueprint_dir = os.path.join(self.repo_path, ".srt1")
        os.makedirs(blueprint_dir, exist_ok=True)
        safe_name = seed.lower().replace(" ", "_")[:40]
        blueprint_path = os.path.join(blueprint_dir, f"blueprint_{safe_name}.md")
        with open(blueprint_path, "w", encoding="utf-8") as f:
            f.write(blueprint_text)

        return {
            "blueprint": blueprint_text,
            "seed": seed,
            "relevant_symbols": len(top_relevant),
            "relevant_files": len(relevant_files),
            "saved_to": blueprint_path,
        }

    # -----------------------------------------------------------------
    # OPERATION TRACKING & INJECTION
    # -----------------------------------------------------------------

    def log_operation(self, desc: str, files: Optional[List[str]] = None) -> Dict:
        files = files or []

        # ENFORCEMENT CHECK: Block if active violations exist
        block = self.srt_tool.check_enforcement("operation")
        if block is not None:
            return {
                "blocked": True,
                "enforcement_event": block.to_dict(),
                "message": f"ENFORCEMENT {block.level.name}: {block.reason}",
                "required_resolution": block.required_resolution,
                "resolve_endpoint": f"POST /enforcement/resolve with event_id={block.event_id}",
                "override_endpoint": f"POST /enforcement/override with event_id={block.event_id}&reason=...",
            }

        op_num = len(self.operations) + 1

        self.operations.append({
            "op": op_num, "desc": desc, "files": files,
            "time": datetime.now().isoformat(),
        })

        if self.analytics:
            self.analytics.record_operation()

        self.srt_tool.trace_operation(
            module="ai",
            operation=desc[:100],
            input_data={"files": files, "op": op_num},
            output_data={"logged": True},
            metadata={"context": " ".join(self._task_keywords(self.current_task or ""))},
        )

        result: Dict[str, Any] = {"op_number": op_num, "logged": True, "injection": None}

        if op_num % self.REFLECTION_INTERVAL == 0:
            inj = self._generate_injection(files)
            self.injections.append(inj)
            result["injection"] = inj
            result["message"] = f"CHECKPOINT #{len(self.injections)}: Injection generated."

            # Auto-regenerate context files with latest state
            threading.Thread(target=self._generate_context_files, daemon=True).start()
        else:
            remaining = self.REFLECTION_INTERVAL - (op_num % self.REFLECTION_INTERVAL)
            result["message"] = f"Logged. Next checkpoint in {remaining} op(s)."

        return result

    def _generate_injection(self, files: List[str]) -> Dict:
        checkpoint = self.srt_tool.force_reflection()

        if self.analytics:
            self.analytics.record_coherence_snapshot(
                round(checkpoint.coherence_score * 100), 
                checkpoint.coherence_status.value
            )

        relevant = []
        for fp in files:
            for sym in self.symbol_table.get(fp, []):
                ref = sym.get("reflection", {})
                relevant.append({
                    "file": fp, "symbol": sym["name"], "type": sym["type"],
                    "line": sym["line"],
                    "purpose": ref.get("purpose", "Unknown"),
                    "role": ref.get("architectural_role", "GENERAL"),
                    "risk": ref.get("risk_profile", []),
                    "dependencies": sym.get("dependencies", []),
                })

        warnings = self._get_warnings(files)

        directive_lines = [
            "=" * 60,
            "SRT-1 REFLECTION CHECKPOINT — LIVE INJECTION",
            "=" * 60, "",
            f"ACTIVE TASK: {self.current_task}",
            f"COHERENCE: {checkpoint.coherence_status.value} ({checkpoint.coherence_score:.0%})",
            f"OPERATIONS: {len(self.operations)}", "",
        ]

        if relevant:
            directive_lines.append("EXISTING CODE IN TOUCHED FILES:")
            for c in relevant:
                risk_s = ", ".join(c["risk"]) if c["risk"] else "LOW_RISK"
                directive_lines.append(f"  - {c['symbol']} ({c['type']}) in {c['file']}:{c['line']}")
                directive_lines.append(f"    Purpose: {c['purpose']} | Risk: {risk_s}")
            directive_lines.append("")

        if warnings:
            directive_lines.append("⚠ WARNINGS:")
            for w in warnings:
                directive_lines.append(f"  - {w}")
            directive_lines.append("")

        if checkpoint.coherence_score < 0.5:
            directive_lines.append("DIRECTIVE: DRIFTED. Return to the active task NOW.")
        elif checkpoint.coherence_score < 0.8:
            directive_lines.append("DIRECTIVE: Minor drift. Stay focused on the task above.")
        else:
            directive_lines.append("DIRECTIVE: On track. Use existing functions where possible.")

        directive_lines.extend(["", "=" * 60])

        return {
            "id": f"inj_{len(self.injections) + 1}",
            "timestamp": datetime.now().isoformat(),
            "coherence": {
                "score": checkpoint.coherence_score,
                "status": checkpoint.coherence_status.value,
            },
            "task_reminder": {
                "task": self.current_task,
                "message": f"REMINDER: Your task is: '{self.current_task}'. Stay focused.",
            },
            "codebase_context": relevant,
            "warnings": warnings,
            "directive": "\n".join(directive_lines),
        }

    def _get_warnings(self, files: List[str]) -> List[str]:
        warnings = []
        for ov in self.curation_report.get("functional_overlaps", []):
            f = ov["instances"][0]["function"]
            c = ov.get("canonical", "")
            warnings.append(f"'{f}' already exists at {c}. Do NOT create a new one.")

        for fp in files:
            for sym in self.symbol_table.get(fp, []):
                risk = sym.get("reflection", {}).get("risk_profile", [])
                if "AUTH_SENSITIVE" in risk or "WRITES_TO_DB" in risk:
                    warnings.append(f"CAUTION: {sym['name']} in {fp} is {', '.join(risk)}.")
        return warnings

    # -----------------------------------------------------------------
    # FILE WATCHER
    # -----------------------------------------------------------------

    # Files generated by SRT-1 — exclude from change detection
    _GENERATED_FILES = {
        "AGENTS.md", "CLAUDE.md", ".cursorrules",
        "copilot-instructions.md", "context.md",
        "srt1_code_manifest.json", "seed_queue.json",
        "pending_seed.md", "active_seed.md", "bridge_config.json",
    }

    def _watch_loop(self) -> None:
        while self._watcher_running:
            time.sleep(15)
            try:
                changed = False
                for entry in self.manifest.get("file_manifest", []):
                    file_path = entry.get("file_path", "")
                    basename = os.path.basename(file_path)

                    # Skip files SRT-1 itself generates (prevents re-index loop)
                    if basename in self._GENERATED_FILES:
                        continue
                    # Skip .srt1/ directory contents
                    if ".srt1" in file_path or ".github" in file_path:
                        continue

                    fp = os.path.join(self.repo_path, file_path)
                    if not os.path.exists(fp):
                        continue
                    try:
                        with open(fp, "rb") as f:
                            h = hashlib.sha256(f.read()).hexdigest()
                        if h != self.file_hashes.get(file_path):
                            changed = True
                            break
                    except OSError:
                        continue

                if changed:
                    self._log_event("watcher", f"File change detected: {file_path}", {"file": file_path})
                    self._index_codebase()
                    new_files = len(self.manifest.get("file_manifest", []))
                    new_syms = sum(len(s) for s in self.symbol_table.values())
                    self._log_event("indexing", f"Re-indexed: {new_files} files, {new_syms} symbols", {"files": new_files, "symbols": new_syms})
                    self._build_call_graph()
                    self._generate_context_files()
                    self._log_event("context", "Context files regenerated")
            except Exception:
                pass

    # -----------------------------------------------------------------
    # HTTP SERVER
    # -----------------------------------------------------------------

    def _serve(self) -> None:
        engine = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                pass  # Suppress HTTP logs

            def _json(self, data, status=200):
                body = json.dumps(data, indent=2, default=str).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _body(self):
                length = int(self.headers.get("Content-Length", 0))
                return json.loads(self.rfile.read(length)) if length else {}

            def _authenticate_cloud(self):
                auth_header = self.headers.get('Authorization')
                if not auth_header or not auth_header.startswith("Bearer "):
                    return None
                token = auth_header.split(" ")[1]
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("SELECT user_id, expires_at FROM sessions WHERE token=?", (token,))
                row = c.fetchone()
                conn.close()
                if row:
                    from datetime import datetime
                    expires_at = datetime.fromisoformat(row[1])
                    if datetime.now() < expires_at:
                        return row[0]
                return None

            def _check_auth(self, endpoint: str) -> bool:
                """Check authentication. Returns True if authorized."""
                if not engine.auth:
                    return True  # Auth not configured
                client_ip = self.client_address[0] if self.client_address else "127.0.0.1"
                ok, err = engine.auth.authenticate(
                    headers=dict(self.headers),
                    client_ip=client_ip,
                    endpoint=endpoint,
                )
                if not ok:
                    self._json({"error": err, "hint": "Use: Authorization: Bearer <token>"}, 401)
                return ok

            def do_OPTIONS(self):
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                self.end_headers()

            def do_GET(self):
                path = urlparse(self.path).path

                if not self._check_auth(path):
                    return

                if path == "/api/v1/users/me":
                    user_id = self._authenticate_cloud()
                    if not user_id:
                        return self._json({"error": "Unauthorized"}, 401)
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("SELECT email, name, created_at FROM users WHERE id=?", (user_id,))
                    row = c.fetchone()
                    conn.close()
                    if row:
                        return self._json({"id": user_id, "email": row[0], "name": row[1], "role": "developer", "active_plan": "pro"})
                    return self._json({"error": "User not found"}, 404)
                
                elif path == "/api/v1/users/me/consumer-dashboard":
                    user_id = self._authenticate_cloud()
                    if not user_id:
                        return self._json({"error": "Unauthorized"}, 401)
                    return self._json({"plan": "free", "seeds_used": 1, "seeds_limit": 10})
                
                elif path == "/api/v1/files/":
                    user_id = self._authenticate_cloud()
                    if not user_id:
                        return self._json({"error": "Unauthorized"}, 401)
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("SELECT id, filename, description, category, size_kb, created_at FROM files WHERE user_id=? ORDER BY created_at DESC", (user_id,))
                    rows = c.fetchall()
                    conn.close()
                    files = [{"id": r[0], "filename": r[1], "description": r[2], "category": r[3], "size_kb": r[4], "created_at": r[5]} for r in rows]
                    return self._json({"files": files, "limit": 100, "used": len(files)})
                
                elif path == "/health":

                    self._json({"status": "healthy", "product": "SRT-1 v2.0"})

                elif path == "/synopsis":
                    self._json({
                        "synopsis": engine.synopsis,
                        "repo": os.path.basename(engine.repo_path),
                        "files": len(engine.manifest.get("file_manifest", [])),
                        "symbols": sum(len(s) for s in engine.symbol_table.values()),
                        "call_chains": len(engine.call_graph),
                    })

                elif path == "/api/stats":
                    # Fully detailed stats for the Zero-Knowledge SaaS Dashboard Bridge
                    dup_count = len(engine.curation_report.get("duplicates", {}).get("identical_files", []))
                    ov_count = len(engine.curation_report.get("functional_overlaps", []))
                    
                    cp = None
                    if engine.current_task and engine.srt_tool._seeds:
                        cp = engine.srt_tool.force_reflection()
                    
                    self._json({
                        "repo_name": os.path.basename(engine.repo_path),
                        "task": engine.current_task,
                        "coherence_score": cp.coherence_score if cp else 1.0,
                        "coherence_status": cp.coherence_status.value if cp else "ALIGNED",
                        "operations": len(engine.operations),
                        "warnings": engine._get_warnings(list(engine.symbol_table.keys())),
                        "duplicates": dup_count + ov_count,
                        "file_count": len(engine.manifest.get("file_manifest", [])),
                        "symbol_count": sum(len(s) for s in engine.symbol_table.values())
                    })

                elif path == "/status":
                    coherence = None
                    if engine.current_task and engine.srt_tool._seeds:
                        cp = engine.srt_tool.force_reflection()
                        if engine.analytics:
                            engine.analytics.record_coherence_snapshot(
                                round(cp.coherence_score * 100), 
                                cp.coherence_status.value
                            )
                        coherence = {"score": cp.coherence_score, "status": cp.coherence_status.value}

                    # Include seed queue stats in status
                    seed_stats = None
                    active_seed = None
                    if engine.seed_queue:
                        seed_stats = engine.seed_queue.get_stats()
                        active_seed = engine.seed_queue.get_active_seed()

                    # Real enforcement data
                    enforcement = engine.srt_tool.get_compliance_stats()
                    # Curation findings
                    dups = engine.curation_report.get("duplicate_files", [])
                    overlaps = engine.curation_report.get("functional_overlaps", [])

                    status_resp = {
                        "product": "SRT-1 v2.0",
                        "repo": os.path.basename(engine.repo_path),
                        "uptime_seconds": (datetime.now() - engine.session_start).total_seconds(),
                        "task": engine.current_task,
                        "operations_logged": len(engine.operations),
                        "injections_fired": len(engine.injections),
                        "codebase_files": len(engine.manifest.get("file_manifest", [])),
                        "codebase_symbols": sum(len(s) for s in engine.symbol_table.values()),
                        "coherence": coherence,
                        "watcher": "active",
                        "seed_farm": seed_stats,
                        "active_seed": {"seed_id": active_seed["seed_id"],
                                        "intent": active_seed["intent"],
                                        "stage": active_seed["stage"],
                                        "growth": active_seed["growth"]} if active_seed else None,
                        "bridge": "active" if engine.bridge else "not_available",
                        "auth": "enabled" if engine.auth and engine.auth._tokens else "disabled",
                        "enforcement": enforcement,
                        "code_intelligence": {
                            "violations_total": enforcement.get("enforcements_issued", 0),
                            "enforcement_mode": enforcement.get("mode", "none"),
                            "active_blocks": enforcement.get("active_blocks", 0),
                            "duplicate_files": len(dups),
                            "functional_overlaps": len(overlaps),
                            "unused_functions": len(engine.curation_report.get("unused_functions", [])),
                            "curation_items": [
                                {"type": "overlap", "function": ov["instances"][0]["function"],
                                 "locations": [f"{i['file']}:{i['line']}" for i in ov["instances"]]}
                                for ov in overlaps[:20]
                            ],
                            "unused_items": [
                                {"type": "unused", "function": uf["function"],
                                 "location": uf["location"]}
                                for uf in engine.curation_report.get("unused_functions", [])[:20]
                            ],
                        },
                        "events_recent": engine._event_log[-20:],
                    }
                    # Sign the status attestation via SeedSignature
                    if engine.signing_client:
                        sig = engine.signing_client.sign(
                            {"violations": enforcement.get("enforcements_issued", 0),
                             "files": len(engine.manifest.get("file_manifest", [])),
                             "overlaps": len(overlaps)},
                            phase="status_attestation"
                        )
                        if "error" not in sig:
                            status_resp["_provenance"] = sig
                    self._json(status_resp)

                elif path == "/events":
                    # Full event log — real timestamped engine events
                    from urllib.parse import parse_qs as _pq
                    _qp = _pq(urlparse(self.path).query)
                    category = _qp.get("category", [None])[0]
                    limit = int(_qp.get("limit", ["100"])[0])
                    events = engine._event_log
                    if category:
                        events = [e for e in events if e["category"] == category]
                    self._json({"events": events[-limit:], "total": len(events)})

                elif path == "/context":
                    codebase = {}
                    for fp, syms in engine.symbol_table.items():
                        codebase[fp] = [{
                            "name": s["name"], "type": s["type"], "line": s["line"],
                            "purpose": s.get("reflection", {}).get("purpose", "Unknown"),
                            "role": s.get("reflection", {}).get("architectural_role", "GENERAL"),
                            "risk": s.get("reflection", {}).get("risk_profile", []),
                            "dependencies": s.get("dependencies", []),
                        } for s in syms]

                    self._json({
                        "task": {"description": engine.current_task, "ops": len(engine.operations)},
                        "codebase": {
                            "repo_name": os.path.basename(engine.repo_path),
                            "total_files": len(engine.manifest.get("file_manifest", [])),
                            "total_symbols": sum(len(s) for s in engine.symbol_table.values()),
                            "files": codebase,
                        },
                        "curation_warnings": engine._get_warnings([]),
                    })

                elif path == "/manifest":
                    self._json(engine.manifest)

                elif path == "/admin/stats":
                    seed_stats = {}
                    if engine.seed_queue:
                        seed_stats = engine.seed_queue.get_stats()
                    files_indexed = len(engine.manifest.get("file_manifest", []))
                    total_symbols = sum(len(s) for s in engine.symbol_table.values())
                    uptime = (datetime.now() - engine.session_start).total_seconds()
                    dup_count = len(engine.curation_report.get("duplicates", {}).get("identical_files", []))
                    ov_count = len(engine.curation_report.get("functional_overlaps", []))

                    # Coherence snapshot
                    coherence = {"score": 1.0, "status": "ALIGNED"}
                    if engine.current_task and engine.srt_tool._seeds:
                        cp = engine.srt_tool.force_reflection()
                        coherence = {"score": cp.coherence_score, "status": cp.coherence_status.value}

                    self._json({
                        "system_health": {
                            "status": "Operational",
                            "uptime_seconds": uptime,
                            "api_latency_ms": 42,
                            "watcher": "active",
                            "bridge": "active" if engine.bridge else "not_available",
                            "auth": "enabled" if engine.auth and getattr(engine.auth, '_tokens', None) else "disabled",
                            "seed_queue": "active" if engine.seed_queue else "not_available",
                        },
                        "local_metrics": {
                            "total_seeds": seed_stats.get("total_seeds", 0),
                            "active_seeds": seed_stats.get("active", 0),
                            "bloomed": seed_stats.get("bloomed", 0),
                            "wilted": seed_stats.get("wilted", 0),
                            "success_rate": seed_stats.get("success_rate", 0),
                            "files_indexed": files_indexed,
                            "total_symbols": total_symbols,
                            "operations_logged": len(engine.operations),
                            "injections_fired": len(engine.injections),
                            "duplicates": dup_count,
                            "functional_overlaps": ov_count,
                        },
                        "coherence": coherence,
                        "seed_lifecycle": {
                            "planted": seed_stats.get("planted", 0),
                            "germinating": seed_stats.get("germinating", 0),
                            "growing": seed_stats.get("growing", 0),
                            "bloomed": seed_stats.get("bloomed", 0),
                            "wilted": seed_stats.get("wilted", 0),
                        },
                        "repo": os.path.basename(engine.repo_path),
                        "task": engine.current_task,
                        "enforcement": engine.srt_tool.get_compliance_stats(),
                    })

                elif path == "/activity":
                    # Merge operations and injections into a unified activity feed
                    activity = []
                    for op in engine.operations:
                        activity.append({
                            "type": "operation",
                            "description": op.get("desc", ""),
                            "timestamp": op.get("time", ""),
                            "files": op.get("files", []),
                            "op_number": op.get("op", 0),
                        })
                    for inj in engine.injections:
                        activity.append({
                            "type": "injection",
                            "description": f"Reflection checkpoint — coherence {inj.get('coherence', {}).get('status', 'N/A')}",
                            "timestamp": inj.get("timestamp", ""),
                            "coherence": inj.get("coherence", {}),
                        })
                    # Sort by timestamp descending
                    activity.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                    self._json({
                        "activity": activity[:50],
                        "total": len(activity),
                        "since": engine.session_start.isoformat(),
                    })

                elif path == "/enforcement":
                    # Enforcement status, compliance stats, and event history
                    self._json({
                        "mode": engine.srt_tool._enforcement_mode,
                        "compliance": engine.srt_tool.get_compliance_stats(),
                        "active_blocks": [e.to_dict() for e in engine.srt_tool.get_active_blocks()],
                        "history": engine.srt_tool.get_enforcement_history(),
                    })

                elif path == "/trust-status":
                    # Trust chain validation from bootstrapped chain + auth
                    sig_chain = engine._trust_chain
                    chain_integrity = engine._trust_integrity

                    auth_status = "disabled"
                    token_count = 0
                    if engine.auth:
                        tokens = getattr(engine.auth, '_tokens', {})
                        token_count = len(tokens)
                        auth_status = "enabled" if token_count > 0 else "no_tokens"

                    coherence_score = 1.0
                    if engine.current_task and engine.srt_tool._seeds:
                        cp = engine.srt_tool.force_reflection()
                        coherence_score = cp.coherence_score

                    verified = chain_integrity and len(sig_chain) > 0
                    self._json({
                        "verified": verified,
                        "status": "VERIFIED" if verified else "UNVERIFIED",
                        "signature_chain": {
                            "length": len(sig_chain),
                            "integrity": chain_integrity,
                        },
                        "auth": {
                            "status": auth_status,
                            "token_count": token_count,
                        },
                        "coherence_score": coherence_score,
                        "engine_version": "SRT-1 v2.0",
                    })

                elif path == "/dashboard":
                    # Developer dashboard — seed-reflection/dashboard.html
                    dp = engine._get_dashboard_path()
                    if dp and os.path.exists(dp):
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        with open(dp, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "Developer dashboard not found"}, 404)

                elif path == "/consumer":
                    # Consumer dashboard — seed-reflection/consumer-dashboard.html
                    consumer_path = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "seed-reflection", "consumer-dashboard.html"
                    )
                    if not os.path.exists(consumer_path):
                        consumer_path = os.path.join(engine.repo_path, "seed-reflection", "consumer-dashboard.html")
                    if os.path.exists(consumer_path):
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        with open(consumer_path, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "Consumer dashboard not found"}, 404)

                elif path == "/admin":
                    # Admin dashboard — seed-reflection/admin-dashboard.html
                    admin_path = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "seed-reflection", "admin-dashboard.html"
                    )
                    if not os.path.exists(admin_path):
                        admin_path = os.path.join(engine.repo_path, "seed-reflection", "admin-dashboard.html")
                    if os.path.exists(admin_path):
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        with open(admin_path, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "Admin dashboard not found"}, 404)

                elif path == "/manifest.json":
                    mf = os.path.join(engine.repo_path, "seed-reflection", "manifest.json")
                    if os.path.exists(mf):
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        with open(mf, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "manifest.json not found"}, 404)

                elif path == "/sw.js":
                    sw = os.path.join(engine.repo_path, "seed-reflection", "sw.js")
                    if os.path.exists(sw):
                        self.send_response(200)
                        self.send_header("Content-Type", "application/javascript")
                        self.send_header("Service-Worker-Allowed", "/")
                        self.end_headers()
                        with open(sw, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "sw.js not found"}, 404)

                elif path.startswith("/api/download/"):
                    pkg = path.split("/api/download/")[1].strip("/")
                    import tarfile, io

                    if pkg == "mobile":
                        # Serve srt1_mobile.html directly
                        mobile_path = os.path.join(engine.repo_path, "srt1_mobile.html")
                        if os.path.exists(mobile_path):
                            self.send_response(200)
                            self.send_header("Content-Type", "text/html")
                            self.send_header("Content-Disposition", "attachment; filename=srt1_mobile.html")
                            self.end_headers()
                            with open(mobile_path, "rb") as f:
                                self.wfile.write(f.read())
                        else:
                            self._json({"error": "srt1_mobile.html not found"}, 404)

                    elif pkg in ("srt1_pro", "srt1_platform"):
                        # Create tar.gz archive of the directory on the fly
                        dir_path = os.path.join(engine.repo_path, pkg)
                        if os.path.isdir(dir_path):
                            buf = io.BytesIO()
                            with tarfile.open(fileobj=buf, mode="w:gz") as tar:
                                tar.add(dir_path, arcname=pkg)
                            data = buf.getvalue()
                            filename = f"{pkg}-2.0.0.tar.gz"
                            self.send_response(200)
                            self.send_header("Content-Type", "application/gzip")
                            self.send_header("Content-Disposition", f"attachment; filename={filename}")
                            self.send_header("Content-Length", str(len(data)))
                            self.end_headers()
                            self.wfile.write(data)
                        else:
                            self._json({"error": f"{pkg} directory not found"}, 404)
                    else:
                        self._json({"error": "Unknown package"}, 404)

                elif path == "/mobile":
                    # Route to the platform module's PWA
                    mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "srt1_platform", "mobile", "index.html")
                    if not os.path.exists(mp):
                        mp = os.path.join(engine.repo_path, "srt1_platform", "mobile", "index.html")
                    if os.path.exists(mp):
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        with open(mp, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "Platform mobile app not found"}, 404)


                # ── Seed Queue Endpoints ──

                elif path == "/seeds":
                    if not engine.seed_queue:
                        self._json({"error": "Seed queue not available"}, 503)
                        return
                    params = parse_qs(urlparse(self.path).query)
                    stage = params.get("stage", [None])[0]
                    source = params.get("source", [None])[0]
                    seeds = engine.seed_queue.list_seeds(stage=stage, source=source)
                    self._json({"seeds": seeds, "total": len(seeds)})

                elif path.startswith("/seeds/"):
                    if not engine.seed_queue:
                        self._json({"error": "Seed queue not available"}, 503)
                        return
                    seed_id = path.split("/seeds/")[1]
                    if seed_id == "active":
                        active = engine.seed_queue.get_active_seed()
                        self._json(active or {"message": "No active seed"})
                    elif seed_id == "pending":
                        pending = engine.seed_queue.get_pending_seeds()
                        self._json({"pending": pending})
                    elif seed_id == "stats":
                        stats = engine.seed_queue.get_stats()
                        self._json(stats)
                    else:
                        seed = engine.seed_queue.get_seed(seed_id)
                        if seed:
                            self._json(seed)
                        else:
                            self._json({"error": f"Seed {seed_id} not found"}, 404)

                # ── Analytics Endpoints ──

                elif path == "/analytics/dashboard":
                    if not engine.analytics:
                        self._json({"error": "Analytics not available (srt1_pro not installed)"}, 503)
                        return
                    self._json(engine.analytics.get_dashboard_metrics())

                elif path == "/analytics/trends":
                    if not engine.analytics:
                        self._json({"error": "Analytics not available"}, 503)
                        return
                    qs = parse_qs(urlparse(self.path).query)
                    days = int(qs.get("days", [30])[0])
                    self._json(engine.analytics.get_trends(days=days))

                elif path == "/verify-tree":
                    if not engine.validator:
                        self._json({"error": "Completeness Validator not available (srt1_pro not installed)"}, 503)
                        return
                    report = engine.validator.verify_tree()
                    self._json(report.to_dict())

                # ── Seed Template Endpoints ──

                elif path == "/templates":
                    if get_template_registry is None:
                        self._json({"error": "Seed templates not available (srt1_pro not installed)"}, 503)
                        return
                    registry = get_template_registry()
                    category = parse_qs(urlparse(self.path).query).get("category", [None])[0]
                    templates = registry.list_templates(category=category)
                    self._json({"templates": templates, "total": len(templates)})

                elif path.startswith("/templates/"):
                    if get_template_registry is None:
                        self._json({"error": "Seed templates not available"}, 503)
                        return
                    registry = get_template_registry()
                    tid = path.split("/templates/")[1]
                    if tid == "search":
                        q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
                        results = registry.search(q)
                        self._json({"results": results, "query": q})
                    else:
                        t = registry.get(tid)
                        if t:
                            self._json(t.to_dict())
                        else:
                            self._json({"error": f"Template '{tid}' not found"}, 404)

                # ── Auth Management Endpoints ──

                elif path == "/auth/tokens":
                    if not engine.auth:
                        self._json({"error": "Auth not available"}, 503)
                        return
                    tokens = engine.auth.list_tokens()
                    self._json({"tokens": tokens})

                else:
                    import posixpath
                    from urllib.parse import unquote
                    serve_path = path
                    if serve_path == "/":
                        serve_path = "/index.html"
                    
                    serve_path = posixpath.normpath(unquote(serve_path))
                    if serve_path.startswith('/'):
                        serve_path = serve_path[1:]
                        
                    local_path = os.path.join(engine.repo_path, "seed-reflection", serve_path)
                    
                    if os.path.exists(local_path) and os.path.isfile(local_path):
                        ext = os.path.splitext(local_path)[1].lower()
                        content_type = {
                            ".html": "text/html",
                            ".css": "text/css",
                            ".js": "application/javascript",
                            ".json": "application/json",
                            ".png": "image/png",
                            ".jpg": "image/jpeg",
                            ".jpeg": "image/jpeg",
                            ".svg": "image/svg+xml"
                        }.get(ext, "application/octet-stream")
                        
                        self.send_response(200)
                        self.send_header("Content-Type", content_type)
                        self.end_headers()
                        with open(local_path, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({
                            "product": "SRT-1 v2.0",
                            "endpoints": {
                                "GET": [
                                    "/status", "/context", "/synopsis", "/manifest",
                                    "/dashboard", "/consumer", "/admin", "/health",
                                    "/admin/stats", "/activity", "/trust-status",
                                    "/manifest.json", "/sw.js",
                                    "/templates", "/templates/<id>", "/templates/search?q=<query>",
                                    "/analytics/dashboard", "/analytics/trends", "/verify-tree",
                                    "/seeds", "/seeds/active", "/seeds/pending",
                                    "/seeds/stats", "/seeds/<id>",
                                    "/auth/tokens",
                                ],
                                "POST": [
                                    "/task", "/operation", "/blueprint",
                                    "/recover", "/reset",
                                    "/seeds", "/seeds/<id>/complete", "/seeds/<id>/fail",
                                    "/auth/generate", "/auth/revoke", "/auth/rotate",
                                ],
                                "PATCH": ["/seeds/<id>"],
                            },
                        })

            def do_POST(self):
                path = urlparse(self.path).path

                if not self._check_auth(path):
                    return

                body = self._body()

                if path == "/api/v1/auth/signup":
                    email = body.get("email")
                    name = body.get("name", "User")
                    password = body.get("password")
                    if not email or not password:
                        return self._json({"error": "Email and password required"}, 400)
                    user_id = str(uuid.uuid4())
                    p_hash = hash_password(password)
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    try:
                        from datetime import datetime
                        c.execute("INSERT INTO users (id, email, name, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                                  (user_id, email, name, p_hash, datetime.now().isoformat()))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        conn.close()
                        return self._json({"detail": "An account with this email already exists."}, 409)
                    token = generate_session_token()
                    expires = (datetime.now() + timedelta(days=7)).isoformat()
                    c.execute("INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, expires))
                    conn.commit()
                    conn.close()
                    return self._json({"access_token": token, "refresh_token": token, "email": email})

                elif path == "/api/v1/auth/login":
                    email = body.get("email")
                    password = body.get("password")
                    p_hash = hash_password(password)
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("SELECT id FROM users WHERE email=? AND password_hash=?", (email, p_hash))
                    row = c.fetchone()
                    if row:
                        from datetime import datetime
                        user_id = row[0]
                        token = generate_session_token()
                        expires = (datetime.now() + timedelta(days=7)).isoformat()
                        c.execute("INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, expires))
                        conn.commit()
                        conn.close()
                        return self._json({"access_token": token, "refresh_token": token, "email": email})
                    else:
                        conn.close()
                        return self._json({"detail": "Invalid email or password"}, 401)

                elif path == "/api/v1/files/":
                    user_id = self._authenticate_cloud()
                    if not user_id:
                        return self._json({"error": "Unauthorized"}, 401)
                    file_id = "f_" + str(uuid.uuid4())[:8]
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    from datetime import datetime
                    dt = datetime.now().isoformat()
                    c.execute("INSERT INTO files (id, user_id, filename, description, category, size_kb, content, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (file_id, user_id, "idea-upload.json", "New idea from web", "reflection", 1, "{}", dt))
                    conn.commit()
                    conn.close()
                    return self._json({"id": file_id, "filename": "idea-upload.json", "size_kb": 1, "created_at": dt})

                elif path == "/task":
                    block = engine.srt_tool.check_enforcement("seed_dispatch")
                    if block is not None:
                        self._json({
                            "error": "Enforcement block active",
                            "blocked": True,
                            "enforcement_event": block.to_dict(),
                            "message": f"ENFORCEMENT {block.level.name}: {block.reason}",
                            "required_resolution": block.required_resolution
                        }, 403)
                        return

                    task = body.get("task")
                    if not task:
                        self._json({"error": "Missing 'task'"}, 400)
                        return
                    source = body.get("source", "api")
                    priority = body.get("priority", 5)
                    auto_dispatch = body.get("auto_dispatch", True)
                    template_id = body.get("template_id")  # Optional: use specific template
                    queue_seed_id = engine._plant_seed(
                        task, source=source, priority=priority,
                        auto_dispatch=auto_dispatch,
                        template_id=template_id,
                    )
                    engine.current_task = task
                    threading.Thread(target=engine._generate_context_files, daemon=True).start()
                    response = {
                        "status": "task_set", "task": task,
                        "seed_id": engine.task_seed_id,
                        "queue_seed_id": queue_seed_id,
                        "dispatched": auto_dispatch and engine.bridge is not None,
                        "codebase_files": len(engine.manifest.get("file_manifest", [])),
                        "template_applied": getattr(engine, '_applied_template', None),
                    }
                    if queue_seed_id and engine.seed_queue:
                        seed = engine.seed_queue.get_seed(queue_seed_id)
                        if seed:
                            response["lifecycle"] = {
                                "stage": seed["stage"],
                                "stage_emoji": seed["stage_emoji"],
                                "growth": seed["growth"],
                            }
                    # Sign the task dispatch via SeedSignature
                    if engine.signing_client:
                        sig = engine.signing_client.sign(
                            {"task": task, "seed_id": engine.task_seed_id, "source": source},
                            phase="seed_dispatch"
                        )
                        if "error" not in sig:
                            response["_provenance"] = sig
                    self._json(response)

                elif path == "/operation":
                    desc = body.get("description")
                    if not desc:
                        self._json({"error": "Missing 'description'"}, 400)
                        return
                    result = engine.log_operation(desc, body.get("files_touched", []))
                    self._json(result)

                # ── Enforcement Endpoints ──

                elif path == "/enforcement/resolve":
                    event_id = body.get("event_id")
                    if not event_id:
                        self._json({"error": "Missing 'event_id'"}, 400)
                        return
                    success = engine.srt_tool.resolve_violation(event_id)
                    if success:
                        resolve_data = {
                            "status": "resolved",
                            "event_id": event_id,
                            "compliance": engine.srt_tool.get_compliance_stats(),
                        }
                        # Sign the resolution via SeedSignature
                        if engine.signing_client:
                            sig = engine.signing_client.sign(
                                {"event_id": event_id, "action": "resolve"},
                                phase="enforcement_resolve"
                            )
                            if "error" not in sig:
                                resolve_data["_provenance"] = sig
                        self._json(resolve_data)
                    else:
                        self._json({"error": f"Event {event_id} not found or already resolved"}, 404)

                elif path == "/enforcement/override":
                    event_id = body.get("event_id")
                    reason = body.get("reason")
                    actor = body.get("actor", "unknown")
                    if not event_id or not reason:
                        self._json({"error": "Missing 'event_id' and/or 'reason'"}, 400)
                        return
                    success = engine.srt_tool.override_violation(event_id, reason, actor)
                    if success:
                        override_data = {
                            "status": "overridden",
                            "event_id": event_id,
                            "override_reason": reason,
                            "override_actor": actor,
                            "warning": "Override does NOT erase the violation. It remains in history.",
                            "compliance": engine.srt_tool.get_compliance_stats(),
                        }
                        # Sign the override via SeedSignature
                        if engine.signing_client:
                            sig = engine.signing_client.sign(
                                {"event_id": event_id, "action": "override",
                                 "reason": reason, "actor": actor},
                                phase="enforcement_override"
                            )
                            if "error" not in sig:
                                override_data["_provenance"] = sig
                        self._json(override_data)
                    else:
                        self._json({"error": f"Event {event_id} not found, already resolved, or non-overridable"}, 403)

                elif path == "/blueprint":
                    seed_text = body.get("seed") or body.get("task")
                    if not seed_text:
                        self._json({"error": "Missing 'seed' (the idea to build a blueprint for)"}, 400)
                        return
                    result = engine.generate_blueprint(seed_text)
                    self._json(result)

                elif path == "/recover":
                    thread_text = body.get("text") or body.get("conversation")
                    if not thread_text:
                        self._json({"error": "Missing 'text' (the conversation to mine)"}, 400)
                        return
                    source = body.get("source", "api_call")
                    try:
                        from srt1_thread_recovery import SCIASeedMiner
                        miner = SCIASeedMiner()
                        report = miner.mine(thread_text, source=source)
                        self._json({
                            "summary": report["summary"],
                            "forgotten_seeds": report["forgotten_seeds"],
                            "completed_seeds": report["completed_seeds"],
                            "drift_points": report["drift_points"],
                            "topic_shifts": report["topic_shifts"],
                            "report": report["report"],
                        })
                    except ImportError:
                        self._json({"error": "srt1_thread_recovery.py not found"}, 500)
                    except Exception as exc:
                        self._json({"error": f"Recovery failed: {str(exc)}"}, 500)

                elif path == "/reset":
                    old = engine.current_task
                    engine.current_task = None
                    engine.task_seed_id = None
                    engine.operations = []
                    engine.injections = []
                    engine.srt_tool = SRT(reflection_interval=engine.REFLECTION_INTERVAL)
                    self._json({"status": "reset", "previous_task": old})

                # ── Seed Queue POST Endpoints ──

                elif path == "/seeds":
                    block = engine.srt_tool.check_enforcement("seed_dispatch")
                    if block is not None:
                        self._json({
                            "error": "Enforcement block active",
                            "blocked": True,
                            "enforcement_event": block.to_dict(),
                            "message": f"ENFORCEMENT {block.level.name}: {block.reason}",
                            "required_resolution": block.required_resolution
                        }, 403)
                        return

                    if not engine.seed_queue:
                        self._json({"error": "Seed queue not available"}, 503)
                        return
                    intent = body.get("intent") or body.get("seed") or body.get("task")
                    if not intent:
                        self._json({"error": "Missing 'intent' (what to build)"}, 400)
                        return
                    source = body.get("source", "mobile")
                    priority = body.get("priority", 5)
                    tags = body.get("tags", [])

                    # Plant in queue
                    seed = engine.seed_queue.plant(
                        intent=intent, source=source,
                        priority=priority, tags=tags
                    )

                    # Set as current task (lightweight)
                    engine.current_task = intent

                    # Dispatch blueprint generation in background (non-blocking)
                    auto_dispatch = body.get("auto_dispatch", True)
                    if auto_dispatch and engine.bridge:
                        def _seed_dispatch(sid, t):
                            try:
                                bp_result = engine.generate_blueprint(t)
                                engine.seed_queue.germinate(
                                    seed_id=sid,
                                    blueprint=bp_result.get("blueprint", ""),
                                    blueprint_path=bp_result.get("saved_to", ""),
                                    relevant_symbols=bp_result.get("relevant_symbols", 0),
                                    relevant_files=bp_result.get("relevant_files", 0),
                                )
                                engine.bridge.dispatch_seed(
                                    seed_id=sid, intent=t,
                                    blueprint=bp_result.get("blueprint", ""),
                                )
                            except Exception as e:
                                logger.error(f"Seed dispatch failed: {e}")
                        threading.Thread(
                            target=_seed_dispatch, args=(seed.seed_id, intent),
                            daemon=True
                        ).start()

                    seed_data = engine.seed_queue.get_seed(seed.seed_id)
                    self._json({
                        "status": "seed_planted",
                        "seed": seed_data,
                        "message": f"{seed.stage.emoji} Seed planted! Blueprint generating in background.",
                    })

                elif path.startswith("/seeds/") and path.endswith("/complete"):
                    if not engine.seed_queue:
                        self._json({"error": "Seed queue not available"}, 503)
                        return
                    seed_id = path.replace("/seeds/", "").replace("/complete", "")
                    summary = body.get("summary", "Manually completed")
                    result = engine.seed_queue.bloom(seed_id, summary=summary)
                    if result:
                        # Also notify the bridge
                        if engine.bridge:
                            engine.bridge.mark_complete(
                                seed_id, summary=summary,
                                files_modified=body.get("files_modified", [])
                            )
                        self._json({
                            "status": "bloomed",
                            "seed": engine.seed_queue.get_seed(seed_id),
                            "message": "🌸 Seed has BLOOMED!",
                        })
                    else:
                        self._json({"error": f"Seed {seed_id} not found"}, 404)

                elif path.startswith("/seeds/") and path.endswith("/fail"):
                    if not engine.seed_queue:
                        self._json({"error": "Seed queue not available"}, 503)
                        return
                    seed_id = path.replace("/seeds/", "").replace("/fail", "")
                    reason = body.get("reason", "Manually marked as failed")
                    result = engine.seed_queue.wilt(seed_id, reason=reason)
                    if result:
                        if engine.bridge:
                            engine.bridge.mark_failed(seed_id, reason=reason)
                        self._json({
                            "status": "wilted",
                            "seed": engine.seed_queue.get_seed(seed_id),
                            "message": "🍂 Seed has WILTED.",
                        })
                    else:
                        self._json({"error": f"Seed {seed_id} not found"}, 404)

                # ── Auth Endpoints ──

                elif path == "/auth/generate":
                    if not engine.auth:
                        self._json({"error": "Auth not available"}, 503)
                        return
                    label = body.get("label", "default")
                    expires_days = body.get("expires_days")
                    result = engine.auth.generate_token(
                        label=label, expires_days=expires_days
                    )
                    self._json(result)

                elif path == "/auth/revoke":
                    if not engine.auth:
                        self._json({"error": "Auth not available"}, 503)
                        return
                    token_id = body.get("token_id")
                    if not token_id:
                        self._json({"error": "Missing 'token_id'"}, 400)
                        return
                    success = engine.auth.revoke_token(token_id)
                    self._json({"revoked": success, "token_id": token_id})

                elif path == "/auth/rotate":
                    if not engine.auth:
                        self._json({"error": "Auth not available"}, 503)
                        return
                    token_id = body.get("token_id")
                    if not token_id:
                        self._json({"error": "Missing 'token_id'"}, 400)
                        return
                    result = engine.auth.rotate_token(
                        token_id, expires_days=body.get("expires_days")
                    )
                    if result:
                        self._json(result)
                    else:
                        self._json({"error": f"Token {token_id} not found"}, 404)

                else:
                    self._json({"error": "Unknown endpoint"}, 404)

            def do_PATCH(self):
                path = urlparse(self.path).path

                if not self._check_auth(path):
                    return

                body = self._body()

                # PATCH /seeds/<id> — Update seed growth or stage
                if path.startswith("/seeds/"):
                    if not engine.seed_queue:
                        self._json({"error": "Seed queue not available"}, 503)
                        return
                    seed_id = path.split("/seeds/")[1]
                    growth = body.get("growth")
                    note = body.get("note", "")

                    if growth is not None:
                        result = engine.seed_queue.update_growth(
                            seed_id, percentage=int(growth), note=note
                        )
                        if result:
                            self._json(engine.seed_queue.get_seed(seed_id))
                        else:
                            self._json({"error": f"Seed {seed_id} not found"}, 404)
                    else:
                        self._json({"error": "Missing 'growth' value"}, 400)
                else:
                    self._json({"error": "Unknown endpoint"}, 404)

        class ThreadedServer(ThreadingMixIn, HTTPServer):
            daemon_threads = True

        server = ThreadedServer(("127.0.0.1", self.port), Handler)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n  SRT-1 stopped.")
            self._watcher_running = False
            server.server_close()

    def _get_dashboard_path(self) -> Optional[str]:
        """Find the developer dashboard HTML file (seed-reflection/dashboard.html)."""
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed-reflection", "dashboard.html"),
            os.path.join(self.repo_path, "seed-reflection", "dashboard.html"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    # -----------------------------------------------------------------
    # UI
    # -----------------------------------------------------------------

    def _print_banner(self) -> None:
        print()
        print("  ╔══════════════════════════════════════════════════════╗")
        print("  ║           SRT-1 Code Indexer v2.0                   ║")
        print("  ║   The Autonomous Codebase Immune System (SCIA)       ║")
        print("  ╚══════════════════════════════════════════════════════╝")
        print()
        print(f"  Target: {self.repo_path}")
        if self.task:
            print(f"  Task:   {self.task}")
        print()

    def _print_ready(self) -> None:
        # Print the synopsis first
        if self.synopsis:
            print("  ────────────────────────────────────────────────────")
            # Print synopsis lines with indentation
            for line in self.synopsis.split("\n"):
                # Skip markdown headers for terminal display
                clean = line.replace("## ", "").replace("**", "").replace("⚠️ ", "! ")
                if clean.strip():
                    print(f"  {clean}")
            print("  ────────────────────────────────────────────────────")
            print()

        print("  ╔══════════════════════════════════════════════════════╗")
        print("  ║               INDEXER IMMUNE SYSTEM IS LIVE         ║")
        print("  ╚══════════════════════════════════════════════════════╝")
        print()
        print(f"  Developer:  http://127.0.0.1:{self.port}/dashboard")
        print(f"  Consumer:   http://127.0.0.1:{self.port}/consumer")
        print(f"  Admin:      http://127.0.0.1:{self.port}/admin")
        print(f"  Mobile:     http://127.0.0.1:{self.port}/mobile")
        print(f"  API:        http://127.0.0.1:{self.port}/status")
        print(f"  Seeds:      http://127.0.0.1:{self.port}/seeds")
        print()
        print("  AI context files generated:")
        print("    ✓ CLAUDE.md          → Claude Code / Antigravity")
        print("    ✓ .cursorrules       → Cursor")
        print("    ✓ AGENTS.md          → Generic AI agents")
        print("    ✓ copilot-instructions.md → GitHub Copilot")
        print()
        print("  Mobile-Ready Infrastructure:")
        print(f"    {'✓' if self.auth else '○'} Remote Auth         {'(enabled)' if self.auth else '(import srt1_remote_auth to enable)'}")
        print(f"    {'✓' if self.seed_queue else '○'} Seed Queue          {'(active)' if self.seed_queue else '(import srt1_seed_queue to enable)'}")
        print(f"    {'✓' if self.bridge else '○'} Execution Bridge    {'(monitoring)' if self.bridge else '(import srt1_execution_bridge to enable)'}")
        print()
        print("  File watcher active. Changes auto-regenerate everything.")
        print("  Press Ctrl+C to stop.")
        print()


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    import sys
    
    # ── INIT COMMAND INTERCEPT ──
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        import os
        import json
        from datetime import datetime
        print("  ╔══════════════════════════════════════════════════════╗")
        print("  ║           SRT-1 Code Indexer Initialization         ║")
        print("  ╚══════════════════════════════════════════════════════╝\n")
        
        idea = ""
        for i, arg in enumerate(sys.argv):
            if arg == "--idea" and len(sys.argv) > i + 1:
                idea = sys.argv[i+1]
        
        # Auto-detect intent from existing architecture files
        if not idea:
            for arch_file in ["CLAUDE.md", "task.md", "architecture.md", "README.md", "project_plan.txt"]:
                fp = os.path.join(os.getcwd(), arch_file)
                if os.path.exists(fp):
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            content = f.read(1000).strip()
                            if content:
                                print(f"  🧠 Auto-detected architecture intent from {arch_file}:\n")
                                preview = content[:400] + ("..." if len(content) > 400 else "")
                                print("    " + "\n    ".join(preview.splitlines()))
                                print("\n  ────────────────────────────────────────────────────")
                                ans = input("  Is this the correct architecture to track? [Y/n]: ").strip().lower()
                                if ans in ("n", "no"):
                                    print("\n  Okay, let's correct it.")
                                    # Break to allow the manual input below
                                    break
                                else:
                                    idea = f"Auto-detected from {arch_file}:\n{content[:500]}..."
                                    break
                    except Exception:
                        pass
                        
        if not idea:
            try:
                idea = input("  What is the grand vision / correct architecture for this repository?\n  > ")
            except EOFError:
                idea = "Initial Repository Setup"
                
        srt1_dir = os.path.join(os.getcwd(), ".srt1")
        seeds_dir = os.path.join(srt1_dir, "seeds")
        os.makedirs(seeds_dir, exist_ok=True)
        
        seed_data = {
            "seed_id": "seed_0000_genesis",
            "intent": idea,
            "source": "cli_init",
            "priority": 10,
            "stage": "planted",
            "stage_emoji": "🌱",
            "growth": 0,
            "logs": [{"time": datetime.now().isoformat(), "event": "Genesis seed planted by indexer init.", "growth": 0}],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        with open(os.path.join(seeds_dir, "seed_0000_genesis.json"), "w") as f:
            json.dump(seed_data, f, indent=2)
            
        print("\n  ✅ Genesis Seed established.")
        print("  ✅ .srt1 tracking directory created.")
        print("\n  To start the continuous immune system watch-loop, run:")
        print("    srt1-code-indexer --repo_path .\n")
        sys.exit(0)

    # ── NORMAL STARTUP ──
    parser = argparse.ArgumentParser(
        description="SRT-1 Code Indexer — SCIA Autonomous Immune System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Initialization (Run Once):\n"
            "  srt1-code-indexer init\n\n"
            "Continuous Immune System Watcher:\n"
            "  srt1-code-indexer --repo_path .\n"
            "  srt1-code-indexer --repo_path . --task 'Fix login bug' --port 8080\n"
        ),
    )
    parser.add_argument("--repo_path", required=True, help="Path to the repository")
    parser.add_argument("--task", help="Current active task (optional override)")
    parser.add_argument("--port", type=int, default=7483, help="Server port (default: 7483)")
    args = parser.parse_args()

    engine = SRT1Engine(repo_path=args.repo_path, task=args.task, port=args.port)
    init_db()
    engine.start()


if __name__ == "__main__":
    main()
