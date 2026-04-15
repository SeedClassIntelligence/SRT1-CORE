#!/usr/bin/env python3
"""
SRT-1 Live Middleware — Real-Time Anti-Hallucination Engine for AI Code Assistants

FILE: srt1_middleware.py
SRT-1 TAG: LIVE_MIDDLEWARE :: REAL_TIME_GUARDRAIL

PURPOSE:
    A persistent local service that sits between the developer and ANY AI code
    assistant. It knows the entire codebase, tracks the developer's current task,
    and every 2-3 operations injects a reflection checkpoint back into the AI —
    reminding it what exists, what the task is, and what NOT to do.

    This is NOT a one-shot report. This is a LIVE, CONTINUOUS, REAL-TIME system.

HOW IT WORKS:
    1. Developer starts the middleware:  srt1-middleware --repo_path ./my_project
    2. SRT-1 indexes the entire codebase (knows what every function does)
    3. Developer sets a task:  POST /task  {"task": "Add refund notification emails"}
    4. As the AI works, operations are logged:  POST /operation  {"description": "..."}
    5. Every 2-3 operations, SRT-1 generates an INJECTION — a context block that
       tells the AI: "Here's what exists.  Here's your task.  Stay on it."
    6. If files change, SRT-1 re-indexes automatically (file watcher)

ENDPOINTS:
    POST /task              — Plant a seed (set current task intent)
    POST /operation         — Log an AI operation, get injection if checkpoint fires
    GET  /context           — Get full context bundle for the AI right now
    GET  /context/relevant  — Get context relevant to specific files being touched
    GET  /status            — Coherence score, drift status, operation count
    GET  /manifest          — Full codebase manifest
    POST /reset             — Reset the session (new task, clear operations)

INTEGRATION:
    Any AI tool can call these endpoints. The middleware is AI-agnostic.
    - Claude: call /context before each response
    - Copilot: call /operation after each suggestion
    - Custom tools: call /context/relevant with the files being edited

Author : William Darnell Jernigan IV (Architect)
License: Apache License 2.0
"""

import os
import sys
import json
import time
import hashlib
import logging
import threading
import argparse
import ssl
import subprocess
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse, parse_qs

# ---- Import Core SCIA IP ----
try:
    from srt1_code_indexer.srt import SRT
    from srt1_code_indexer.indexer import SRT1CodeIndexer
except ImportError:
    try:
        from srt import SRT
        from srt1_code_indexer import SRT1CodeIndexer
    except ImportError:
        sys.exit(
            "[FATAL] Cannot import SCIA core modules.\n"
            "Ensure srt.py and srt1_code_indexer.py "
            "are available."
        )

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SRT-1] %(message)s")
logger = logging.getLogger("srt1_middleware")


# =============================================================================
# LIVE CONTEXT ENGINE
# =============================================================================

class SCIALiveEngine:
    """
    The real-time brain. Knows the codebase, tracks the task, fires
    checkpoints, and generates context injections for AI code assistants.
    """

    def __init__(self, repo_path: str, reflection_interval: int = 3):
        self.repo_path = os.path.abspath(repo_path)
        self.reflection_interval = reflection_interval

        # ---- Core SCIA IP ----
        self.srt_tool = SRT(reflection_interval=reflection_interval)

        # ---- Codebase Knowledge ----
        self.manifest: Dict[str, Any] = {}
        self.symbol_table: Dict[str, List[Dict[str, Any]]] = {}
        self.curation_report: Dict[str, Any] = {}
        self.file_hashes: Dict[str, str] = {}  # path -> hash, for change detection
        self._lock = threading.Lock()  # Prevent concurrent re-indexing

        # ---- Session State ----
        self.current_task: Optional[str] = None
        self.task_seed_id: Optional[str] = None
        self.operations: List[Dict[str, Any]] = []
        self.injections: List[Dict[str, Any]] = []
        self.session_start = datetime.now()

        # ---- Initial Index ----
        self._index_codebase()

        # ---- File Watcher (background thread) ----
        self._watcher_running = True
        self._watcher_thread = threading.Thread(
            target=self._watch_for_changes, daemon=True
        )
        self._watcher_thread.start()

        logger.info(f"Live engine initialized. Watching: {self.repo_path}")
        logger.info(
            f"Codebase: {len(self.manifest.get('file_manifest', []))} files, "
            f"{sum(len(s) for s in self.symbol_table.values())} symbols"
        )

    # -----------------------------------------------------------------
    # CODEBASE INDEXING
    # -----------------------------------------------------------------

    def _index_codebase(self) -> None:
        """Run the full SRT-1 Code Indexer and load results."""
        with self._lock:
            try:
                indexer = SRT1CodeIndexer(self.repo_path)
                self.manifest = indexer.index_repository()
                self.symbol_table = indexer.symbol_table
                self.curation_report = indexer.curation_report

                # Cache file hashes for change detection
                for entry in indexer.file_manifest:
                    self.file_hashes[entry["file_path"]] = entry["content_hash"]

                logger.info("Codebase indexed successfully.")
            except Exception as exc:
                logger.error(f"Indexing failed: {exc}")

    def _reindex_if_changed(self) -> bool:
        """Check if any files changed and re-index if so."""
        changed = False

        for entry in self.manifest.get("file_manifest", []):
            fpath = entry.get("file_path", "")
            full_path = os.path.join(self.repo_path, fpath)

            if not os.path.exists(full_path):
                continue

            try:
                with open(full_path, "rb") as f:
                    current_hash = hashlib.sha256(f.read()).hexdigest()
                if current_hash != self.file_hashes.get(fpath):
                    changed = True
                    break
            except (OSError, PermissionError):
                continue

        if changed:
            logger.info("File changes detected — re-indexing...")
            self._index_codebase()
            return True
        return False

    def _watch_for_changes(self) -> None:
        """Background thread: poll for file changes every 15 seconds."""
        while self._watcher_running:
            time.sleep(15)
            try:
                self._reindex_if_changed()
            except Exception as exc:
                logger.error(f"Watcher error: {exc}")

    # -----------------------------------------------------------------
    # TASK MANAGEMENT (Seed Planting)
    # -----------------------------------------------------------------

    def set_task(self, task: str, context: Optional[Dict] = None,
                 template_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Plant a seed — set the developer's current task intent.
        Everything from this point is measured against this seed.

        If template_id is provided, uses that template. Otherwise,
        auto-detects the best matching template for higher coherence.
        """
        self.current_task = task
        self.operations = []
        self.injections = []

        # Plant the seed in SRT (template-aware)
        self.srt_tool = SRT(reflection_interval=self.reflection_interval)

        applied_template = None
        try:
            from srt1_pro.seed_templates import get_registry
            registry = get_registry()
            # Load user templates
            user_tpl_dir = os.path.join(self.repo_path, ".srt1", "templates")
            registry.load_user_templates(user_tpl_dir)

            if template_id:
                try:
                    registry.plant_from_template(
                        template_id=template_id,
                        task=task,
                        srt_tool=self.srt_tool,
                    )
                    applied_template = template_id
                except ValueError:
                    pass  # Fall through to auto-detect

            if not applied_template:
                seed, detected_id = registry.plant_auto(
                    task=task,
                    srt_tool=self.srt_tool,
                )
                applied_template = detected_id
        except ImportError:
            # srt1_pro not available — plant plain seed
            self.srt_tool.plant_seed(
                task=task,
                domain="code_development",
                keywords=self._extract_task_keywords(task),
                metadata={
                    "repo_path": self.repo_path,
                    "set_at": datetime.now().isoformat(),
                    **(context or {}),
                },
            )

        self.task_seed_id = (
            self.srt_tool._seeds[-1].seed_id if self.srt_tool._seeds else None
        )

        logger.info(f"Task seed planted: {task}" +
                     (f" (template: {applied_template})" if applied_template else ""))

        return {
            "status": "task_set",
            "task": task,
            "seed_id": self.task_seed_id,
            "template_applied": applied_template,
            "codebase_files": len(self.manifest.get("file_manifest", [])),
            "codebase_symbols": sum(len(s) for s in self.symbol_table.values()),
            "curation_warnings": (
                len(self.curation_report.get("duplicate_files", []))
                + len(self.curation_report.get("functional_overlaps", []))
            ),
            "message": (
                f"SRT-1 is now tracking your task. "
                f"Reflection checkpoints will fire every {self.reflection_interval} operations. "
                f"Call POST /operation after each AI action."
            ),
        }

    def _extract_task_keywords(self, task: str) -> List[str]:
        """Extract relevant keywords from the task description."""
        # Common noise words to filter out
        noise = {
            "a", "an", "the", "to", "in", "on", "at", "for", "of", "and",
            "or", "is", "it", "my", "i", "we", "do", "add", "make", "create",
            "build", "implement", "that", "this", "with", "from", "into",
            "should", "need", "want", "please", "can", "you",
        }
        words = task.lower().replace(",", " ").replace(".", " ").split()
        keywords = [w for w in words if w not in noise and len(w) > 2]

        # Always include core pipeline terms for coherence
        keywords.extend([
            "code", "development", "task", "repository", "function",
            "implement", "modify", "update",
        ])
        return list(set(keywords))

    # -----------------------------------------------------------------
    # OPERATION TRACKING & INJECTION
    # -----------------------------------------------------------------

    def log_operation(
        self, description: str, files_touched: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Log an AI operation. If the reflection checkpoint fires,
        generate and return an injection directive.
        """
        op_number = len(self.operations) + 1
        files_touched = files_touched or []

        operation = {
            "op_number": op_number,
            "description": description,
            "files_touched": files_touched,
            "timestamp": datetime.now().isoformat(),
        }
        self.operations.append(operation)

        # Trace through SRT
        self.srt_tool.trace_operation(
            module="ai_assistant",
            operation=description[:100],
            input_data={"files": files_touched, "op": op_number},
            output_data={"logged": True},
            metadata={
                "context": " ".join(
                    self._extract_task_keywords(self.current_task or "")
                ),
            },
        )

        # Check if we need to inject
        should_inject = (op_number % self.reflection_interval) == 0

        result: Dict[str, Any] = {
            "op_number": op_number,
            "logged": True,
            "injection": None,
        }

        if should_inject:
            injection = self._generate_injection(operation)
            self.injections.append(injection)
            result["injection"] = injection
            result["message"] = (
                f"REFLECTION CHECKPOINT #{len(self.injections)}: "
                f"Injection generated. Feed this to the AI."
            )
            logger.info(
                f"Checkpoint #{len(self.injections)} fired at op #{op_number}"
            )
        else:
            ops_until = self.reflection_interval - (op_number % self.reflection_interval)
            result["message"] = f"Logged. Next checkpoint in {ops_until} operation(s)."

        return result

    def _generate_injection(self, trigger_op: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a context injection — the directive that gets pushed
        back into the AI's context to keep it on task.
        """
        # Force a reflection checkpoint
        checkpoint = self.srt_tool.force_reflection()

        # Get relevant symbols for files being touched
        relevant_context = []
        for fpath in trigger_op.get("files_touched", []):
            symbols = self.symbol_table.get(fpath, [])
            for sym in symbols:
                ref = sym.get("reflection", {})
                relevant_context.append({
                    "file": fpath,
                    "symbol": sym["name"],
                    "type": sym["type"],
                    "line": sym["line"],
                    "purpose": ref.get("purpose", "Unknown"),
                    "role": ref.get("architectural_role", "GENERAL"),
                    "risk": ref.get("risk_profile", []),
                    "dependencies": sym.get("dependencies", []),
                })

        # Get curation warnings
        warnings = self._get_active_warnings(trigger_op.get("files_touched", []))

        # Build the injection
        injection = {
            "injection_id": f"inj_{len(self.injections) + 1}",
            "timestamp": datetime.now().isoformat(),
            "coherence": {
                "score": checkpoint.coherence_score,
                "status": checkpoint.coherence_status.value,
                "operations_since_start": len(self.operations),
            },
            "task_reminder": {
                "original_task": self.current_task,
                "seed_id": self.task_seed_id,
                "message": (
                    f"REMINDER: Your task is: '{self.current_task}'. "
                    f"Stay focused on this. Do not drift."
                ),
            },
            "codebase_context": relevant_context,
            "warnings": warnings,
            "directive": self._build_directive(checkpoint, relevant_context, warnings),
        }

        return injection

    def _build_directive(
        self,
        checkpoint,
        relevant_context: List[Dict],
        warnings: List[str],
    ) -> str:
        """
        Build a human-readable directive string that can be injected
        directly into the AI's prompt/context.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("SRT-1 REFLECTION CHECKPOINT — LIVE INJECTION")
        lines.append("=" * 60)
        lines.append("")

        # Task reminder
        lines.append(f"ACTIVE TASK: {self.current_task}")
        lines.append(
            f"COHERENCE: {checkpoint.coherence_status.value} "
            f"({checkpoint.coherence_score:.0%})"
        )
        lines.append(
            f"OPERATIONS COMPLETED: {len(self.operations)}"
        )
        lines.append("")

        # What exists (relevant to current work)
        if relevant_context:
            lines.append("RELEVANT CODE THAT ALREADY EXISTS:")
            for ctx in relevant_context:
                risk_str = ", ".join(ctx["risk"]) if ctx["risk"] else "LOW_RISK"
                deps_str = ", ".join(ctx["dependencies"][:5])
                if len(ctx["dependencies"]) > 5:
                    deps_str += f" (+{len(ctx['dependencies']) - 5} more)"
                lines.append(
                    f"  - {ctx['symbol']} ({ctx['type']}) in {ctx['file']}:{ctx['line']}"
                )
                lines.append(f"    Purpose: {ctx['purpose']}")
                lines.append(f"    Role: {ctx['role']} | Risk: {risk_str}")
                if deps_str:
                    lines.append(f"    Calls: {deps_str}")
            lines.append("")

        # Warnings
        if warnings:
            lines.append("⚠ WARNINGS — DO NOT IGNORE:")
            for w in warnings:
                lines.append(f"  - {w}")
            lines.append("")

        # Directive
        lines.append("DIRECTIVE:")
        if checkpoint.coherence_score < 0.5:
            lines.append(
                "  You have DRIFTED from the original task. STOP what you are "
                "doing and return to the task described above. Do not create "
                "new functionality that was not requested."
            )
        elif checkpoint.coherence_score < 0.8:
            lines.append(
                "  Minor drift detected. Stay focused on the active task. "
                "Review the existing code above before making changes."
            )
        else:
            lines.append(
                "  On track. Continue with the active task. Use existing "
                "functions where possible."
            )

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _get_active_warnings(self, files_touched: List[str]) -> List[str]:
        """Generate warnings relevant to the current operation."""
        warnings: List[str] = []

        # Warn about duplicate functions the AI might recreate
        for overlap in self.curation_report.get("functional_overlaps", []):
            func_name = overlap["instances"][0]["function"]
            canonical = overlap.get("canonical", "")
            warnings.append(
                f"'{func_name}' already exists at {canonical}. "
                f"Do NOT create a new version."
            )

        # Warn about duplicate files
        for dup in self.curation_report.get("duplicate_files", []):
            canonical = dup.get("canonical", "")
            warnings.append(
                f"Duplicate files detected. Use '{canonical}' as canonical."
            )

        # Warn about high-risk functions in touched files
        for fpath in files_touched:
            for sym in self.symbol_table.get(fpath, []):
                ref = sym.get("reflection", {})
                risk = ref.get("risk_profile", [])
                if "AUTH_SENSITIVE" in risk or "WRITES_TO_DB" in risk:
                    warnings.append(
                        f"CAUTION: {sym['name']} in {fpath} is "
                        f"{', '.join(risk)}. Modify with care."
                    )

        return warnings

    # -----------------------------------------------------------------
    # CONTEXT BUNDLE GENERATION
    # -----------------------------------------------------------------

    def get_full_context(self) -> Dict[str, Any]:
        """
        Get the complete context bundle — everything the AI needs to
        know about the codebase and the current task, right now.
        """
        # Build codebase summary
        codebase_summary = {}
        for fpath, symbols in self.symbol_table.items():
            file_summary = []
            for sym in symbols:
                ref = sym.get("reflection", {})
                file_summary.append({
                    "name": sym["name"],
                    "type": sym["type"],
                    "line": sym["line"],
                    "purpose": ref.get("purpose", "Unknown"),
                    "role": ref.get("architectural_role", "GENERAL"),
                    "risk": ref.get("risk_profile", []),
                    "dependencies": sym.get("dependencies", []),
                    "parameters": sym.get("parameters", []),
                })
            codebase_summary[fpath] = file_summary

        context = {
            "srt1_version": "2.0.0",
            "generated_at": datetime.now().isoformat(),
            "task": {
                "description": self.current_task,
                "seed_id": self.task_seed_id,
                "operations_completed": len(self.operations),
                "injections_fired": len(self.injections),
            },
            "codebase": {
                "repo_name": os.path.basename(self.repo_path),
                "total_files": len(self.manifest.get("file_manifest", [])),
                "total_symbols": sum(len(s) for s in self.symbol_table.values()),
                "files": codebase_summary,
            },
            "curation_warnings": self._get_active_warnings([]),
            "coherence": None,
        }

        # Include coherence if task is active
        if self.current_task and self.srt_tool._seeds:
            checkpoint = self.srt_tool.force_reflection()
            context["coherence"] = {
                "score": checkpoint.coherence_score,
                "status": checkpoint.coherence_status.value,
            }

        return context

    def get_relevant_context(self, files: List[str]) -> Dict[str, Any]:
        """Get context relevant to specific files being edited."""
        relevant = {}
        for fpath in files:
            symbols = self.symbol_table.get(fpath, [])
            if symbols:
                relevant[fpath] = [
                    {
                        "name": s["name"],
                        "type": s["type"],
                        "line": s["line"],
                        "purpose": s.get("reflection", {}).get("purpose", "Unknown"),
                        "role": s.get("reflection", {}).get("architectural_role", "GENERAL"),
                        "risk": s.get("reflection", {}).get("risk_profile", []),
                        "dependencies": s.get("dependencies", []),
                    }
                    for s in symbols
                ]

        return {
            "task": self.current_task,
            "files_requested": files,
            "context": relevant,
            "warnings": self._get_active_warnings(files),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current middleware status."""
        coherence = None
        if self.current_task and self.srt_tool._seeds:
            checkpoint = self.srt_tool.force_reflection()
            coherence = {
                "score": checkpoint.coherence_score,
                "status": checkpoint.coherence_status.value,
            }

        return {
            "middleware": "SRT-1 Live Middleware v2.0",
            "repo": os.path.basename(self.repo_path),
            "uptime_seconds": (datetime.now() - self.session_start).total_seconds(),
            "task": self.current_task,
            "operations_logged": len(self.operations),
            "injections_fired": len(self.injections),
            "codebase_files": len(self.manifest.get("file_manifest", [])),
            "codebase_symbols": sum(len(s) for s in self.symbol_table.values()),
            "coherence": coherence,
            "watcher": "active",
        }

    def reset_session(self) -> Dict[str, Any]:
        """Reset the session — clear task, operations, start fresh."""
        old_task = self.current_task
        self.current_task = None
        self.task_seed_id = None
        self.operations = []
        self.injections = []
        self.srt_tool = SRT(reflection_interval=self.reflection_interval)
        self.session_start = datetime.now()

        logger.info(f"Session reset. Previous task: {old_task}")
        return {"status": "reset", "previous_task": old_task}


# =============================================================================
# HTTP SERVER — Any AI tool can call these endpoints
# =============================================================================

class SRT1RequestHandler(BaseHTTPRequestHandler):
    """HTTP handler for the live middleware API."""

    engine: SCIALiveEngine  # Set by the server

    def log_message(self, fmt, *args):
        """Suppress default HTTP logs — we use our own logger."""
        pass

    def _send_json(self, data: Dict, status: int = 200) -> None:
        """Send a JSON response."""
        body = json.dumps(data, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> Dict:
        """Read and parse JSON request body."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path

        if path == "/status":
            self._send_json(self.engine.get_status())

        elif path == "/context":
            self._send_json(self.engine.get_full_context())

        elif path == "/context/relevant":
            params = parse_qs(urlparse(self.path).query)
            files = params.get("files", [])
            if files:
                files = files[0].split(",")
            self._send_json(self.engine.get_relevant_context(files))

        elif path == "/manifest":
            self._send_json(self.engine.manifest)

        elif path == "/health":
            self._send_json({"status": "healthy", "middleware": "SRT-1 v2.0"})

        else:
            self._send_json(
                {
                    "error": "Unknown endpoint",
                    "available": {
                        "GET": ["/status", "/context", "/context/relevant?files=a.py,b.py", "/manifest", "/health"],
                        "POST": ["/task", "/operation", "/reset"],
                    },
                },
                404,
            )

    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/task":
            task = body.get("task")
            if not task:
                self._send_json({"error": "Missing 'task' in request body"}, 400)
                return
            result = self.engine.set_task(task, context=body.get("context"))
            self._send_json(result)

        elif path == "/operation":
            desc = body.get("description")
            if not desc:
                self._send_json({"error": "Missing 'description' in request body"}, 400)
                return
            files = body.get("files_touched", [])
            result = self.engine.log_operation(desc, files_touched=files)
            self._send_json(result)

        elif path == "/reset":
            result = self.engine.reset_session()
            self._send_json(result)

        else:
            self._send_json({"error": "Unknown endpoint"}, 404)


# =============================================================================
# CLI & SERVER STARTUP
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SRT-1 Live Middleware — Real-Time Anti-Hallucination Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Start the middleware:\n"
            "  python srt1_middleware.py --repo_path ./my_project\n\n"
            "Then use the API:\n"
            "  curl -X POST http://localhost:7483/task -d '{\"task\": \"Add user logout\"}'\n"
            "  curl -X POST http://localhost:7483/operation -d '{\"description\": \"Created logout route\"}'\n"
            "  curl http://localhost:7483/status\n"
            "  curl http://localhost:7483/context\n"
        ),
    )
    parser.add_argument("--repo_path", required=True, help="Path to the repository")
    parser.add_argument("--port", type=int, default=7483, help="Port (default: 7483)")
    parser.add_argument("--interval", type=int, default=3, help="Reflection interval (default: 3)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--tls-cert", dest="tls_cert", default=None,
                        help="Path to TLS certificate file (.pem). If omitted with --tls, a self-signed cert is auto-generated.")
    parser.add_argument("--tls-key", dest="tls_key", default=None,
                        help="Path to TLS private key file (.pem).")
    parser.add_argument("--tls", action="store_true",
                        help="Enable TLS/HTTPS. Auto-generates a self-signed cert if --tls-cert is not provided.")
    args = parser.parse_args()

    # Determine TLS mode
    use_tls = args.tls or (args.tls_cert is not None)
    _tmp_cert_dir = None  # track temp dir for cleanup

    if use_tls and not args.tls_cert:
        # Auto-generate a self-signed certificate (requires openssl on PATH)
        _tmp_cert_dir = tempfile.mkdtemp(prefix="srt1_tls_")
        args.tls_cert = os.path.join(_tmp_cert_dir, "server.crt")
        args.tls_key = os.path.join(_tmp_cert_dir, "server.key")
        try:
            subprocess.run(
                [
                    "openssl", "req", "-x509", "-newkey", "rsa:2048",
                    "-keyout", args.tls_key,
                    "-out", args.tls_cert,
                    "-days", "365",
                    "-nodes",
                    "-subj", "/CN=srt1-middleware/O=SCIA/C=US",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            sys.exit(
                f"[FATAL] Could not auto-generate TLS certificate: {exc}\n"
                "Install openssl or supply --tls-cert / --tls-key explicitly."
            )

    if use_tls and args.host == "127.0.0.1":
        # Warn when TLS is enabled but still bound to loopback — common dev scenario
        print()
        print("  ⚠  WARNING: TLS enabled but binding to 127.0.0.1 (loopback only).")
        print("     To accept remote connections use --host 0.0.0.0")

    if not use_tls and args.host != "127.0.0.1":
        # Warn loudly when exposed without TLS
        print()
        print("  ⚠  WARNING: No TLS and binding to a non-loopback address!")
        print("     All traffic is unencrypted. Use --tls to enable HTTPS.")

    # Initialize the live engine
    print()
    print("=" * 60)
    print("  SRT-1 LIVE MIDDLEWARE v2.0")
    print("  Real-Time Anti-Hallucination Engine for AI Code Assistants")
    print("=" * 60)
    print()

    engine = SCIALiveEngine(
        repo_path=args.repo_path,
        reflection_interval=args.interval,
    )

    # Start HTTP(S) server
    SRT1RequestHandler.engine = engine

    class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
        daemon_threads = True

    server = ThreadedHTTPServer((args.host, args.port), SRT1RequestHandler)

    if use_tls:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(certfile=args.tls_cert, keyfile=args.tls_key)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        scheme = "https"
    else:
        scheme = "http"

    print()
    print(f"  Listening on {scheme}://{args.host}:{args.port}")
    if use_tls and _tmp_cert_dir:
        print(f"  TLS: self-signed certificate (auto-generated in {_tmp_cert_dir})")
    elif use_tls:
        print(f"  TLS: certificate {args.tls_cert}")
    print()
    print("  Endpoints:")
    print(f"    POST {scheme}://{args.host}:{args.port}/task          — Set current task")
    print(f"    POST {scheme}://{args.host}:{args.port}/operation     — Log AI operation")
    print(f"    GET  {scheme}://{args.host}:{args.port}/context       — Full context bundle")
    print(f"    GET  {scheme}://{args.host}:{args.port}/status        — Coherence & status")
    print(f"    POST {scheme}://{args.host}:{args.port}/reset         — Reset session")
    print()
    print("  Watching for file changes every 5 seconds...")
    print("  Press Ctrl+C to stop.")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  SRT-1 Middleware stopped.")
        engine._watcher_running = False
        server.server_close()
    finally:
        if _tmp_cert_dir:
            import shutil
            shutil.rmtree(_tmp_cert_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
