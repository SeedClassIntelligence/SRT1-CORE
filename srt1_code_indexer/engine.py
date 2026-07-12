"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: ORCHESTRATOR, SERVICE_LAYER, CLI_ENTRY_POINT
Key Symbols: hash_password, generate_session_token, init_db, SRT1Engine, main ... and 38 more

Extracted Purposes:
  - SRT1Engine: The unified SRT-1 engine. Indexes, injects, watches, serves.
  - _log_event: Record a real, timestamped engine event. External signing is optional.
  - start: Run the full SRT-1 pipeline: index → analyze → inject → serve → watch.
  ...
"""
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
License: Business Source License 1.1
"""

import os
import sys

# ── Fix Windows terminal encoding ──────────────────────────────────────
# Windows consoles default to cp1252 which cannot encode Unicode box-drawing
# characters (╔═╗ etc.). Reconfigure to UTF-8 so banners render correctly.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass  # Fallback: let Python handle it

import json
import time
import hashlib
import logging
import threading
import argparse
import subprocess
import socket
import signal
import webbrowser
import sqlite3
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs

# ---- Import Core SCIA IP ----
_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_dir = os.path.dirname(_this_dir)  # SRT1-CORE
sys.path.insert(0, _this_dir)
if _core_dir not in sys.path:
    sys.path.insert(0, _core_dir)
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
    from srt1_platform.workcell import WorkCellRegistry
    from srt1_platform.repository_activation import RepositoryActivationRegistry
    from srt1_platform.change_proposal import ChangeProposalStore
except ImportError:
    SCIARemoteAuth = None
    SCIASeedQueue = None
    SeedStage = None
    SCIADispatchBridge = None
    WorkCellRegistry = None
    RepositoryActivationRegistry = None
    ChangeProposalStore = None

# ---- Shared LLM Intelligence Layer ----
try:
    from srt1_platform.intelligence_adapter import IntelligenceAdapter
    from srt1_platform.llm_providers import TokenBudget
except ImportError:
    IntelligenceAdapter = None
    TokenBudget = None

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

# ---- Operational Registry (Phase B) ----
try:
    from srt1_platform.operational_registry import OperationalRegistry
except ImportError:
    OperationalRegistry = None

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [SRT-1] %(message)s",
)
logger = logging.getLogger("srt1")


def _find_free_port(start_port: int, span: int = 100) -> int:
    for port in range(start_port, start_port + span):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port + span


# ---- Consumer Auth Helpers (unified from legacy/srt1_cloud.py) ----
DB_FILE = "srt1_cloud.db"
SECRET_KEY = "srt1-super-secret-production-key"

def indexer_hash_password(password: str) -> str:
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

    @staticmethod
    def _env_flag_enabled(name: str) -> bool:
        value = os.getenv(name, "").strip().lower()
        return value in {"1", "true", "yes", "on"}

    @classmethod
    def _llm_opt_in_enabled(cls) -> bool:
        return (
            cls._env_flag_enabled("SRT1_ENABLE_LLM")
            or cls._env_flag_enabled("SRT1_ENABLE_SEMANTIC_ENRICHMENT")
        )

    def _semantic_enrichment_enabled(self) -> bool:
        return bool(self.llm) and self._env_flag_enabled("SRT1_ENABLE_SEMANTIC_ENRICHMENT")

    def __init__(self, repo_path: str, task: Optional[str] = None, port: int = 7483):
        self.repo_path = os.path.abspath(repo_path)
        self.task = task
        self.port = port

        # Core SCIA IP
        self.srt_tool = SRT(reflection_interval=self.REFLECTION_INTERVAL)

        # ---- Shared LLM Intelligence (SRT-1 Thinking Mode) ----
        self.llm: Optional['IntelligenceAdapter'] = None
        if IntelligenceAdapter and self._llm_opt_in_enabled():
            try:
                adapter = IntelligenceAdapter()
                if adapter.is_available():
                    self.llm = adapter
                    logger.info(f"SRT-1 Intelligence Adapter: Active — providers: {adapter.get_available_providers()}")
                else:
                    logger.info("SRT-1 LLM: No providers configured — using deterministic analysis")
            except Exception as e:
                logger.warning(f"SRT-1 LLM: Init failed ({e}) — using deterministic analysis")

        elif IntelligenceAdapter:
            logger.info("SRT-1 LLM: Optional model enrichment disabled; using deterministic analysis")

        # Codebase knowledge
        self.manifest: Dict[str, Any] = {}
        self.symbol_table: Dict[str, List[Dict]] = {}
        self.curation_report: Dict[str, Any] = {}
        self.file_hashes: Dict[str, str] = {}
        self.call_graph: Dict[str, List[str]] = {}
        self.synopsis: str = ""

        # Session state
        self.task = task
        self.task_seed_id: Optional[str] = None
        self.build_plan: Optional[Dict[str, Any]] = None
        self.operations: List[Dict] = []
        self.injections: List[Dict] = []
        self.session_start = datetime.now()
        
        # Enforcement Auto-Nudge
        import time
        self.enforcement_nudge_enabled = True
        self.last_nudge_time = time.time()

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

            # Auto-generate or load dev token for mobile companion
            srt1_dir = os.path.join(self.repo_path, ".srt1")
            os.makedirs(srt1_dir, exist_ok=True)
            config_path = os.path.join(srt1_dir, "config.json")
            self.dev_token = None

            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        self.dev_token = config.get("mobile_token")
                except Exception:
                    pass

            if not self.dev_token:
                token_dict = self.auth.generate_token(label="mobile_companion")
                self.dev_token = token_dict.get("token")
                try:
                    config_data = {}
                    if os.path.exists(config_path):
                        with open(config_path, "r", encoding="utf-8") as f:
                            config_data = json.load(f)
                    config_data["mobile_token"] = self.dev_token
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(config_data, f)
                except Exception:
                    pass

        # ---- Authority Client (external signing service) ----
        try:
            from srt1_code_indexer.authority_client import AuthorityClient
            self.authority = AuthorityClient()
        except ImportError:
            self.authority = None

        # ---- Optional external authority hook ----
        self.signing_client = None
        try:
            from srt1_code_indexer.authority_client import AuthorityClient
            _authority = AuthorityClient()
            self.signing_client = _authority if _authority.is_available else None
        except ImportError:
            pass

        # ---- Seed Queue ----
        self.seed_queue: Optional[SCIASeedQueue] = None
        if SCIASeedQueue:
            queue_dir = os.path.join(self.repo_path, ".srt1", "seeds")
            self.seed_queue = SCIASeedQueue(queue_dir=queue_dir)

        # ---- WorkCell Registry ----
        self.workcell_registry = None
        if WorkCellRegistry:
            self.workcell_registry = WorkCellRegistry(repo_path=self.repo_path)

        # ---- Repository Activation Registry ----
        self.repository_registry = None
        if RepositoryActivationRegistry:
            activation_dir = os.path.join(self.repo_path, ".srt1", "repositories")
            self.repository_registry = RepositoryActivationRegistry(state_dir=activation_dir)
            try:
                self.repository_registry.register_current(
                    repo_path=self.repo_path,
                    runtime_port=self.port,
                    manifest=self.manifest,
                    workcell_count=0,
                    activate=True,
                )
            except Exception as exc:
                logger.warning(f"Repository activation registration failed: {exc}")

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

    def _get_repository_registry(self):
        """Return Repository Activation registry, lazily creating it for tests."""
        registry = getattr(self, "repository_registry", None)
        if registry:
            return registry
        if RepositoryActivationRegistry is None or not getattr(self, "repo_path", None):
            return None
        activation_dir = os.path.join(self.repo_path, ".srt1", "repositories")
        registry = RepositoryActivationRegistry(state_dir=activation_dir)
        self.repository_registry = registry
        return registry

    def _refresh_repository_activation(self) -> Dict[str, Any]:
        """Register the current local repository with current manifest/runtime state."""
        registry = self._get_repository_registry()
        if not registry:
            return {
                "status": "unavailable",
                "error": "Repository Activation registry unavailable",
                "repositories": [],
                "count": 0,
            }

        workcell_count = None
        workcells = self._get_workcell_status()
        if workcells:
            workcell_count = workcells.get("workcell_count")

        try:
            registry.register_current(
                repo_path=self.repo_path,
                runtime_port=getattr(self, "port", None),
                manifest=getattr(self, "manifest", {}) or {},
                workcell_count=workcell_count,
                activate=True,
            )
        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc),
                "repositories": registry.list_repositories(),
                "count": len(registry.list_repositories()),
            }
        return registry.summary()

    def _get_repository_activation_status(self) -> Dict[str, Any]:
        """Return first-run Repository Manager status for API/PWA surfaces."""
        registry = self._get_repository_registry()
        if not registry:
            return {
                "status": "unavailable",
                "active_repository": None,
                "repositories": [],
                "count": 0,
            }
        summary = registry.summary()
        if not summary.get("active_repository"):
            return self._refresh_repository_activation()
        return summary

    def _activate_repository(self, repo_id: Optional[str] = None) -> Dict[str, Any]:
        """Activate a known repository. Core only supports the current local runtime path."""
        registry = self._get_repository_registry()
        if not registry:
            return {"status": "unavailable", "error": "Repository Activation registry unavailable"}
        if not repo_id:
            return self._refresh_repository_activation()
        try:
            candidate = next((repo for repo in registry.list_repositories() if repo.get("repo_id") == repo_id), None)
            if candidate and os.path.realpath(candidate.get("path", "")) != os.path.realpath(self.repo_path):
                return {
                    "status": "registered",
                    "error": "Repository is registered, but this engine is running a different local path. Launch SRT-1 for that repository to activate it.",
                    "active_repository": registry.active_repository(),
                    "repositories": registry.list_repositories(),
                }
            active = registry.activate(repo_id)
            return {"status": "ready", "active_repository": active.to_dict(), "repositories": registry.list_repositories()}
        except Exception as exc:
            return {"status": "error", "error": str(exc), "repositories": registry.list_repositories()}

    def _register_repository_path(self, repo_path: Optional[str]) -> Dict[str, Any]:
        """Register a user-supplied local path without switching engine context unsafely."""
        registry = self._get_repository_registry()
        if not registry:
            return {"status": "unavailable", "error": "Repository Activation registry unavailable"}
        if not repo_path or not str(repo_path).strip():
            return {"status": "error", "error": "Repository path is required", "repositories": registry.list_repositories()}

        real_path = os.path.realpath(str(repo_path).strip())
        try:
            if os.path.realpath(real_path) == os.path.realpath(self.repo_path):
                return self._refresh_repository_activation()
            record = registry.register_path(real_path, activate=False)
            return {
                "status": "registered",
                "registered_repository": record.to_dict(),
                "active_repository": registry.active_repository(),
                "repositories": registry.list_repositories(),
                "message": "Repository path registered. Launch SRT-1 for that path to build its manifest, FileCells, and WorkCells.",
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc), "repositories": registry.list_repositories()}

    def _browse_repository_folder(self) -> Dict[str, Any]:
        """Open a local folder picker and register the selected repository path."""
        registry = self._get_repository_registry()
        if not registry:
            return {"status": "unavailable", "error": "Repository Activation registry unavailable"}
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            selected = filedialog.askdirectory(
                title="Select repository for SRT-1",
                initialdir=os.path.dirname(os.path.realpath(self.repo_path)),
            )
            root.destroy()
            if not selected:
                return {
                    "status": "cancelled",
                    "active_repository": registry.active_repository(),
                    "repositories": registry.list_repositories(),
                }
            return self._register_repository_path(selected)
        except Exception as exc:
            return {
                "status": "error",
                "error": f"Folder picker unavailable: {exc}",
                "active_repository": registry.active_repository(),
                "repositories": registry.list_repositories(),
            }

    def _launch_repository_runtime(self, repo_id: Optional[str]) -> Dict[str, Any]:
        """Launch an isolated SRT-1 engine for a registered repository."""
        registry = self._get_repository_registry()
        if not registry:
            return {"status": "unavailable", "error": "Repository Activation registry unavailable"}
        if not repo_id:
            return {"status": "error", "error": "Repository id is required", "repositories": registry.list_repositories()}

        repositories = registry.list_repositories()
        candidate = next((repo for repo in repositories if repo.get("repo_id") == repo_id), None)
        if not candidate:
            return {"status": "error", "error": f"Repository not registered: {repo_id}", "repositories": repositories}

        repo_path = os.path.realpath(candidate.get("path", ""))
        if not os.path.isdir(repo_path):
            return {"status": "error", "error": f"Repository path does not exist: {repo_path}", "repositories": repositories}

        if os.path.realpath(repo_path) == os.path.realpath(self.repo_path):
            return {
                "status": "ready",
                "active_repository": registry.active_repository(),
                "repositories": repositories,
                "runtime_port": getattr(self, "port", None),
                "dashboard_url": f"http://127.0.0.1:{getattr(self, 'port', '')}/dashboard",
                "message": "Repository is already running in this engine.",
            }

        if OperationalRegistry:
            try:
                op_registry = OperationalRegistry()
                for engine_entry in op_registry.get_active_engines():
                    if os.path.realpath(engine_entry.get("workspace_path", "")) == repo_path:
                        port = engine_entry.get("port")
                        return {
                            "status": "running",
                            "runtime_port": port,
                            "dashboard_url": f"http://127.0.0.1:{port}/dashboard",
                            "active_repository": registry.active_repository(),
                            "repositories": repositories,
                            "message": "Repository runtime is already running.",
                        }
            except Exception:
                pass

        start_port = int(getattr(self, "port", 7484) or 7484) + 1
        port = _find_free_port(start_port)
        log_dir = os.path.join(os.path.expanduser("~"), ".srt1", "runtime-logs")
        os.makedirs(log_dir, exist_ok=True)
        safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in os.path.basename(repo_path) or "repository")
        stdout_path = os.path.join(log_dir, f"{safe_name}_{port}.out.log")
        stderr_path = os.path.join(log_dir, f"{safe_name}_{port}.err.log")

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([_core_dir, env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        try:
            with open(stdout_path, "a", encoding="utf-8") as stdout, open(stderr_path, "a", encoding="utf-8") as stderr:
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "srt1_code_indexer.engine",
                        "--repo_path",
                        repo_path,
                        "--port",
                        str(port),
                    ],
                    cwd=_core_dir,
                    env=env,
                    stdout=stdout,
                    stderr=stderr,
                    stdin=subprocess.DEVNULL,
                    creationflags=creationflags,
                )
        except Exception as exc:
            return {"status": "error", "error": f"Could not launch repository runtime: {exc}", "repositories": repositories}

        record = registry.register_path(repo_path, runtime_port=port, activate=False)
        return {
            "status": "launching",
            "runtime_port": port,
            "pid": process.pid,
            "dashboard_url": f"http://127.0.0.1:{port}/dashboard",
            "registered_repository": record.to_dict(),
            "active_repository": registry.active_repository(),
            "repositories": registry.list_repositories(),
            "stdout_log": stdout_path,
            "stderr_log": stderr_path,
        }

    def _stop_repository_runtime(self, repo_id: Optional[str]) -> Dict[str, Any]:
        """Stop an isolated SRT-1 engine for a registered repository."""
        registry = self._get_repository_registry()
        if not registry:
            return {"status": "unavailable", "error": "Repository Activation registry unavailable"}
        if not repo_id:
            return {"status": "error", "error": "Repository id is required", "repositories": registry.list_repositories()}

        repositories = registry.list_repositories()
        candidate = next((repo for repo in repositories if repo.get("repo_id") == repo_id), None)
        if not candidate:
            return {"status": "error", "error": f"Repository not registered: {repo_id}", "repositories": repositories}

        repo_path = os.path.realpath(candidate.get("path", ""))
        if os.path.realpath(repo_path) == os.path.realpath(self.repo_path):
            return {
                "status": "error",
                "error": "Refusing to stop the current active engine from inside itself.",
                "active_repository": registry.active_repository(),
                "repositories": repositories,
            }
        if not OperationalRegistry:
            return {"status": "unavailable", "error": "OperationalRegistry unavailable", "repositories": repositories}

        try:
            op_registry = OperationalRegistry()
            engines = op_registry.get_all_engines().get("engines", {})
            match = None
            match_id = None
            for engine_id, entry in engines.items():
                if os.path.realpath(entry.get("workspace_path", "")) == repo_path and entry.get("status") == "RUNNING":
                    match = entry
                    match_id = engine_id
                    break
            if not match:
                record = registry.register_path(repo_path, runtime_port=None, activate=False)
                return {
                    "status": "not_running",
                    "registered_repository": record.to_dict(),
                    "active_repository": registry.active_repository(),
                    "repositories": registry.list_repositories(),
                }

            pid = match.get("pid")
            if pid:
                os.kill(int(pid), signal.SIGTERM)
            if match_id:
                op_registry.deregister_engine(match_id)
            record = registry.register_path(repo_path, runtime_port=None, activate=False)
            return {
                "status": "stopped",
                "stopped_pid": pid,
                "registered_repository": record.to_dict(),
                "active_repository": registry.active_repository(),
                "repositories": registry.list_repositories(),
            }
        except Exception as exc:
            return {"status": "error", "error": f"Could not stop repository runtime: {exc}", "repositories": registry.list_repositories()}

    def _shutdown_current_runtime(self) -> Dict[str, Any]:
        """Stop this local SRT-1 runtime after the HTTP response is sent."""
        port = getattr(self, "port", None)
        engine_id = getattr(self, "_engine_id", None)
        server = getattr(self, "_http_server", None)

        def _shutdown() -> None:
            time.sleep(0.35)
            try:
                if getattr(self, "_registry", None) and engine_id:
                    self._registry.deregister_engine(engine_id)
            except Exception:
                pass
            self._watcher_running = False
            if server:
                try:
                    server.shutdown()
                    server.server_close()
                    return
                except Exception:
                    pass
            os._exit(0)

        threading.Thread(target=_shutdown, daemon=True).start()
        return {
            "status": "stopping",
            "message": "SRT-1 runtime is stopping.",
            "port": port,
            "engine_id": engine_id,
        }

    def _log_event(self, category: str, message: str, data: Optional[Dict] = None) -> None:
        """Record a real, timestamped engine event. External signing is optional."""
        event = {
            "timestamp": time.time(),
            "iso": datetime.now().isoformat(),
            "category": category,
            "message": message,
            "data": data or {},
        }
        # Optional external signing; Core continues if unavailable.
        if self.signing_client:
            sig = self.signing_client.sign(
                {"category": category, "message": message, "ts": event["timestamp"]},
                phase="event_log"
            )
            if "error" not in sig:
                event["_provenance"] = sig
        # In-memory event cache for dashboard read performance.
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
        if hasattr(self, 'dev_token') and self.dev_token:
            print(f"  Mobile Companion token: {self.dev_token}")
            print(f"  Dashboard (Local):      http://localhost:{self.port}\n")
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

        # Step 4: Generate AI context files (with timeout to prevent server hang)
        print("  [4/6] Generating AI context files...")
        import threading
        context_result: Dict[str, Any] = {"status": "pending", "files_written": []}

        def _context_worker() -> None:
            context_result.update(self._generate_context_files())

        ctx_thread = threading.Thread(target=_context_worker, daemon=True)
        ctx_thread.start()
        ctx_thread.join(timeout=30)
        if ctx_thread.is_alive():
            print("         ⚠ Context generation still running in background (server will start anyway)")
            context_result.update({"status": "background", "files_written": []})
        elif context_result.get("files_written"):
            written = ", ".join(context_result["files_written"])
            print(f"         ✓ Context files updated: {written}")
        else:
            print(f"         ⚠ Context generation skipped: {context_result.get('reason', 'no files written')}")
        self._last_context_generation = dict(context_result)
        self._log_event("context", "Context generation completed", context_result)
        # ── SCIA Event: context_docs_generated (canonical audit name) ──
        self._log_event("context_docs_generated", "Assistant context generation checked", {
            "targets": context_result.get("files_written", []),
            "status": context_result.get("status"),
            "reason": context_result.get("reason"),
            "workspace_root": self.repo_path,
        })

        # Step 5: Generate build plan + plant task seed
        print(f"  [5/6] Generating build plan...")
        self.build_plan = self._generate_build_plan()
        print(f"         Project: {self.build_plan['project_name']}")
        print(f"         Type:    {self.build_plan['project_type']}")
        print(f"         Health:  {self.build_plan['health']['status']}")
        self._log_event("plan", f"Build plan generated for {self.build_plan['project_name']}", self.build_plan)

        if self.task:
            self._plant_seed(self.task)
            print(f"         Seed: \"{self.task}\"")
            self._log_event("seed", f"Task seed planted: {self.task}")
        else:
            # Auto-derive task from the project's own intent
            auto_task = self.build_plan.get("intent", "")[:180]
            if auto_task:
                self.task = auto_task
                print(f"         Auto-detected intent from project files.")
                self._log_event("seed", f"Auto-genesis task derived: {auto_task[:80]}...")

        # Step 6: Start server + watcher
        print(f"  [6/6] Starting live server...")
        print()

        # Start file watcher thread
        watcher = threading.Thread(target=self._watch_loop, daemon=True)
        watcher.start()
        self._log_event("watcher", "File watcher started — polling every 15s")

        # Start transparent telemetry (only if developer opted in)
        sync_thread = threading.Thread(target=self._telemetry_loop, daemon=True)
        sync_thread.start()

        # Start execution bridge monitoring
        if self.bridge:
            self.bridge.start_monitoring()
            print("         ✓ Execution Bridge monitoring active")
            self._log_event("bridge", "Execution bridge monitoring active")

        import socket
        import hashlib
        
        def derive_project_port(repo_path: str, base_port: int = 7483) -> int:
            """Derive a deterministic port from the repo path so each project has its own port."""
            path_hash = hashlib.sha256(os.path.abspath(repo_path).lower().encode()).hexdigest()
            offset = int(path_hash[:8], 16) % 1000
            return base_port + offset

        def get_free_port(start_port: int) -> int:
            for p in range(start_port, start_port + 100):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(('127.0.0.1', p)) != 0:
                        return p
            return start_port
        
        # Only derive a new port if the default 7483 is used (allows explicit override)
        if self.port == 7483:
            derived = derive_project_port(self.repo_path, self.port)
            self.port = get_free_port(derived)
        else:
            self.port = get_free_port(self.port)

        # Print ready message
        self._refresh_repository_activation()
        self._print_ready()
        self._log_event("engine", f"Server ready on port {self.port}", {"port": self.port})

        # ── Registry: Self-register + heartbeat ─────────────────────
        self._registry = None
        self._engine_id = None
        if OperationalRegistry:
            try:
                self._registry = OperationalRegistry()
                self._engine_id = OperationalRegistry.generate_engine_id(self.repo_path, self.port)
                manifest_hash = self.manifest.get("integrity", {}).get("manifest_hash", "")
                self._registry.register_engine(
                    engine_id=self._engine_id,
                    port=self.port,
                    workspace_path=self.repo_path,
                    manifest_hash=manifest_hash,
                    workspace_name=os.path.basename(self.repo_path),
                )
                print(f"         \u2713 Registered in OperationalRegistry (ID: {self._engine_id[:16]}...)")
                self._log_event("registry", f"Engine registered: {self._engine_id}", {"port": self.port})

                # Start heartbeat daemon
                def _heartbeat_loop():
                    while True:
                        time.sleep(15)
                        try:
                            mh = self.manifest.get("integrity", {}).get("manifest_hash", "")
                            self._registry.heartbeat(self._engine_id, manifest_hash=mh)
                        except Exception:
                            pass

                hb_thread = threading.Thread(target=_heartbeat_loop, daemon=True)
                hb_thread.start()

                # Register shutdown hook
                import atexit
                atexit.register(lambda: self._registry.deregister_engine(self._engine_id) if self._registry else None)
            except Exception as e:
                print(f"         \u26a0 Registry registration failed: {e}")

        # Open dashboard via the local server instead of file://
        dashboard_path = self._get_dashboard_path()
        if dashboard_path:
            webbrowser.open(f"http://127.0.0.1:{self.port}/dashboard")

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

        # Attach optional external trust provenance when configured.
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
        overlaps = self.curation_report.get("functional_overlaps", [])
        blocking_overlaps = [ov for ov in overlaps if not self._is_advisory_overlap(ov)]
        warnings = self._collect_warnings() if blocking_overlaps else []

        if blocking_overlaps:
            for ov in blocking_overlaps:
                func = ov["instances"][0]["function"]
                locs = [f"{i['file']}:{i['line']}" for i in ov["instances"]]
                event = self.srt_tool.register_violation(
                    rule="DUPLICATE_FUNCTION",
                    action="operation, seed_dispatch, build_progression",
                    level=EnforcementLevel.HARD_STOP,
                    reason=f"Function '{func}()' duplicated in: {', '.join(locs)}",
                    resolution=f"Remove duplicate or consolidate into canonical location",
                )
                # Attach optional external trust provenance when configured.
                if self.signing_client:
                    sig = self.signing_client.sign(event.to_dict(), phase="enforcement")
                    if "error" not in sig:
                        event.metadata = sig  # attach provenance

        if blocking_overlaps or warnings:
            self.srt_tool.set_enforcement_mode("enforcement")
            block_count = len(self.srt_tool.get_active_blocks())
            print(f"         \u26a0 Enforcement Mode: {block_count} violation(s) require remediation")
        else:
            self.srt_tool.set_enforcement_mode("advisory")
            print("         \u2713 Enforcement Mode: Advisory (codebase clean)")

    @staticmethod
    def _is_advisory_overlap(overlap: Dict[str, Any]) -> bool:
        """Return True for duplicate findings that should remain advisory only."""
        instances = overlap.get("instances", [])
        if not instances:
            return False

        files = [
            str(inst.get("file", "")).replace("\\", "/").lstrip("./")
            for inst in instances
        ]
        func = str(instances[0].get("function", ""))

        if any(path.startswith(("scratch/", "tests/")) for path in files):
            return True

        pwa_mirror_files = {
            "srt1_platform/pwa/api/platform.js",
            "srt1_platform/pwa/js/platform.js",
        }
        if set(files).issubset(pwa_mirror_files):
            return True

        interface_method_names = {
            "generate",
            "get_available_providers",
            "get_budget_status",
            "is_available",
        }
        if func in interface_method_names:
            return True

        return False

    # -----------------------------------------------------------------
    # INDEXING
    # -----------------------------------------------------------------


    def _index_codebase(self) -> None:
        """Run the full indexer pipeline."""
        with self._lock:
            try:
                # ── SCIA Event: repo_index_started ─────────────────────────
                import time as _time
                _index_start_ts = _time.time()
                _trigger = "startup" if not self.manifest else "file_watcher"
                self._log_event("repo_index_started", "Repository indexing started", {
                    "workspace_root": self.repo_path,
                    "trigger": _trigger,
                })

                # Capture T-1 state for Delta Audit
                state_t1 = {}
                if self.manifest:
                    state_t1 = dict(self.manifest)
                elif os.path.exists(os.path.join(self.repo_path, "srt1_code_manifest.json")):
                    try:
                        with open(os.path.join(self.repo_path, "srt1_code_manifest.json"), "r", encoding="utf-8") as f:
                            state_t1 = json.load(f)
                    except Exception:
                        pass
                
                indexer = SRT1CodeIndexer(self.repo_path)
                self.manifest = indexer.index_repository()
                self.symbol_table = indexer.symbol_table
                self.curation_report = indexer.curation_report

                for entry in indexer.file_manifest:
                    self.file_hashes[entry["file_path"]] = entry["content_hash"]

                registry = self._get_workcell_registry()
                if registry:
                    registry.populate_from_manifest(self.manifest)
                self._refresh_repository_activation()
                    
                # Run optional delta audit if a T-1 state and integration are available.
                if state_t1 and self.manifest:
                    try:
                        from srt1_platform.delta_auditor import SCIADeltaAuditor
                        delta_report = SCIADeltaAuditor.compute_delta(self.repo_path, state_t1, self.manifest)
                        if self.signing_client:
                            sig = self.signing_client.sign(delta_report, phase="delta_audit")
                            if "error" not in sig:
                                delta_report["_provenance"] = sig
                        
                        # Write to Audit file
                        audit_path = os.path.join(self.repo_path, "srt1_audit_delta.json")
                        with open(audit_path, "w", encoding="utf-8") as f:
                            json.dump(delta_report, f, indent=2)
                    except ImportError:
                        # Optional delta audit integration missing; Core continues.
                        pass

                # ── SCIA Event: repo_index_completed ───────────────────────
                _files_indexed = len(self.manifest.get("file_manifest", []))
                _symbols_found = sum(len(s) for s in self.symbol_table.values())
                _duration_ms = int((_time.time() - _index_start_ts) * 1000)
                self._log_event("repo_index_completed", "Repository indexing completed", {
                    "workspace_root": self.repo_path,
                    "files_indexed": _files_indexed,
                    "symbols_found": _symbols_found,
                    "duration_ms": _duration_ms,
                    "trigger": _trigger,
                })

                # ── Semantic Enrichment Layer ──────────────────────────────
                # Applied AFTER deterministic indexing completes.
                # If LLM is unavailable or fails, the deterministic manifest
                # remains the source of structural truth — unmodified.
                # All enrichment outputs are labeled as "semantic_enrichment"
                # to distinguish them from deterministic authority.
                if self._semantic_enrichment_enabled():
                    import threading
                    threading.Thread(target=self._apply_semantic_enrichment, daemon=True).start()
                else:
                    self._log_event(
                        "semantic_enrichment",
                        "Optional semantic enrichment skipped; deterministic manifest is active",
                        {"enabled": False},
                    )
                        
            except Exception as exc:
                # ── SCIA Event: repo_index_failed ──────────────────────────
                self._log_event("repo_index_failed", f"Repository indexing failed: {exc}", {
                    "workspace_root": self.repo_path,
                    "error": str(exc),
                })
                print(f"  [ERROR] Indexing failed: {exc}")


    # ═══════════════════════════════════════════════════════════════════════
    # SEMANTIC ENRICHMENT — Model-Assisted Understanding (Optional Layer)
    # ═══════════════════════════════════════════════════════════════════════
    #
    # These methods use the IntelligenceAdapter to add model-assisted
    # semantic understanding ON TOP of the deterministic AST manifest.
    #
    # Rules:
    #   - All outputs are labeled "semantic_enrichment" (not authority)
    #   - Deterministic manifest is NEVER modified — enrichments are additive
    #   - If LLM is unavailable, indexing continues with zero degradation
    #   - TokenBudget and AnalysisCache are respected
    #   - No code generation, no proposals, no execution
    # ═══════════════════════════════════════════════════════════════════════

    def _apply_semantic_enrichment(self) -> None:
        """Apply model-assisted semantic enrichment after deterministic indexing.
        If IntelligenceAdapter is unavailable, this is a no-op."""
        if not self.llm:
            return

        logger.info("SRT-1 Intelligence: Applying semantic enrichment layer...")
        enrichment_results = {}

        # 1. Enrich architectural roles
        try:
            role_enrichments = self._enrich_roles_semantic()
            if role_enrichments:
                enrichment_results["role_enrichments"] = role_enrichments
                logger.info(f"  ✓ Role enrichment: {len(role_enrichments)} symbols enriched")
        except Exception as e:
            logger.warning(f"  ⚠ Role enrichment failed ({e}), using deterministic roles")

        # 2. Detect semantic overlaps
        try:
            semantic_overlaps = self._detect_semantic_overlaps()
            if semantic_overlaps:
                enrichment_results["semantic_overlaps"] = semantic_overlaps
                logger.info(f"  ✓ Semantic overlap detection: {len(semantic_overlaps)} groups found")
        except Exception as e:
            logger.warning(f"  ⚠ Semantic overlap detection failed ({e})")

        # 3. Assess architectural coherence
        try:
            coherence = self._assess_coherence()
            if coherence and coherence.get("coherence_score", 0) > 0:
                enrichment_results["coherence_assessment"] = coherence
                logger.info(f"  ✓ Coherence assessment: score={coherence.get('coherence_score', 0)}/100")
        except Exception as e:
            logger.warning(f"  ⚠ Coherence assessment failed ({e})")

        # 4. Summarize key modules
        try:
            module_summaries = self._summarize_modules()
            if module_summaries:
                enrichment_results["module_summaries"] = module_summaries
                logger.info(f"  ✓ Module summaries: {len(module_summaries)} modules summarized")
        except Exception as e:
            logger.warning(f"  ⚠ Module summarization failed ({e})")

        # 5. Build context insight for current task
        try:
            if self.task:
                context_insight = self._build_context_insight()
                if context_insight:
                    enrichment_results["context_insight"] = context_insight
                    logger.info("  ✓ Context insight generated for current task")
        except Exception as e:
            logger.warning(f"  ⚠ Context insight failed ({e})")

        # 6. Deep-parse non-Python files via LLM
        # ── Phase D: Language Coverage Expansion ──
        # Regex gives us symbol names. This step gives us real understanding.
        try:
            deep_count = 0
            skip_exts = {'.py', '.md', '.json', '.yaml', '.yml', '.txt'}
            for fpath, symbols in list(self.symbol_table.items()):
                ext = os.path.splitext(fpath)[1].lower()
                if ext in skip_exts:
                    continue
                # Read source for this file
                full = os.path.join(self.repo_path, fpath)
                try:
                    with open(full, 'r', encoding='utf-8', errors='ignore') as fh:
                        source = fh.read()
                except Exception:
                    continue
                if not source.strip():
                    continue
                deep = self.llm.deep_analyze_source(source, fpath, ext, symbols)
                if deep and deep.get("enriched_symbols"):
                    # Merge deep analysis into existing symbols
                    existing_names = {s.get("name") for s in symbols}
                    for es in deep["enriched_symbols"]:
                        if es.get("name") not in existing_names:
                            symbols.append({
                                "name": es["name"],
                                "type": es.get("type", "function"),
                                "line": es.get("line", 0),
                                "reflection": {
                                    "architectural_role": "GENERAL",
                                    "purpose": es.get("purpose", ""),
                                    "risk_profile": es.get("risk", ["LOW_RISK"]),
                                },
                                "dependencies": es.get("dependencies", []),
                                "_source": "deep_analysis",
                            })
                    # Upgrade fidelity marker for this file
                    deep_count += 1
                    # Store per-file deep analysis metadata
                    if "deep_analysis" not in enrichment_results:
                        enrichment_results["deep_analysis"] = {}
                    enrichment_results["deep_analysis"][fpath] = {
                        "fidelity": "deep",
                        "purpose": deep.get("architectural_purpose", ""),
                        "risk_tags": deep.get("risk_tags", []),
                        "missed_symbols": len(deep.get("missed_symbols", [])),
                        "dependency_chains": len(deep.get("dependency_chains", [])),
                    }
            if deep_count:
                logger.info(f"  ✓ Deep analysis: {deep_count} non-Python files enhanced")
        except Exception as e:
            logger.warning(f"  ⚠ Deep non-Python analysis failed ({e})")

        # Store enrichments as a clearly labeled additive layer
        if enrichment_results and self.manifest:
            self.manifest["semantic_enrichment"] = {
                "_meta": {
                    "source": "IntelligenceAdapter",
                    "authority": "semantic_enrichment",
                    "note": "Model-assisted understanding. Not deterministic authority. "
                            "Deterministic AST manifest is the source of structural truth.",
                    "budget_status": self.llm.get_budget_status(),
                },
                **enrichment_results,
            }
            logger.info(f"SRT-1 Intelligence: Enrichment layer complete "
                        f"({len(enrichment_results)} sections)")

    def _enrich_roles_semantic(self) -> List[Dict]:
        """Use IntelligenceAdapter.enrich_roles() to semantically validate
        deterministic role assignments. Returns enrichment proposals only."""
        if not self.symbol_table:
            return []

        # Collect a representative sample of symbols for enrichment
        symbol_data = []
        for fpath, symbols in list(self.symbol_table.items())[:15]:
            for sym in symbols[:5]:
                reflection = sym.get("reflection", {})
                symbol_data.append({
                    "name": sym["name"],
                    "type": sym.get("type", "function"),
                    "file": fpath,
                    "docstring": sym.get("docstring_first_line", ""),
                    "deterministic_role": reflection.get("architectural_role", "GENERAL"),
                    "dependencies": sym.get("dependencies", [])[:5],
                })

        if not symbol_data:
            return []

        enrichments = self.llm.enrich_roles(symbol_data)

        # Merge enrichments back as additive metadata (never overwrite deterministic)
        enriched = []
        for e in enrichments:
            name = e.get("name", "")
            semantic_role = e.get("role", "")
            semantic_risk = e.get("risk", "")
            if not name:
                continue
            # Find the symbol and add semantic enrichment alongside deterministic role
            for fpath, symbols in self.symbol_table.items():
                for sym in symbols:
                    if sym["name"] == name:
                        if "semantic_enrichment" not in sym:
                            sym["semantic_enrichment"] = {}
                        sym["semantic_enrichment"]["semantic_role"] = semantic_role
                        sym["semantic_enrichment"]["semantic_risk"] = semantic_risk
                        enriched.append({
                            "name": name,
                            "file": fpath,
                            "deterministic_role": sym.get("reflection", {}).get("architectural_role", "GENERAL"),
                            "semantic_role": semantic_role,
                            "semantic_risk": semantic_risk,
                        })
                        break
        return enriched

    def _detect_semantic_overlaps(self) -> List[Dict]:
        """Use IntelligenceAdapter.detect_semantic_overlaps() to find semantic
        duplicates beyond pattern matching."""
        if not self.symbol_table:
            return []

        functions = []
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                if sym.get("type") == "function":
                    functions.append({
                        "name": sym["name"],
                        "file": fpath,
                        "docstring": sym.get("docstring_first_line", ""),
                        "dependencies": sym.get("dependencies", [])[:5],
                    })

        if len(functions) < 2:
            return []

        overlaps = self.llm.detect_semantic_overlaps(functions)

        # Add to curation report as semantic enrichment (not authoritative)
        if overlaps and self.curation_report:
            if "semantic_overlaps" not in self.curation_report:
                self.curation_report["semantic_overlaps"] = []
            for group in overlaps:
                self.curation_report["semantic_overlaps"].append({
                    "type": "semantic_overlap",
                    "source": "semantic_enrichment",
                    "group": group.get("group", []),
                    "reason": group.get("reason", ""),
                })
        return overlaps

    def _assess_coherence(self) -> Dict:
        """Use IntelligenceAdapter.assess_coherence() to assess architectural health."""
        if not self.manifest:
            return {}

        metadata = self.manifest.get("metadata", {})
        summary = (
            f"Repository: {metadata.get('repo_name', 'unknown')}\n"
            f"Files: {metadata.get('total_files_scanned', 0)}\n"
            f"Symbols: {metadata.get('total_symbols_indexed', 0)}\n"
            f"Reflections: {metadata.get('total_reflections', 0)}\n"
        )

        # Add role distribution
        roles = {}
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                role = sym.get("reflection", {}).get("architectural_role", "GENERAL")
                roles[role] = roles.get(role, 0) + 1
        summary += f"Role distribution: {dict(sorted(roles.items(), key=lambda x: -x[1])[:8])}\n"

        # Add curation summary
        curation = self.curation_report or {}
        summary += (
            f"Duplicates: {len(curation.get('duplicate_files', []))}\n"
            f"Overlaps: {len(curation.get('functional_overlaps', []))}\n"
            f"Unused: {len(curation.get('unused_functions', []))}\n"
        )

        return self.llm.assess_coherence(summary)

    def _summarize_modules(self) -> Dict[str, str]:
        """Use IntelligenceAdapter.summarize_module() on key source modules."""
        summaries = {}

        # Identify key modules (largest symbol count, up to 5)
        module_sizes = [
            (fpath, len(symbols))
            for fpath, symbols in self.symbol_table.items()
        ]
        module_sizes.sort(key=lambda x: -x[1])
        key_modules = [fpath for fpath, _ in module_sizes[:5]]

        for fpath in key_modules:
            full_path = os.path.join(self.repo_path, fpath)
            if not os.path.exists(full_path):
                continue
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    source = f.read()
                summary = self.llm.summarize_module(source, module_name=fpath)
                if summary:
                    summaries[fpath] = summary
            except Exception:
                continue

        return summaries

    def _build_context_insight(self) -> str:
        """Use IntelligenceAdapter.build_context_insight() to rank symbols
        by semantic relevance to the current task."""
        if not self.task or not self.symbol_table:
            return ""

        # Collect all symbols for relevance ranking
        all_symbols = []
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                all_symbols.append({
                    "name": sym["name"],
                    "type": sym.get("type", "function"),
                    "file": fpath,
                    "docstring": sym.get("docstring_first_line", ""),
                    "role": sym.get("reflection", {}).get("architectural_role", "GENERAL"),
                })

        return self.llm.build_context_insight(all_symbols, self.task)

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
        
        # Expose to manifest for the frontend
        self.manifest["call_graph"] = self.call_graph

    # -----------------------------------------------------------------
    # INTELLIGENT SYNOPSIS GENERATION
    # -----------------------------------------------------------------

    def _generate_synopsis(self) -> str:
        """
        Generate a semantic synopsis of the entire project.

        If an LLM is available, uses it for intelligent summarization.
        Results are hash-cached — identical codebase state costs zero tokens.
        Falls back to deterministic AST-based generation when no LLM is configured.
        """
        # ---- LLM-Enhanced Synopsis (SRT-1 Thinking Mode) ----
        if self.llm:
            try:
                return self._generate_synopsis_llm()
            except Exception as e:
                logger.warning(f"LLM synopsis failed ({e}), falling back to deterministic")

        # ---- Deterministic Fallback (no LLM) ----
        return self._generate_synopsis_deterministic()

    def _generate_synopsis_llm(self) -> str:
        """LLM-powered synopsis. Cached by codebase hash — repeats cost zero tokens."""
        # Build compact stats for the LLM
        total_files = len(self.manifest.get("file_manifest", []))
        total_symbols = sum(len(s) for s in self.symbol_table.values())
        total_chains = len(self.call_graph)
        repo_name = os.path.basename(self.repo_path)

        classes = []
        functions = []
        risk_counts: Dict[str, int] = {}
        roles: Dict[str, int] = {}

        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                ref = sym.get("reflection", {})
                role = ref.get("architectural_role", "GENERAL")
                roles[role] = roles.get(role, 0) + 1
                for r in ref.get("risk_profile", []):
                    if r != "LOW_RISK":
                        risk_counts[r] = risk_counts.get(r, 0) + 1
                if sym["type"] == "class" and sym["name"] != "__init__":
                    purpose = ref.get("purpose", "")
                    if purpose and purpose != "No docstring provided.":
                        classes.append(f"{sym['name']}: {purpose[:80]}")
                elif sym["type"] == "function":
                    functions.append(sym["name"])

        # Overlaps / warnings
        overlaps = self.curation_report.get("functional_overlaps", [])
        overlap_desc = ""
        if overlaps:
            for ov in overlaps[:3]:
                func = ov["instances"][0]["function"]
                locs = [i["file"] for i in ov["instances"]]
                overlap_desc += f"  - {func}() duplicated in: {', '.join(locs)}\n"

        context = (
            f"Repository: {repo_name}\n"
            f"Files: {total_files}, Classes: {len(classes)}, "
            f"Functions: {len(functions)}, Call chains: {total_chains}\n"
            f"Top classes:\n" + "\n".join(f"  - {c}" for c in classes[:8]) + "\n"
            f"Roles: {dict(sorted(roles.items(), key=lambda x: -x[1])[:5])}\n"
            f"Risks: {dict(sorted(risk_counts.items(), key=lambda x: -x[1])[:5])}\n"
            + (f"Duplications:\n{overlap_desc}" if overlap_desc else "")
        )

        response = self.llm.analyze(
            prompt=(
                "Generate a concise, semantic Project Synopsis for this codebase. "
                "Start with a one-line architectural description. Then list Core Components "
                "(top 5 classes with purpose), Risk Profile summary, and any warnings. "
                "Use markdown with ## headers. Be precise — no filler."
            ),
            context=context,
            max_tokens=1024,
        )

        if response.content and response.provider != "budget_exhausted":
            # Wrap in synopsis header if LLM didn't include it
            content = response.content.strip()
            if not content.startswith("##"):
                content = f"## 🧠 Project Synopsis\n\n{content}"
            return content

        # Budget exhausted — fall back
        return self._generate_synopsis_deterministic()

    def _generate_synopsis_deterministic(self) -> str:
        """Original deterministic synopsis. Zero LLM tokens. Always available."""
        lines = []
        lines.append(f"## 🧠 Project Synopsis\n")
        
        # 1. Extract intent and definitions from markdown rulebooks
        extracted_rules = []
        project_intent = ""
        
        md_files_to_check = ["AGENTS.md", "README.md"]
        for md_file in md_files_to_check:
            md_path = os.path.join(self.repo_path, md_file)
            if os.path.exists(md_path):
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Extract the first major paragraph as the project intent
                    if not project_intent:
                        for paragraph in content.split('\n\n'):
                            paragraph = paragraph.strip()
                            if paragraph and not paragraph.startswith('#') and not paragraph.startswith('>') and not paragraph.startswith('['):
                                if len(paragraph) > 50: # Substantial paragraph
                                    project_intent = paragraph
                                    break
                                    
                    # Extract definitions (H2 and H3 headers and their immediate text)
                    # Use line-by-line parsing instead of regex to avoid backtracking on large files
                    content_lines = content.split('\n')
                    i = 0
                    while i < len(content_lines):
                        line = content_lines[i]
                        if line.startswith('## ') or line.startswith('### '):
                            title = line.lstrip('#').strip()
                            # Collect body text until next header or empty section
                            body_parts = []
                            i += 1
                            while i < len(content_lines) and not content_lines[i].startswith('#'):
                                body_parts.append(content_lines[i])
                                i += 1
                                if len(body_parts) > 10:  # Cap to avoid huge sections
                                    break
                            body_clean = '\n'.join(body_parts).strip().split('\n\n')[0]
                            if body_clean and len(body_clean) > 20 and "I have analyzed" not in body_clean:
                                extracted_rules.append((title, body_clean.strip()))
                        else:
                            i += 1
                except Exception:
                    pass

        if project_intent:
            lines.append(f"**Architectural Intent:**")
            lines.append(f"{project_intent}\n")
            
        if extracted_rules:
            lines.append(f"**Extracted Core Concepts:**")
            # Only show top 3 to keep it concise but meaningful
            for title, desc in extracted_rules[:3]:
                # clean up bolding/newlines in description for tight display
                desc_clean = desc.replace('\\n', ' ').strip()
                if len(desc_clean) > 150:
                    desc_clean = desc_clean[:147] + "..."
                lines.append(f"- **{title}**: {desc_clean}")
            lines.append("")

        lines.append(f"**Codebase Statistics:**")
        
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
    # AUTO-GENESIS BUILD PLAN (Deterministic — No LLM)
    # -----------------------------------------------------------------

    def _generate_build_plan(self) -> Dict[str, Any]:
        """
        Derive a build plan from the files SRT-1 already read.
        Nothing fabricated. Pure extraction from the indexed codebase.
        """
        repo_name = os.path.basename(self.repo_path)

        # 1. Extract project intent from markdown (same source as synopsis)
        project_intent = ""
        project_name = repo_name
        md_files = ["README.md", "AGENTS.md", "CLAUDE.md", "task.md",
                     "architecture.md", "project_plan.txt", "TODO.md"]
        for md_file in md_files:
            md_path = os.path.join(self.repo_path, md_file)
            if os.path.exists(md_path):
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read(3000)
                    # Extract first H1 as the project name
                    for line in content.split('\n'):
                        line_s = line.strip()
                        if line_s.startswith('# ') and project_name == repo_name:
                            candidate = line_s[2:].strip()
                            if candidate and len(candidate) < 80:
                                project_name = candidate
                                break
                    # Extract first substantial paragraph as the intent
                    if not project_intent:
                        for paragraph in content.split('\n\n'):
                            paragraph = paragraph.strip()
                            if (paragraph and not paragraph.startswith('#')
                                    and not paragraph.startswith('>')
                                    and not paragraph.startswith('[')
                                    and not paragraph.startswith('```')
                                    and "AUTO-GENERATED" not in paragraph):
                                if len(paragraph) > 40:
                                    project_intent = paragraph[:300]
                                    break
                except Exception:
                    pass

        # 2. Inventory what already exists
        total_files = len(self.manifest.get("file_manifest", []))
        total_symbols = sum(len(s) for s in self.symbol_table.values())
        total_chains = len(self.call_graph)

        classes = []
        functions = []
        for fpath, symbols in self.symbol_table.items():
            for sym in symbols:
                if sym["type"] == "class" and sym["name"] != "__init__":
                    purpose = sym.get("reflection", {}).get("purpose", "")
                    classes.append({"name": sym["name"], "file": fpath, "purpose": purpose})
                elif sym["type"] == "function" and sym["name"] not in ("__init__", "__post_init__"):
                    purpose = sym.get("reflection", {}).get("purpose", "")
                    functions.append({"name": sym["name"], "file": fpath, "purpose": purpose})

        # 3. Identify gaps and warnings from curation
        overlaps = self.curation_report.get("functional_overlaps", [])
        unused = self.curation_report.get("unused_functions", [])
        warnings = self._collect_warnings()

        # 4. Detect file types to understand what the project IS
        file_types = {}
        for entry in self.manifest.get("file_manifest", []):
            ext = os.path.splitext(entry.get("file_path", ""))[1].lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1

        project_type = "Software Project"
        if file_types.get(".html", 0) > 2 or file_types.get(".tsx", 0) > 2:
            project_type = "Web Application"
        elif file_types.get(".py", 0) > 5:
            project_type = "Python Application"
        elif file_types.get(".ts", 0) > 5 or file_types.get(".js", 0) > 5:
            project_type = "JavaScript/TypeScript Application"

        # 5. Build the plan — raw data, no fabrication
        plan = {
            "project_name": project_name,
            "project_type": project_type,
            "intent": project_intent if project_intent else f"{project_name} — {project_type}",
            "inventory": {
                "files": total_files,
                "classes": len(classes),
                "functions": len(functions),
                "call_chains": total_chains,
            },
            "components": [
                {"name": c["name"], "file": os.path.basename(c["file"]),
                 "purpose": c["purpose"][:120] if c["purpose"] and c["purpose"] != "No docstring provided." else ""}
                for c in classes[:12]
            ],
            "health": {
                "duplicates": len(overlaps),
                "unused_functions": len(unused),
                "warnings": len(warnings),
                "status": "clean" if (len(overlaps) == 0 and len(warnings) == 0) else "needs_attention"
            },
            "action_items": [],
            "generated_at": datetime.now().isoformat(),
        }

        # Auto-derive action items from what is actually there
        if overlaps:
            for ov in overlaps[:3]:
                func = ov["instances"][0]["function"]
                plan["action_items"].append(
                    f"Resolve duplicate function '{func}()' — exists in {len(ov['instances'])} locations"
                )
        if unused:
            plan["action_items"].append(
                f"Review {len(unused)} potentially unused function(s) for cleanup"
            )
        if not project_intent:
            plan["action_items"].append(
                "Add a README.md with project description so SRT-1 can extract architectural intent"
            )
        if not plan["action_items"]:
            plan["action_items"].append(
                f"Codebase is clean. {total_files} files, {len(classes)} classes, {len(functions)} functions mapped."
            )

        return plan

    # -----------------------------------------------------------------
    # CONTEXT FILE GENERATION (Auto-Injection)
    # -----------------------------------------------------------------

    def _get_recall_seed_id(self) -> Optional[str]:
        """Return the canonical seed identity for recall hydration."""
        identity = self._get_active_seed_identity()
        if identity:
            return identity.get("queue_seed_id") or identity.get("seed_id")
        return self.task_seed_id

    def _get_recall_identity(self, seed_id: Optional[str] = None) -> Dict[str, Optional[str]]:
        """Return recall identity with queue seed as canonical when present."""
        if seed_id and getattr(self, "seed_queue", None):
            queue_seed_id = self._resolve_queue_seed_id(seed_id)
            if queue_seed_id:
                seed = self.seed_queue.get_seed(queue_seed_id)
                if seed:
                    return {
                        "queue_seed_id": queue_seed_id,
                        "srt_anchor_id": seed.get("srt_anchor_id"),
                        "manifest_hash": seed.get("manifest_hash"),
                    }

        identity = self._get_active_seed_identity()
        if identity:
            queue_seed_id = identity.get("queue_seed_id") or identity.get("seed_id")
            return {
                "queue_seed_id": queue_seed_id,
                "srt_anchor_id": identity.get("srt_anchor_id"),
                "manifest_hash": identity.get("manifest_hash"),
            }
        return {
            "queue_seed_id": self.task_seed_id,
            "srt_anchor_id": self.task_seed_id,
            "manifest_hash": None,
        }

    def _build_recall_url(self, seed_id: str, limit: int = 3) -> str:
        """Build the optional private-memory recall URL safely."""
        from urllib.parse import quote
        return f"http://127.0.0.1:8000/api/v1/memory/recall/{quote(seed_id, safe='')}?limit={limit}"

    def _fetch_recall_reflections(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Fetch optional private recall packets; fail closed when unavailable."""
        identity = self._get_recall_identity()
        seed_id = identity.get("queue_seed_id")
        if not seed_id or "{" in seed_id or "}" in seed_id:
            return []

        try:
            import urllib.request
            from srt1_platform.recall_packet import RecallPacket

            url = self._build_recall_url(seed_id, limit=limit)
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    recalls = data.get("recalls", [])
                    if not isinstance(recalls, list):
                        return []
                    return [
                        RecallPacket.from_external_reflection(
                            recall,
                            queue_seed_id=seed_id,
                            srt_anchor_id=identity.get("srt_anchor_id"),
                            manifest_hash=identity.get("manifest_hash"),
                        ).to_reinjection_dict()
                        for recall in recalls
                    ]
        except Exception:
            return []

        return []

    def _build_manifest_recall_candidates(
        self,
        limit: int = 5,
        seed_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Build local manifest recall candidates as packet-shaped data."""
        identity = self._get_recall_identity(seed_id=seed_id)
        queue_seed_id = identity.get("queue_seed_id")
        if not queue_seed_id or not self.task:
            return []

        if not getattr(self, "repo_path", None):
            return []

        manifest_path = os.path.join(self.repo_path, "srt1_code_manifest.json")
        if not os.path.isfile(manifest_path):
            return []

        try:
            from srt1_pro.context_bundler import SCIAContextBundler
            bundler = SCIAContextBundler(manifest_path)
            return bundler.build_recall_candidates(
                task=self.task,
                queue_seed_id=queue_seed_id,
                srt_anchor_id=identity.get("srt_anchor_id"),
                max_candidates=limit,
            )
        except Exception:
            return []

    def _build_recall_packets(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Collect packet-shaped recall inputs for reinjection."""
        packets: List[Dict[str, Any]] = []
        packets.extend(self._fetch_recall_reflections(limit=limit))
        packets.extend(self._build_manifest_recall_candidates(limit=limit))
        return packets

    def _build_recall_response(
        self,
        seed_id: str,
        limit: int = 3,
        include_external: bool = False,
    ) -> Dict[str, Any]:
        """Build the public Core recall API response without owning private memory."""
        identity = self._get_recall_identity(seed_id=seed_id)
        queue_seed_id = identity.get("queue_seed_id") or seed_id
        packets = (
            self._build_recall_packets(limit=limit)
            if include_external
            else self._build_manifest_recall_candidates(limit=limit, seed_id=seed_id)
        )
        if not packets:
            try:
                from srt1_platform.recall_packet import RecallPacket

                packets = [
                    RecallPacket.degraded(
                        queue_seed_id=queue_seed_id,
                        srt_anchor_id=identity.get("srt_anchor_id"),
                        reason="No local manifest candidates or external recall packets available.",
                    ).to_dict()
                ]
            except Exception:
                packets = []

        visible_packets = packets[:limit]
        return {
            "seed_id": queue_seed_id,
            "queue_seed_id": queue_seed_id,
            "srt_anchor_id": identity.get("srt_anchor_id"),
            "recalls": visible_packets,
            "count": len(visible_packets),
            "freshness_state": (
                "degraded"
                if visible_packets and visible_packets[0].get("freshness_state") == "degraded"
                else "fresh"
            ),
            "trust_state": {
                "signature": "unsigned",
                "verification": "unverified",
                "lineage": "missing",
            },
        }

    def _generate_context_files(self) -> Dict[str, Any]:
        """Inject JIT Context directly into the AGENTS.md master document via Reinjector."""
        result: Dict[str, Any] = {
            "status": "skipped",
            "files_written": [],
            "reason": None,
        }
        try:
            # Safely import the new reinjection middleware
            from srt1_pro.reinjector import SCIAReinjector
            reinjector = SCIAReinjector(self.repo_path)
            
            # Fetch current violations / drift
            warnings = self._collect_warnings()
            
            # Hydrate Recall Memory from backend (Phase 4 Runtime Hydration Bridge)
            reflections = self._build_recall_packets(limit=3)
            if False:
                try:
                    import urllib.request
                    import json
                    url = self._build_recall_url(self._get_recall_seed_id(), limit=3)
                    req = urllib.request.Request(url, method="GET")
                    with urllib.request.urlopen(req, timeout=1.5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode())
                            reflections = data.get("recalls", [])
                            if reflections:
                                print(f"         ✓ Downloaded {len(reflections)} ranked lessons from Knowledge Graph")
                except Exception as e:
                    # Fail silently if backend is offline or disconnected
                    pass
            
            # Inject JIT context directly into the master AGENTS.md
            success = reinjector.inject_packets(
                active_task=self.task,
                warnings=warnings,
                reflections=reflections
            )
            
            if success:
                print("         ✓ AGENTS.md proactively updated (Segmented Mode)")
                result["status"] = "updated"
                result["files_written"].append("AGENTS.md")
                try:
                    context_dir = os.path.join(self.repo_path, ".srt1", "context")
                    os.makedirs(context_dir, exist_ok=True)
                    context_path = os.path.join(context_dir, "runtime_codebase_map.md")
                    with open(context_path, "w", encoding="utf-8") as f:
                        f.write(self._build_codebase_map_only())
                    result["files_written"].append(os.path.relpath(context_path, self.repo_path))
                except Exception as e:
                    print(f"         Failed to write runtime codebase map: {e}")
                return result
                
                # Append the dynamic codebase map quietly to the bottom of the file
                # so the agent still knows what functions exist
                try:
                    agents_path = os.path.join(self.repo_path, "AGENTS.md")
                    with open(agents_path, "r", encoding="utf-8") as f:
                        c = f.read()
                    
                    # Cut out the old code map if it exists and append freshly generated one
                    if "## 📁 Runtime Codebase Map" in c:
                        c = c.split("## 📁 Runtime Codebase Map")[0]
                        
                    dynamic_map = self._build_codebase_map_only()
                    c = c.rstrip() + "\n\n## 📁 Runtime Codebase Map\n\n" + dynamic_map
                    
                    # Fix the dashboard link to use the actual runtime port
                    c = c.replace(
                        "http://127.0.0.1:7483/dashboard",
                        f"http://127.0.0.1:{self.port}/dashboard"
                    )
                    
                    with open(agents_path, "w", encoding="utf-8") as f:
                        f.write(c)
                except Exception as e:
                    print(f"         ⚠ Failed to append codebase map: {e}")
            else:
                print("         ⚠ AGENTS.md JIT block not found. Skipping reinjection.")
                result["reason"] = "AGENTS.md JIT block not found"
        except ImportError:
            print("         ⚠ srt1_pro.reinjector not found. Skipping dynamic reinjection.")
            result["reason"] = "srt1_pro.reinjector unavailable"

        # Attach optional external trust provenance when configured.
        if self.signing_client:
            import hashlib as _hl
            content_hash = _hl.sha256(("REINJECT_" + str(self.task)).encode()).hexdigest()
            sig = self.signing_client.sign(
                {"content_hash": content_hash, "files_written": 1},
                phase="context_reinjection"
            )
            if "error" not in sig:
                print("         ✓ Reinjection event signed by authority")
        return result

    def _write(self, directory: str, filename: str, content: str) -> None:
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _build_codebase_map_only(self) -> str:
        """Build ONLY the dynamic codebase structure for append."""
        L: List[str] = []

        if self.synopsis:
            L.append(self.synopsis)
            L.append("")
        L.append(f"\n*SRT-1 Runtime Codebase Map generated at: {datetime.now().isoformat()}*")
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

    @staticmethod
    def _is_remediation_seed_payload(body: Dict[str, Any]) -> bool:
        """Return True when a seed is explicitly created to resolve findings."""
        source = str(body.get("source") or "").lower()
        context = body.get("context") if isinstance(body.get("context"), dict) else {}
        finding_type = body.get("finding_type") or context.get("finding_type")
        return source in {
            "dashboard_finding",
            "reflection_finding",
            "remediation",
        } or bool(finding_type)

    def _plant_seed(self, task: str, source: str = "api",
                    priority: int = 5, auto_dispatch: bool = False,
                    template_id: Optional[str] = None,
                    assistant_credentials: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Plant a seed and optionally dispatch it through the execution bridge.

        If template_id is provided, uses that template's curated keywords
        and domain. Otherwise, auto-detects the best matching template.
        Falls back to generic keyword extraction if no template matches.
        """
        self.task = task
        self.operations = []
        self.injections = []
        self.srt_tool = SRT(reflection_interval=self.REFLECTION_INTERVAL)

        # Canonical lifecycle seed: create queue record before reflection anchor.
        queue_seed_id = None
        if self.seed_queue:
            seed = self.seed_queue.plant(
                intent=task, source=source, priority=priority
            )
            queue_seed_id = seed.seed_id

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

        if queue_seed_id and self.seed_queue:
            if hasattr(self.seed_queue, "set_srt_anchor"):
                self.seed_queue.set_srt_anchor(queue_seed_id, self.task_seed_id)
            else:
                seed = self.seed_queue._seeds.get(queue_seed_id)
                if seed:
                    seed.srt_anchor_id = self.task_seed_id
                    self.seed_queue._save()

        workcell_execution = None
        if queue_seed_id:
            workcell_execution = self._activate_workcell_execution(queue_seed_id, task)

        if self.analytics:
            self.analytics.record_seed_planted(applied_template)

        credential_context = self._normalize_assistant_credentials(assistant_credentials)

        if queue_seed_id and self.seed_queue:
            # Auto-dispatch through execution bridge (in background thread)
            if auto_dispatch and self.bridge:
                def _dispatch_async(sid, t):
                    job_id = None
                    try:
                        allowed_paths = self._get_workcell_allowed_paths(workcell_execution)
                        registry = self._get_workcell_registry()
                        if registry:
                            job_result = registry.start_execution_job(
                                sid,
                                provider=credential_context["provider"] or "execution_bridge",
                                adapter="assistant_adapter",
                                cancellable=True,
                                hard_cancellable=False,
                                runtime_port=(workcell_execution or {}).get("runtime_port"),
                                metadata={
                                    "allowed_paths": allowed_paths,
                                    "credential_mode": credential_context["mode"],
                                    "credential_providers": credential_context["providers"],
                                },
                            )
                            job_id = (job_result.get("job") or {}).get("job_id")
                            registry.record_execution_event(
                                sid,
                                event_type="assistant.dispatch_started",
                                status="running",
                                actor="execution_bridge",
                                message="Assistant dispatch entered WorkCell runtime governor.",
                                metadata={"allowed_paths": allowed_paths, "execution_job_id": job_id},
                                execution_status="running",
                            )
                        guard = self._check_workcell_dispatch_guard(sid, allowed_paths)
                        if not guard.get("allowed"):
                            if registry:
                                registry.update_execution_job(
                                    sid,
                                    job_id=job_id,
                                    status="blocked",
                                    metadata=guard,
                                )
                                registry.record_execution_event(
                                    sid,
                                    event_type="assistant.dispatch_blocked",
                                    status="blocked",
                                    actor="workcell_runtime_governor",
                                    message=guard.get("reason") or "Assistant dispatch blocked by WorkCell runtime governor.",
                                    metadata=guard,
                                )
                            return

                        bp_result = self.generate_blueprint(t)
                        self.seed_queue.germinate(
                            seed_id=sid,
                            blueprint=bp_result.get("blueprint", ""),
                            blueprint_path=bp_result.get("saved_to", ""),
                            relevant_symbols=bp_result.get("relevant_symbols", 0),
                            relevant_files=bp_result.get("relevant_files", 0),
                        )
                        guard = self._check_workcell_dispatch_guard(sid, allowed_paths)
                        if not guard.get("allowed"):
                            if registry:
                                registry.update_execution_job(
                                    sid,
                                    job_id=job_id,
                                    status="blocked",
                                    metadata=guard,
                                )
                                registry.record_execution_event(
                                    sid,
                                    event_type="assistant.dispatch_blocked",
                                    status="blocked",
                                    actor="workcell_runtime_governor",
                                    message=guard.get("reason") or "Assistant dispatch blocked before adapter handoff.",
                                    metadata=guard,
                                )
                            return

                        dispatch_result = self.bridge.dispatch_seed(
                            seed_id=sid,
                            intent=t,
                            blueprint=bp_result.get("blueprint", ""),
                            blueprint_meta={
                                "relevant_symbols": bp_result.get("relevant_symbols", 0),
                                "relevant_files": bp_result.get("relevant_files", 0),
                                "workcell_package_path": (workcell_execution or {}).get("package_path"),
                                "allowed_paths": allowed_paths,
                                "restricted_paths": (workcell_execution or {}).get("restricted_paths", []),
                                "trust_state": (workcell_execution or {}).get("trust_state", {}),
                                "credential_mode": credential_context["mode"],
                                "credential_provider": credential_context["provider"],
                                "credential_providers": credential_context["providers"],
                            },
                            execution_context={
                                **(workcell_execution or {}),
                                "credential_mode": credential_context["mode"],
                                "credential_provider": credential_context["provider"],
                                "credential_providers": credential_context["providers"],
                            },
                            transient_credentials=credential_context["provider_keys"],
                        )
                        registry = self._get_workcell_registry()
                        if registry:
                            registry.update_execution_job(
                                sid,
                                job_id=job_id,
                                status="dispatched",
                                provider_acknowledged=dispatch_result.get("dispatched", False),
                                result={
                                    "methods": dispatch_result.get("methods", {}),
                                    "dispatched": dispatch_result.get("dispatched", False),
                                },
                            )
                            registry.record_execution_event(
                                sid,
                                event_type="assistant.dispatched",
                                status="dispatched",
                                actor="execution_bridge",
                                message="Bounded WorkCell request handed to configured assistant adapters.",
                                metadata={
                                    "methods": dispatch_result.get("methods", []),
                                    "dispatched": dispatch_result.get("dispatched", False),
                                    "credential_mode": credential_context["mode"],
                                    "credential_providers": credential_context["providers"],
                                    "credential_secret_persisted": False,
                                },
                                execution_status="dispatched",
                            )
                    except Exception as e:
                        registry = self._get_workcell_registry()
                        if registry:
                            registry.update_execution_job(
                                sid,
                                job_id=job_id,
                                status="failed",
                                error=str(e),
                            )
                            registry.record_execution_event(
                                sid,
                                event_type="assistant.dispatch_failed",
                                status="failed",
                                actor="execution_bridge",
                                message=str(e),
                            )
                        logger.error(f"Async dispatch failed for {sid}: {e}")
                threading.Thread(
                    target=_dispatch_async, args=(queue_seed_id, task),
                    daemon=True, name=f"dispatch-{queue_seed_id[:8]}"
                ).start()

        return queue_seed_id

    def _get_workcell_registry(self):
        """Return the WorkCell registry, lazily creating it for test/legacy engines."""
        registry = getattr(self, "workcell_registry", None)
        if registry:
            return registry
        if WorkCellRegistry is None or not getattr(self, "repo_path", None):
            return None
        registry = WorkCellRegistry(repo_path=self.repo_path)
        self.workcell_registry = registry
        return registry

    def _activate_workcell_execution(self, queue_seed_id: str, objective: str) -> Optional[Dict[str, Any]]:
        """Create a read-only WorkCell execution package for a canonical queue seed."""
        registry = self._get_workcell_registry()
        if not registry:
            return None
        try:
            execution = registry.activate_execution(
                queue_seed_id=queue_seed_id,
                srt_anchor_id=getattr(self, "task_seed_id", None),
                objective=objective,
                manifest=getattr(self, "manifest", {}) or {},
                runtime_port=getattr(self, "port", None),
                assigned_agent="unassigned",
            )
            return execution.to_dict()
        except Exception as exc:
            logger.warning(f"WorkCell execution activation failed for {queue_seed_id}: {exc}")
            return None

    def _get_workcell_allowed_paths(self, workcell_execution: Optional[Dict[str, Any]]) -> List[str]:
        """Resolve the selected WorkCell's canonical write scope for assistant dispatch."""
        if not workcell_execution:
            return []
        direct = workcell_execution.get("owned_paths") or workcell_execution.get("allowed_paths")
        if direct:
            return list(direct)
        registry = self._get_workcell_registry()
        workcell_id = workcell_execution.get("workcell_id")
        workcells = getattr(registry, "_workcells", {}) if registry else {}
        workcell = workcells.get(workcell_id)
        return list(getattr(workcell, "owned_paths", []) or [])

    def _get_workcell_status(self, queue_seed_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Return WorkCell registry summary or a specific execution for status/API output."""
        registry = self._get_workcell_registry()
        if not registry:
            return None
        if queue_seed_id:
            execution = registry.get_execution_for_seed(queue_seed_id)
            if execution:
                return execution
        return registry.summary()

    def _repair_workcell_package(self, queue_seed_id: Optional[str]) -> Dict[str, Any]:
        """Regenerate local WorkCell package files for an existing queue seed."""
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error"}
        registry = self._get_workcell_registry()
        if not registry:
            return {"error": "WorkCell registry unavailable", "status": "error"}
        return registry.repair_execution_package(queue_seed_id)

    def _get_workcell_md_preview(self, queue_seed_id: Optional[str]) -> Dict[str, Any]:
        """Return generated workcell.md instructions for a WorkCell execution."""
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error"}
        registry = self._get_workcell_registry()
        if not registry:
            return {"error": "WorkCell registry unavailable", "status": "error"}
        return registry.read_workcell_md(queue_seed_id)

    def _get_workcell_workspace(self, queue_seed_id: Optional[str]) -> Dict[str, Any]:
        """Return the visual WorkCell workspace descriptor for browser IDE surfaces."""
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error"}
        registry = self._get_workcell_registry()
        if not registry:
            return {"error": "WorkCell registry unavailable", "status": "error"}
        return registry.get_execution_workspace(queue_seed_id)

    def _get_workcell_activity(
        self,
        queue_seed_id: Optional[str],
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error", "events": []}
        registry = self._get_workcell_registry()
        if not registry:
            return {"error": "WorkCell registry unavailable", "status": "error", "events": []}
        return registry.get_execution_activity(queue_seed_id, limit=limit, offset=offset)

    def _control_workcell_execution(
        self,
        queue_seed_id: Optional[str],
        action: str,
        actor: str = "human",
        reason: str = "",
    ) -> Dict[str, Any]:
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error"}
        registry = self._get_workcell_registry()
        if not registry:
            return {"error": "WorkCell registry unavailable", "status": "error"}
        return registry.control_execution(queue_seed_id, action, actor=actor, reason=reason)

    def _verify_workcell_execution(
        self,
        queue_seed_id: Optional[str],
        verified: bool = True,
        actor: str = "dashboard_human",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error"}
        registry = self._get_workcell_registry()
        if not registry:
            return {"error": "WorkCell registry unavailable", "status": "error"}
        verification_details = dict(details or {})
        verification_details.setdefault("source", "dashboard_review_lane")
        verification_details.setdefault("method", "manual_core_verification")
        return registry.record_verification(
            queue_seed_id,
            verified=bool(verified),
            actor=actor or "dashboard_human",
            details=verification_details,
        )

    def _dispatch_existing_workcell_execution(
        self,
        queue_seed_id: Optional[str],
        assistant_credentials: Optional[Dict[str, Any]] = None,
        actor: str = "dashboard_human",
        background: bool = True,
    ) -> Dict[str, Any]:
        """Dispatch an existing WorkCell execution without planting a duplicate seed."""
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error"}
        registry = self._get_workcell_registry()
        if not registry:
            return {"error": "WorkCell registry unavailable", "status": "error"}
        if not getattr(self, "bridge", None):
            return {"error": "Execution bridge unavailable", "status": "error"}

        execution = registry.get_execution_for_seed(queue_seed_id)
        if not execution:
            return {"error": "WorkCell execution not found", "status": "not_found", "queue_seed_id": queue_seed_id}

        allowed_paths = self._get_workcell_allowed_paths(execution)
        credential_context = self._normalize_assistant_credentials(assistant_credentials)
        job_result = registry.start_execution_job(
            queue_seed_id,
            provider=credential_context["provider"] or "execution_bridge",
            adapter="assistant_adapter",
            cancellable=True,
            hard_cancellable=False,
            runtime_port=execution.get("runtime_port"),
            metadata={
                "allowed_paths": allowed_paths,
                "credential_mode": credential_context["mode"],
                "credential_providers": credential_context["providers"],
                "dispatch_source": "existing_workcell",
            },
        )
        if job_result.get("status") != "registered":
            return job_result
        job_id = (job_result.get("job") or {}).get("job_id")

        def _dispatch_now() -> Dict[str, Any]:
            try:
                guard = self._check_workcell_dispatch_guard(queue_seed_id, allowed_paths)
                if not guard.get("allowed"):
                    registry.update_execution_job(queue_seed_id, job_id=job_id, status="blocked", metadata=guard)
                    registry.record_execution_event(
                        queue_seed_id,
                        event_type="assistant.dispatch_blocked",
                        status="blocked",
                        actor="workcell_runtime_governor",
                        message=guard.get("reason") or "Assistant dispatch blocked by WorkCell runtime governor.",
                        metadata=guard,
                    )
                    return {"status": "blocked", "queue_seed_id": queue_seed_id, "job_id": job_id, "guard": guard}

                objective = execution.get("objective") or "Execute selected WorkCell objective"
                bp_result = self.generate_blueprint(objective)
                if getattr(self, "seed_queue", None):
                    try:
                        self.seed_queue.germinate(
                            seed_id=queue_seed_id,
                            blueprint=bp_result.get("blueprint", ""),
                            blueprint_path=bp_result.get("saved_to", ""),
                            relevant_symbols=bp_result.get("relevant_symbols", 0),
                            relevant_files=bp_result.get("relevant_files", 0),
                        )
                    except Exception:
                        pass

                dispatch_result = self.bridge.dispatch_seed(
                    seed_id=queue_seed_id,
                    intent=objective,
                    blueprint=bp_result.get("blueprint", ""),
                    blueprint_meta={
                        "relevant_symbols": bp_result.get("relevant_symbols", 0),
                        "relevant_files": bp_result.get("relevant_files", 0),
                        "workcell_package_path": execution.get("package_path"),
                        "allowed_paths": allowed_paths,
                        "restricted_paths": execution.get("restricted_paths", []),
                        "trust_state": execution.get("trust_state", {}),
                        "credential_mode": credential_context["mode"],
                        "credential_provider": credential_context["provider"],
                        "credential_providers": credential_context["providers"],
                    },
                    execution_context={
                        **execution,
                        "allowed_paths": allowed_paths,
                        "credential_mode": credential_context["mode"],
                        "credential_provider": credential_context["provider"],
                        "credential_providers": credential_context["providers"],
                    },
                    transient_credentials=credential_context["provider_keys"],
                )
                registry.update_execution_job(
                    queue_seed_id,
                    job_id=job_id,
                    status="dispatched",
                    provider_acknowledged=dispatch_result.get("dispatched", False),
                    result={
                        "methods": dispatch_result.get("methods", {}),
                        "dispatched": dispatch_result.get("dispatched", False),
                    },
                )
                registry.record_execution_event(
                    queue_seed_id,
                    event_type="assistant.dispatched",
                    status="dispatched",
                    actor="execution_bridge",
                    message="Existing WorkCell execution handed to configured assistant adapters.",
                    metadata={
                        "methods": dispatch_result.get("methods", {}),
                        "dispatched": dispatch_result.get("dispatched", False),
                        "credential_mode": credential_context["mode"],
                        "credential_providers": credential_context["providers"],
                        "credential_secret_persisted": False,
                    },
                    execution_status="dispatched",
                )
                return {
                    "status": "dispatched",
                    "queue_seed_id": queue_seed_id,
                    "job_id": job_id,
                    "dispatch": dispatch_result,
                    "secret_persisted": False,
                }
            except Exception as exc:
                registry.update_execution_job(queue_seed_id, job_id=job_id, status="failed", error=str(exc))
                registry.record_execution_event(
                    queue_seed_id,
                    event_type="assistant.dispatch_failed",
                    status="failed",
                    actor="execution_bridge",
                    message=str(exc),
                )
                return {"status": "failed", "queue_seed_id": queue_seed_id, "job_id": job_id, "error": str(exc)}

        if background:
            threading.Thread(
                target=_dispatch_now,
                daemon=True,
                name=f"workcell-dispatch-{queue_seed_id[:8]}",
            ).start()
            return {
                "status": "dispatch_started",
                "queue_seed_id": queue_seed_id,
                "job_id": job_id,
                "allowed_paths": allowed_paths,
                "secret_persisted": False,
            }
        return _dispatch_now()

    def _acknowledge_workcell_execution_job(
        self,
        queue_seed_id: Optional[str],
        acknowledgement: str,
        job_id: Optional[str] = None,
        actor: str = "assistant_runtime",
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error"}
        registry = self._get_workcell_registry()
        if not registry:
            return {"error": "WorkCell registry unavailable", "status": "error"}
        return registry.acknowledge_execution_job(
            queue_seed_id,
            job_id=job_id,
            acknowledgement=acknowledgement,
            actor=actor,
            message=message,
            metadata=metadata,
        )

    def _get_change_proposal_store(self):
        if ChangeProposalStore is None:
            return None
        return ChangeProposalStore(repo_path=self.repo_path)

    def _list_change_proposals(self, queue_seed_id: Optional[str] = None) -> Dict[str, Any]:
        store = self._get_change_proposal_store()
        if not store:
            return {"status": "error", "error": "ChangeProposal store unavailable", "proposals": []}
        return store.list_proposals(queue_seed_id=queue_seed_id)

    def _get_change_proposal(self, proposal_id: Optional[str]) -> Dict[str, Any]:
        if not proposal_id:
            return {"status": "error", "error": "proposal_id is required"}
        store = self._get_change_proposal_store()
        if not store:
            return {"status": "error", "error": "ChangeProposal store unavailable"}
        return store.get_proposal(proposal_id)

    def _apply_change_proposal(
        self,
        proposal_id: Optional[str],
        actor: str = "human",
    ) -> Dict[str, Any]:
        if not proposal_id:
            return {"status": "error", "error": "proposal_id is required"}
        store = self._get_change_proposal_store()
        if not store:
            return {"status": "error", "error": "ChangeProposal store unavailable"}
        record = store.get_proposal(proposal_id)
        if record.get("status") == "not_found":
            return record
        queue_seed_id = record.get("queue_seed_id")
        proposal = record.get("proposal") or {}
        target_paths = (
            proposal.get("files_write", [])
            + proposal.get("files_create", [])
            + proposal.get("files_delete", [])
        )
        write_check = self._validate_workcell_writes(
            queue_seed_id,
            target_paths,
            actor="change_proposal_apply_gate",
        )
        if not write_check.get("allowed"):
            return {
                "status": "blocked",
                "proposal_id": proposal_id,
                "error": "WorkCell write validation blocked proposal apply.",
                "write_check": write_check,
            }
        result = store.apply_proposal(proposal_id, actor=actor)
        registry = self._get_workcell_registry() if queue_seed_id else None
        if registry:
            registry.record_execution_event(
                queue_seed_id,
                event_type="change_proposal.apply",
                status=result.get("status") or "unknown",
                actor=actor or "human",
                message="Approved ChangeProposal apply attempted.",
                metadata={
                    "proposal_id": proposal_id,
                    "applied": result.get("applied", False),
                    "files_changed": result.get("files_changed", []),
                    "verification": result.get("verification"),
                },
            )
        return result

    def _review_change_proposal(
        self,
        proposal_id: Optional[str],
        action: str,
        actor: str = "human",
        reason: str = "",
    ) -> Dict[str, Any]:
        if not proposal_id:
            return {"status": "error", "error": "proposal_id is required"}
        store = self._get_change_proposal_store()
        if not store:
            return {"status": "error", "error": "ChangeProposal store unavailable"}
        result = store.review_proposal(proposal_id, action=action, actor=actor, reason=reason)
        queue_seed_id = result.get("queue_seed_id")
        registry = self._get_workcell_registry() if queue_seed_id else None
        if registry and result.get("status") not in {"not_found", "invalid_action", "blocked", "error"}:
            registry.record_execution_event(
                queue_seed_id,
                event_type=f"change_proposal.{action}",
                status=result.get("status") or "reviewed",
                actor=actor or "human",
                message=reason or f"Change proposal {action} requested.",
                metadata={
                    "proposal_id": proposal_id,
                    "applied": False,
                    "source_mutation": False,
                },
            )
        return result

    def _validate_workcell_writes(
        self,
        queue_seed_id: Optional[str],
        proposed_paths: Optional[List[str]],
        actor: str = "assistant_runtime",
    ) -> Dict[str, Any]:
        if not queue_seed_id:
            return {"error": "queue_seed_id is required", "status": "error", "allowed": False}
        registry = self._get_workcell_registry()
        if not registry:
            return {
                "error": "WorkCell registry unavailable",
                "status": "error",
                "allowed": False,
            }
        return registry.validate_execution_writes(
            queue_seed_id,
            proposed_paths or [],
            actor=actor,
        )

    def _check_workcell_dispatch_guard(
        self,
        queue_seed_id: Optional[str],
        allowed_paths: Optional[List[str]],
    ) -> Dict[str, Any]:
        """Fail closed unless the active WorkCell can accept assistant execution."""
        if not queue_seed_id:
            return {"allowed": False, "status": "blocked", "reason": "queue_seed_id is required"}
        registry = self._get_workcell_registry()
        if not registry:
            return {"allowed": False, "status": "blocked", "reason": "WorkCell registry unavailable"}
        execution = registry.get_execution_for_seed(queue_seed_id)
        if not execution:
            return {"allowed": False, "status": "blocked", "reason": "WorkCell execution not found"}
        execution_status = execution.get("status") or "unknown"
        if execution_status in {"pause_requested", "stop_requested", "cancelled", "terminated", "completed"}:
            return {
                "allowed": False,
                "status": "blocked",
                "reason": f"WorkCell is {execution_status}",
                "execution_status": execution_status,
            }
        write_check = registry.validate_execution_writes(
            queue_seed_id,
            allowed_paths or [],
            actor="assistant_runtime_governor",
        )
        if not write_check.get("allowed"):
            return {
                "allowed": False,
                "status": "blocked",
                "reason": "Assistant dispatch requires validated WorkCell write scope.",
                "execution_status": execution_status,
                "write_check": write_check,
            }
        return {
            "allowed": True,
            "status": "allowed",
            "execution_status": execution_status,
            "write_check": write_check,
        }

    def _sanitize_assistant_adapter_config(
        self, adapters: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Return Core-safe assistant adapter configs without storing raw API keys."""
        clean: List[Dict[str, Any]] = []
        for adapter in adapters or []:
            adapter_type = str(adapter.get("type") or "").strip().lower()
            if not adapter_type:
                continue
            enabled = adapter.get("enabled", True)
            if isinstance(enabled, str):
                enabled = enabled.lower() not in {"0", "false", "no", "off"}
            if not enabled:
                continue
            if adapter_type in {"codex"}:
                clean.append({"type": "codex", "name": "codex"})
            elif adapter_type in {"file", "file_context", "file_handoff"}:
                clean.append({
                    "type": "file_context",
                    "name": str(adapter.get("name") or "file_context"),
                })
            elif adapter_type in {"custom_http", "http", "webhook"}:
                endpoint = str(adapter.get("endpoint") or "").strip()
                if endpoint:
                    clean.append({
                        "type": "custom_http",
                        "endpoint": endpoint,
                        "timeout": float(adapter.get("timeout") or 20.0),
                    })
            elif adapter_type in {"openai_compatible", "provider_runtime", "llm_provider"}:
                endpoint = str(adapter.get("endpoint") or "").strip()
                model = str(adapter.get("model") or "").strip()
                provider = str(adapter.get("provider") or "openai").strip().lower()
                if endpoint and model:
                    clean.append({
                        "type": "openai_compatible",
                        "provider": provider,
                        "endpoint": endpoint,
                        "model": model,
                        "timeout": float(adapter.get("timeout") or 60.0),
                    })
        return clean

    def _normalize_assistant_credentials(
        self,
        credentials: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Normalize dispatch-only credentials without persisting secret values."""
        if not isinstance(credentials, dict):
            return {
                "mode": "none",
                "provider": "",
                "providers": [],
                "provider_keys": {},
                "secret_persisted": False,
            }

        mode = str(credentials.get("mode") or "session").strip().lower()
        if mode not in {"session", "external"}:
            mode = "session"

        requested_provider = str(credentials.get("provider") or "").strip().lower()
        allowed = {"openai", "anthropic", "gemini", "grok", "groq", "together", "custom"}
        provider_keys: Dict[str, str] = {}

        if mode == "session":
            raw_keys = credentials.get("provider_keys") or credentials.get("keys") or {}
            if isinstance(raw_keys, dict):
                for provider, value in raw_keys.items():
                    name = str(provider or "").strip().lower()
                    key = str(value or "").strip()
                    if name in allowed and key:
                        provider_keys[name] = key

        providers = sorted(provider_keys)
        if mode == "external" and requested_provider in allowed:
            providers = [requested_provider]

        provider = requested_provider if requested_provider in providers else (providers[0] if providers else "")
        return {
            "mode": mode if (mode == "external" or provider_keys) else "none",
            "provider": provider,
            "providers": providers,
            "provider_keys": provider_keys,
            "secret_persisted": False,
        }

    def _get_assistant_adapter_config(self) -> Dict[str, Any]:
        """Expose bridge adapter configuration without secrets."""
        bridge = getattr(self, "bridge", None)
        adapters = list(getattr(bridge, "assistant_adapters", []) or []) if bridge else []
        methods = list(getattr(bridge, "dispatch_methods", []) or []) if bridge else []
        return {
            "status": "available" if bridge else "not_available",
            "dispatch_methods": methods,
            "assistant_adapters": adapters,
            "available_adapters": [
                {
                    "type": "codex",
                    "label": "Codex WorkCell handoff",
                    "description": "Writes bounded WorkCell instructions for Codex.",
                },
                {
                    "type": "file_context",
                    "label": "File handoff",
                    "description": "Writes a model-agnostic request package into .srt1/adapters/.",
                },
                {
                    "type": "custom_http",
                    "label": "Custom HTTP model adapter",
                    "description": "Posts bounded WorkCell JSON to a developer-controlled endpoint.",
                },
                {
                    "type": "openai_compatible",
                    "label": "OpenAI-compatible provider runtime",
                    "description": "Calls any chat-completions-compatible LLM with transient credentials and bounded WorkCell context.",
                },
            ],
            "slack_seed_endpoint": "/api/v1/slack/seed",
            "slack_command_endpoint": "/api/v1/slack/command",
        }

    def _configure_assistant_adapters(
        self, adapters: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Persist Core-safe assistant adapter configuration on the bridge."""
        bridge = getattr(self, "bridge", None)
        if not bridge:
            return {"status": "error", "error": "Execution bridge unavailable"}
        clean = self._sanitize_assistant_adapter_config(adapters)
        bridge.configure(assistant_adapters=clean)
        return {
            "status": "configured",
            "assistant_adapters": clean,
            "dispatch_methods": list(bridge.dispatch_methods),
        }

    def _plant_slack_seed(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Plant a Slack-originated seed through the canonical queue-first path."""
        task = (
            body.get("task")
            or body.get("text")
            or body.get("message")
            or body.get("command_text")
            or ""
        ).strip()
        if task.startswith("/srt1"):
            task = task[len("/srt1"):].strip()
        if not task:
            return {
                "status": "error",
                "error": "Missing Slack seed text",
                "response_type": "ephemeral",
                "text": "SRT-1 needs a seed objective. Example: /srt1 improve dashboard contrast",
            }

        source = body.get("source") or "slack"
        priority = int(body.get("priority") or 5)
        auto_dispatch = body.get("auto_dispatch", True)
        if isinstance(auto_dispatch, str):
            auto_dispatch = auto_dispatch.lower() not in {"0", "false", "no", "off"}

        queue_seed_id = self._plant_seed(
            task,
            source=source,
            priority=priority,
            auto_dispatch=auto_dispatch,
            template_id=body.get("template_id"),
            assistant_credentials=body.get("assistant_credentials"),
        )
        self.task = task
        threading.Thread(target=self._generate_context_files, daemon=True).start()
        response = self._build_task_response(
            task=task,
            queue_seed_id=queue_seed_id,
            auto_dispatch=auto_dispatch,
        )
        credential_summary = self._normalize_assistant_credentials(
            body.get("assistant_credentials")
        )
        response.update({
            "status": "seed_planted",
            "source": source,
            "assistant_credentials": {
                "mode": credential_summary["mode"],
                "providers": credential_summary["providers"],
                "secret_persisted": False,
            },
            "slack": {
                "channel_id": body.get("channel_id"),
                "user_id": body.get("user_id"),
                "user_name": body.get("user_name"),
                "team_id": body.get("team_id"),
            },
            "response_type": "ephemeral",
            "text": f"SRT-1 seed planted: {queue_seed_id}",
        })
        return response

    def _resolve_queue_seed_id(self, seed_id: Optional[str]) -> Optional[str]:
        """Resolve a public/callback seed id to canonical queue seed id."""
        if not seed_id or not self.seed_queue:
            return None
        if self.seed_queue.get_seed(seed_id):
            return seed_id
        for candidate in self.seed_queue.list_seeds(limit=1000):
            full_seed = self.seed_queue.get_seed(candidate["seed_id"])
            if full_seed and full_seed.get("srt_anchor_id") == seed_id:
                return full_seed["seed_id"]
        return None

    def _on_seed_completed(self, seed_id: str, files_modified: List[str],
                           summary: str) -> None:
        """Callback when the execution bridge detects seed completion."""
        queue_seed_id = self._resolve_queue_seed_id(seed_id)
        registry = self._get_workcell_registry()
        if registry and queue_seed_id:
            registry.record_execution_event(
                queue_seed_id,
                event_type="completion.proposed",
                status="awaiting_verification",
                actor="execution_bridge",
                message=summary,
                metadata={"files_modified": files_modified},
                execution_status="awaiting_review",
            )
        if self.seed_queue and queue_seed_id:
            self.seed_queue.propose_completion(
                queue_seed_id,
                summary=summary,
                files_modified=files_modified,
            )

        # --- COMPLETENESS VERIFICATION ENFORCEMENT ---
        if self.validator:
            if registry and queue_seed_id:
                registry.record_execution_event(
                    queue_seed_id,
                    event_type="verification.started",
                    status="running",
                    actor="verification",
                    message="Post-execution verification started.",
                    metadata={"files_to_check": files_modified},
                )
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
                
                if self.seed_queue and queue_seed_id:
                    # Update seed status to active / error
                    self.seed_queue.return_for_revision(queue_seed_id, reason=error_msg)
                if registry and queue_seed_id:
                    registry.record_verification(
                        queue_seed_id,
                        verified=False,
                        details={
                            "empty_harness_count": len(report.empty_harnesses),
                            "files_checked": files_modified,
                        },
                    )
                
                self.srt_tool.add_reflection("WARNING", error_msg, {"action": "rejected_completion"})
                return
            if self.seed_queue and queue_seed_id:
                self.seed_queue.record_verification_result(
                    queue_seed_id,
                    verified=True,
                    details={"validator": "SeedTreeValidator"},
                )
            if registry and queue_seed_id:
                registry.record_verification(
                    queue_seed_id,
                    verified=True,
                    details={"validator": "SeedTreeValidator", "files_checked": files_modified},
                )

        # Commit bloom
        if self.seed_queue and queue_seed_id:
            self.seed_queue.accept_completion(queue_seed_id, summary=summary, actor="verification")
            for f in files_modified:
                self.seed_queue.record_file_change(queue_seed_id, f)
        if registry and queue_seed_id:
            registry.record_execution_event(
                queue_seed_id,
                event_type="completion.accepted",
                status="completed",
                actor="continuity",
                message=summary,
                metadata={"files_modified": files_modified},
                execution_status="completed",
            )
        logger.info(f"🌸 Seed {seed_id} BLOOMED: {summary}")

    def _on_seed_failed(self, seed_id: str, reason: str) -> None:
        """Callback when a seed fails or goes stale."""
        queue_seed_id = self._resolve_queue_seed_id(seed_id)
        if self.seed_queue and queue_seed_id:
            self.seed_queue.wilt(queue_seed_id, reason=reason)
        logger.warning(f"🍂 Seed {seed_id} WILTED: {reason}")

    def _build_task_response(self, task: str, queue_seed_id: Optional[str],
                             auto_dispatch: bool) -> Dict[str, Any]:
        """Build the /task response without changing lifecycle ownership."""
        response = {
            "status": "task_set", "task": task,
            "seed_id": queue_seed_id or self.task_seed_id,
            "queue_seed_id": queue_seed_id,
            "srt_anchor_id": self.task_seed_id,
            "dispatched": auto_dispatch and self.bridge is not None,
            "codebase_files": len(self.manifest.get("file_manifest", [])),
            "template_applied": getattr(self, '_applied_template', None),
        }
        if queue_seed_id and self.seed_queue:
            seed = self.seed_queue.get_seed(queue_seed_id)
            if seed:
                response["lifecycle"] = {
                    "stage": seed["stage"],
                    "stage_emoji": seed["stage_emoji"],
                    "growth": seed["growth"],
                }
                response["workcell"] = self._get_workcell_status(queue_seed_id)
        return response

    def _get_active_seed_identity(self) -> Optional[Dict[str, Any]]:
        """Return user-facing seed identity with queue state as canonical."""
        if self.seed_queue:
            active_seed = self.seed_queue.get_active_seed()
            if active_seed:
                return {
                    "seed_id": active_seed["seed_id"],
                    "queue_seed_id": active_seed["seed_id"],
                    "srt_anchor_id": active_seed.get("srt_anchor_id") or self.task_seed_id,
                    "lifecycle_state": active_seed.get("stage"),
                    "trust_state": active_seed.get("trust_state"),
                    "manifest_hash": active_seed.get("manifest_hash"),
                    "intent": active_seed.get("intent"),
                    "stage": active_seed.get("stage"),
                    "growth": active_seed.get("growth"),
                }

        if self.task_seed_id:
            return {
                "seed_id": self.task_seed_id,
                "queue_seed_id": None,
                "srt_anchor_id": self.task_seed_id,
                "lifecycle_state": None,
                "trust_state": None,
                "manifest_hash": None,
                "intent": getattr(self, "task", None),
                "stage": None,
                "growth": None,
            }

        return None

    def _task_keywords(self, task: str) -> List[str]:
        """Extract keywords from task. Uses LLM intent classification when available."""
        # LLM-enhanced: use classify_intent for semantic keyword extraction
        if self.llm:
            try:
                intent = self.llm.classify_intent(task)
                if intent.confidence > 0.4:
                    kw = []
                    kw.extend(w.lower() for w in intent.title.split() if len(w) > 2)
                    kw.extend(d.lower() for d in intent.domains)
                    kw.extend(w.lower() for w in intent.description.split() if len(w) > 3)
                    return list(set(kw))[:20]
            except Exception as e:
                logger.warning(f"LLM intent classification failed ({e}), using deterministic")

        # Deterministic fallback
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
        safe_chars = []
        for char in seed.lower()[:80]:
            safe_chars.append(char if char.isalnum() else "_")
        safe_name = "_".join(part for part in "".join(safe_chars).split("_") if part)[:40]
        safe_name = safe_name or "seed"
        blueprint_path = os.path.join(blueprint_dir, f"blueprint_{safe_name}.md")
        with open(blueprint_path, "w", encoding="utf-8") as f:
            f.write(blueprint_text)

        # ── FILECELL ASSIGNMENT ─────────────────────────────────────
        filecell_manifest = None
        try:
            from srt1_platform.filecell import FileCellManifest
            # Read scope: All relevant files found in the codebase scan
            allowed_reads = [os.path.abspath(os.path.join(self.repo_path, f)) for f in relevant_files]
            # Write scope: Only the top 3 most relevant files (to demonstrate strict separation)
            # Dependencies fall into read scope but NOT write scope.
            allowed_writes = [os.path.abspath(os.path.join(self.repo_path, s["file"])) for s in top_relevant[:3]]
            
            # Prevent self-modification or audit ledger tampering
            forbidden = [os.path.abspath(os.path.join(self.repo_path, ".srt1"))]
            
            filecell_manifest = FileCellManifest.generate(
                task_intent=seed,
                allowed_reads=allowed_reads,
                allowed_writes=allowed_writes,
                forbidden_paths=forbidden
            )
            
            # Emit immediate Seed Signature for allocation
            if getattr(self, "signing_client", None):
                try:
                    self.signing_client.sign(
                        content={"cell_id": filecell_manifest.cell_id, "intent": seed},
                        phase="filecell_allocation"
                    )
                except Exception:
                    pass
        except ImportError:
            pass

        return {
            "blueprint": blueprint_text,
            "seed": seed,
            "relevant_symbols": len(top_relevant),
            "relevant_files": len(relevant_files),
            "saved_to": blueprint_path,
            "filecell_manifest": filecell_manifest
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
            metadata={"context": " ".join(self._task_keywords(self.task or ""))},
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
            f"ACTIVE TASK: {self.task}",
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
                "task": self.task,
                "message": f"REMINDER: Your task is: '{self.task}'. Stay focused.",
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
    # TRANSPARENT TELEMETRY (Opt-In, Self-Enforcing)
    # -----------------------------------------------------------------
    #
    # SRT-1 Telemetry Commitment:
    #   - ONLY runs if the developer explicitly consented on first run
    #   - NEVER sends: file names, file paths, source code, function names,
    #     repo names, or anything that identifies the project or person
    #   - DOES send: anonymous UUID, file count, symbol count, violation
    #     count, OS type, SRT-1 version
    #   - Every payload is logged to the dashboard activity feed so the
    #     developer can see exactly what was sent
    #   - Self-enforcement: if any outbound call is made that wasn't logged,
    #     the engine flags it as an enforcement violation
    #

    _TELEMETRY_URL = "https://telemetry.srt1.network/v1/ping"
    _SRT1_VERSION = "1.0.0"

    @staticmethod
    def _get_consent_path(repo_path: str) -> str:
        """Get path to the telemetry consent file."""
        return os.path.join(repo_path, ".srt1", "consent.json")

    @staticmethod
    def _check_telemetry_consent(repo_path: str) -> bool:
        """Check if the developer has opted in to telemetry."""
        consent_path = SRT1Engine._get_consent_path(repo_path)
        if not os.path.exists(consent_path):
            return False
        try:
            with open(consent_path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
                return data.get("telemetry_consent", False)
        except Exception:
            return False

    @staticmethod
    def _save_telemetry_consent(repo_path: str, consented: bool) -> None:
        """Save the developer's telemetry consent decision."""
        consent_path = SRT1Engine._get_consent_path(repo_path)
        os.makedirs(os.path.dirname(consent_path), exist_ok=True)
        import json as _json
        data = {
            "telemetry_consent": consented,
            "decided_at": datetime.now().isoformat(),
            "note": "You can change this at any time by editing this file."
        }
        with open(consent_path, "w", encoding="utf-8") as f:
            f.write(_json.dumps(data, indent=2))

    @staticmethod
    def _get_anonymous_id(repo_path: str) -> str:
        """Get or create a stable anonymous UUID (not tied to identity)."""
        import uuid
        consent_path = SRT1Engine._get_consent_path(repo_path)
        try:
            with open(consent_path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
                if "anonymous_id" in data:
                    return data["anonymous_id"]
        except Exception:
            pass
        return str(uuid.uuid4())

    def _build_telemetry_payload(self) -> dict:
        """Build the exact payload that will be sent. Nothing hidden."""
        import platform
        files = len(self.manifest.get("file_manifest", []))
        syms = sum(len(s) for s in self.symbol_table.values())
        enforcement = self.srt_tool.get_compliance_stats()
        violations = enforcement.get("enforcements_issued", 0)
        overlaps = len(self.manifest.get("curation_report", {}).get("functional_overlaps", []))

        return {
            "id": self._get_anonymous_id(self.repo_path),
            "v": self._SRT1_VERSION,
            "os": platform.system(),
            "files": files,
            "symbols": syms,
            "violations": violations,
            "overlaps": overlaps,
            "t": int(time.time())
        }
        # NOTE: No repo name. No file names. No paths. No code. No identity.

    def _telemetry_loop(self) -> None:
        """Background thread: transparent, opt-in anonymous telemetry."""
        import urllib.request

        # If developer did not consent, thread exits immediately
        if not self._check_telemetry_consent(self.repo_path):
            return

        self._log_event("trust", "Telemetry active (opted in). All payloads logged to dashboard.")

        while self._watcher_running:
            time.sleep(86400)  # Once per day — minimal footprint
            try:
                payload = self._build_telemetry_payload()

                # Log EXACTLY what we're sending to the dashboard activity feed
                self._log_event(
                    "trust",
                    f"Telemetry ping sent: {json.dumps(payload)}",
                    {"payload": payload, "destination": self._TELEMETRY_URL}
                )

                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    self._TELEMETRY_URL,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                # 3-second timeout — never blocks the engine
                with urllib.request.urlopen(req, timeout=3) as resp:
                    pass

            except Exception:
                # Network down, server unreachable — silently continue
                pass

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
        _last_reindex_time = 0.0  # Debounce: prevent re-index storms
        while self._watcher_running:
            time.sleep(15)
            if getattr(self, "enforcement_nudge_enabled", False) and (time.time() - getattr(self, "last_nudge_time", time.time())) >= 1800:
                try:
                    self._generate_context_files()
                    self._log_event("nudge", "Auto-Nudge (30m) triggered. Context files regenerated.", {"type": "enforcement_nudge"})
                    self.last_nudge_time = time.time()
                except Exception:
                    pass

            # Debounce: skip if we re-indexed less than 60s ago
            if time.time() - _last_reindex_time < 60:
                continue

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
                    display_path = file_path.replace("seed-reflection/", "").replace("seed-reflection\\\\", "").replace("SRT1-CORE\\\\", "").replace("SRT1-CORE/", "")
                    self._log_event("watcher", f"File change detected: {display_path}", {"file": display_path})
                    self._index_codebase()
                    new_files = len(self.manifest.get("file_manifest", []))
                    new_syms = sum(len(s) for s in self.symbol_table.values())
                    self._log_event("indexing", f"Re-indexed: {new_files} files, {new_syms} symbols", {"files": new_files, "symbols": new_syms})
                    self._build_call_graph()
                    self._generate_context_files()
                    # Refresh hashes AFTER context generation to prevent detecting our own writes
                    for entry in self.manifest.get("file_manifest", []):
                        fp2 = os.path.join(self.repo_path, entry.get("file_path", ""))
                        if os.path.exists(fp2):
                            try:
                                with open(fp2, "rb") as f2:
                                    self.file_hashes[entry["file_path"]] = hashlib.sha256(f2.read()).hexdigest()
                            except OSError:
                                pass
                    _last_reindex_time = time.time()
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
                if not length:
                    return {}
                raw = self.rfile.read(length).decode("utf-8", errors="replace")
                content_type = self.headers.get("Content-Type", "")
                if "application/x-www-form-urlencoded" in content_type:
                    parsed = parse_qs(raw, keep_blank_values=True)
                    return {
                        key: values[-1] if values else ""
                        for key, values in parsed.items()
                    }
                try:
                    return json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    return {"text": raw}

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
                    
                ui_routes = [
                    "/dashboard", "/consumer", "/admin", "/mobile", "/observatory", "/constellation",
                    "/auth.html", "/index.html", "/comparison.html", "/documentation.html",
                    "/assets/", "/js/", "/sw.js", "/manifest.json", "/download"
                ]
                if endpoint == "/" or any(endpoint.startswith(p) for p in ui_routes):
                    return True

                client_ip = self.client_address[0] if self.client_address else "127.0.0.1"
                
                # Local developer dashboard bypasses API auth
                if client_ip == "127.0.0.1":
                    return True
                    
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
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, x-api-key")
                self.end_headers()

            def do_GET(self):
                path = urlparse(self.path).path

                if getattr(self, "path", "").startswith("/debug-path"):
                    return self._json({"path": path, "raw": self.path})

                if not self._check_auth(path):
                    return

                if path == "/language-coverage":
                    coverage = engine.manifest.get("language_coverage", {})
                    return self._json({
                        "coverage": coverage,
                        "total_languages": len(coverage),
                        "structurally_parsed": [ext for ext, data in coverage.items() if data.get("symbols", 0) > 0],
                        "scan_only": [ext for ext, data in coverage.items() if data.get("symbols", 0) == 0],
                    })

                elif path == "/llm-status":
                    if engine.llm:
                        return self._json({
                            "available": engine.llm.is_available(),
                            "providers": engine.llm.get_available_providers(),
                            "budget": engine.llm.get_budget_status(),
                        })
                    else:
                        return self._json({"available": False, "providers": [], "budget": None})

                elif path == "/engine-info":
                    uptime = (datetime.now() - engine.session_start).total_seconds()
                    manifest_hash = engine.manifest.get("integrity", {}).get("manifest_hash", "")
                    return self._json({
                        "engine_id": getattr(engine, '_engine_id', None),
                        "port": engine.port,
                        "workspace_path": engine.repo_path,
                        "workspace_name": os.path.basename(engine.repo_path),
                        "manifest_hash": manifest_hash,
                        "uptime_seconds": round(uptime, 1),
                        "files_indexed": len(engine.manifest.get("file_manifest", [])),
                        "total_symbols": sum(len(s) for s in engine.symbol_table.values()),
                        "task": engine.task,
                        "status": "RUNNING",
                        "language_coverage": engine.manifest.get("language_coverage", {}),
                    })

                elif path == "/dashboard-summary":
                    metadata = engine.manifest.get("metadata", {})
                    enforcement = engine.srt_tool.get_compliance_stats()
                    curation = engine.curation_report or {}
                    manifest_hash = engine.manifest.get("integrity", {}).get("manifest_hash", "")
                    files = engine.manifest.get("file_manifest", [])
                    symbol_count = sum(len(s) for s in engine.symbol_table.values())

                    self._json({
                        "repo": os.path.basename(engine.repo_path),
                        "product": "SRT-1 v2.0",
                        "manifest_hash": manifest_hash,
                        "manifest_freshness": "fresh" if manifest_hash else "unknown",
                        "files_indexed": metadata.get("total_files_scanned", len(files)),
                        "symbols_indexed": metadata.get("total_symbols_indexed", symbol_count),
                        "reflections": metadata.get("total_reflections", 0),
                        "duplicate_files": len(curation.get("duplicate_files", [])),
                        "functional_overlaps": len(curation.get("functional_overlaps", [])),
                        "unused_functions": len(curation.get("unused_functions", [])),
                        "trust": {
                            "signature": "signed" if engine.signing_client else "unsigned",
                            "verification": "verified" if engine._trust_integrity else "unverified",
                            "lineage": "present" if engine._trust_chain else "missing",
                        },
                        "enforcement": {
                            "mode": enforcement.get("mode", "unknown"),
                            "active_blocks": enforcement.get("active_blocks", 0),
                            "violations_total": enforcement.get("enforcements_issued", 0),
                        },
                        "seed_queue": engine.seed_queue.get_stats() if engine.seed_queue else None,
                        "active_seed": engine._get_active_seed_identity(),
                        "repository_activation": engine._get_repository_activation_status(),
                        "workcells": engine._get_workcell_status(),
                    })

                elif path == "/api/v1/users/me":
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
                
                elif path == "/admin/stats":
                    # Master Telemetry Endpoint for Admin Dashboard
                    seed_stats = {}
                    if engine.seed_queue:
                        seed_stats = engine.seed_queue.get_stats()
                    files_indexed = len(engine.manifest.get("file_manifest", []))
                    total_symbols = sum(len(s) for s in engine.symbol_table.values())
                    uptime = (datetime.now() - engine.session_start).total_seconds()
                    dup_count = len(engine.curation_report.get("functional_overlaps", []))
                    ov_count = len(engine.curation_report.get("functional_overlaps", []))

                    # Coherence snapshot
                    coherence = {"score": 1.0, "status": "ALIGNED"}
                    if engine.task and engine.srt_tool._seeds:
                        cp = engine.srt_tool.force_reflection()
                        coherence = {"score": cp.coherence_score, "status": cp.coherence_status.value}

                    return self._json({
                        "repo": os.path.basename(engine.repo_path),
                        "system_health": {
                            "status": "Operational",
                            "uptime_seconds": uptime,
                            "watcher": "running",
                            "bridge": "running" if engine.bridge else "not_available",
                            "mcp_server": "available" if hasattr(engine, '_mcp_available') and engine._mcp_available else "not_connected",
                            "auto_dispatch": "disabled (human-in-the-loop)",
                            "auth": "enabled" if engine.auth and getattr(engine.auth, '_tokens', None) else "disabled",
                            "seed_queue": "active" if engine.seed_queue else "not_available",
                        },
                        "local_metrics": {
                            "files_indexed": files_indexed,
                            "total_symbols": total_symbols,
                            "total_seeds": seed_stats.get("total_seeds", 0),
                            "active_seeds": seed_stats.get("active", 0),
                            "bloomed": seed_stats.get("bloomed", 0),
                            "wilted": seed_stats.get("wilted", 0),
                            "success_rate": seed_stats.get("success_rate", 0),
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
                        "task": engine.task,
                        "enforcement": engine.srt_tool.get_compliance_stats(),
                    })

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
                    if engine.task and engine.srt_tool._seeds:
                        cp = engine.srt_tool.force_reflection()
                    
                    self._json({
                        "repo_name": os.path.basename(engine.repo_path),
                        "task": engine.task,
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
                    if engine.task and engine.srt_tool._seeds:
                        cp = engine.srt_tool.force_reflection()
                        if engine.analytics:
                            engine.analytics.record_coherence_snapshot(
                                round(cp.coherence_score * 100), 
                                cp.coherence_status.value
                            )
                        coherence = {"score": cp.coherence_score, "status": cp.coherence_status.value}

                    # Include seed queue stats in status
                    seed_stats = None
                    if engine.seed_queue:
                        seed_stats = engine.seed_queue.get_stats()
                    active_seed = engine._get_active_seed_identity()

                    # Real enforcement data
                    enforcement = engine.srt_tool.get_compliance_stats()
                    # Curation findings
                    dups = engine.curation_report.get("duplicate_files", [])
                    overlaps = engine.curation_report.get("functional_overlaps", [])

                    status_resp = {
                        "product": "SRT-1 v2.0",
                        "repo": os.path.basename(engine.repo_path),
                        "uptime_seconds": (datetime.now() - engine.session_start).total_seconds(),
                        "task": engine.task,
                        "operations_logged": len(engine.operations),
                        "injections_fired": len(engine.injections),
                        "codebase_files": len(engine.manifest.get("file_manifest", [])),
                        "codebase_symbols": sum(len(s) for s in engine.symbol_table.values()),
                        "coherence": coherence,
                        "watcher": "active",
                        "seed_farm": seed_stats,
                        "active_seed": active_seed,
                        "repository_activation": engine._get_repository_activation_status(),
                        "workcells": engine._get_workcell_status(active_seed.get("queue_seed_id") if active_seed else None),
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
                        "build_plan": engine.build_plan,
                        # File tree for dashboard canonical view
                        "file_tree": [
                            {
                                "path": entry.get("file_path", ""),
                                "ext": entry.get("extension", ""),
                                "fidelity": (
                                    "ast" if entry.get("extension") == ".py"
                                    else "deep" if entry.get("file_path", "") in
                                        (engine.manifest.get("semantic_enrichment", {})
                                         .get("deep_analysis", {}))
                                    else "structural"
                                ),
                                "symbols": len(engine.symbol_table.get(entry.get("file_path", ""), []))
                            }
                            for entry in engine.manifest.get("file_manifest", [])
                        ],
                        # Language coverage breakdown
                        "language_coverage": {
                            ext: {
                                "parser": "ast" if ext == ".py" else "regex",
                                "fidelity": "full" if ext == ".py" else "structural",
                                "files": sum(1 for e in engine.manifest.get("file_manifest", []) if e.get("extension") == ext),
                                "symbols": sum(len(engine.symbol_table.get(e.get("file_path", ""), [])) for e in engine.manifest.get("file_manifest", []) if e.get("extension") == ext)
                            }
                            for ext in set(e.get("extension", "") for e in engine.manifest.get("file_manifest", []))
                        },
                        "events_recent": [], # Handled by /events directly now
                    }
                    # Attach optional external trust provenance when configured.
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
                    # Full event log from the in-memory Core event cache.
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
                        "task": {"description": engine.task, "ops": len(engine.operations)},
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

                elif path.startswith("/api/v1/memory/recall/"):
                    from urllib.parse import parse_qs as _pq

                    seed_id = path.rsplit("/", 1)[-1]
                    query = _pq(urlparse(self.path).query)
                    try:
                        limit = int(query.get("limit", ["3"])[0])
                    except (TypeError, ValueError):
                        limit = 3

                    self._json(engine._build_recall_response(seed_id, limit=limit))

                elif path == "/api/v1/repositories":
                    self._json(engine._get_repository_activation_status())

                elif path == "/api/v1/workcells":
                    self._json(engine._get_workcell_status() or {
                        "workcell_count": 0,
                        "execution_count": 0,
                        "workcells": [],
                        "executions": [],
                    })

                elif path == "/api/v1/assistant-adapters":
                    self._json(engine._get_assistant_adapter_config())

                elif path == "/api/v1/change-proposals":
                    query = parse_qs(urlparse(self.path).query)
                    queue_seed_id = (query.get("queue_seed_id") or [None])[0]
                    self._json(engine._list_change_proposals(queue_seed_id=queue_seed_id))

                elif path.startswith("/api/v1/change-proposals/"):
                    proposal_id = path[len("/api/v1/change-proposals/"):].strip("/")
                    result = engine._get_change_proposal(proposal_id)
                    status_code = 200 if result.get("status") != "not_found" else 404
                    self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/proposals"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/proposals")].strip("/")
                    self._json(engine._list_change_proposals(queue_seed_id=queue_seed_id))

                elif path.startswith("/api/v1/workcells/") and path.endswith("/package/workcell-md"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/package/workcell-md")].strip("/")
                    result = engine._get_workcell_md_preview(queue_seed_id)
                    status_code = 200 if result.get("status") == "ok" else 404
                    self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/workspace"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/workspace")].strip("/")
                    result = engine._get_workcell_workspace(queue_seed_id)
                    status_code = 200 if result.get("status") == "ok" else 404
                    self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/activity"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/activity")].strip("/")
                    query = parse_qs(urlparse(self.path).query)
                    try:
                        limit = int(query.get("limit", ["100"])[0])
                        offset = int(query.get("offset", ["0"])[0])
                    except (TypeError, ValueError):
                        limit, offset = 100, 0
                    result = engine._get_workcell_activity(queue_seed_id, limit=limit, offset=offset)
                    status_code = 200 if result.get("status") == "ok" else 404
                    self._json(result, status_code)

                # NOTE: /admin/stats handler consolidated above (line ~1668). Dead duplicate removed.

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
                    if engine.task and engine.srt_tool._seeds:
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
                        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                        self.send_header("Pragma", "no-cache")
                        self.send_header("Expires", "0")
                        self.end_headers()
                        with open(dp, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "Developer dashboard not found"}, 404)

                elif path == "/download/srt1-core.zip":
                    zip_path = os.path.join(engine.repo_path, "srt1-core.zip")
                    if os.path.exists(zip_path):
                        self.send_response(200)
                        self.send_header("Content-Type", "application/zip")
                        self.send_header("Content-Disposition", 'attachment; filename="srt1-core.zip"')
                        self.end_headers()
                        with open(zip_path, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        import io
                        import zipfile

                        allowed_roots = {
                            "docs",
                            "srt1_code_indexer",
                            "srt1_platform",
                            "srt1_pro",
                            "srt1-skills",
                            "tests",
                        }
                        allowed_files = {
                            "AGENTS.md",
                            "BUILD.md",
                            "CLAUDE.md",
                            "Install-SRT1.ps1",
                            "LICENSE",
                            "MANIFEST.in",
                            "README.md",
                            "pyproject.toml",
                            "setup.py",
                            "srt1.bat",
                            "START_SRT1.bat",
                        }
                        excluded_dirs = {
                            ".git",
                            ".pytest_cache",
                            ".srt1",
                            "__pycache__",
                            "build",
                            "dist",
                            "memory",
                            "scia_memory",
                            "scia_security",
                            "scratch",
                            "scratch_ledger_test",
                            "sion_output",
                            "SRT1_CORE.egg-info",
                        }
                        excluded_suffixes = {
                            ".bak",
                            ".db",
                            ".log",
                            ".pyc",
                        }
                        excluded_files = {
                            ".env",
                            "debug.log",
                            "project_code.txt",
                            "pytest_output.txt",
                            "srt1_audit_delta.json",
                            "srt1_cloud.db",
                            "srt1_code_manifest.json",
                            "scratch.html",
                            "unknown_to_ast.py",
                        }

                        buffer = io.BytesIO()
                        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                            for root_name in sorted(allowed_roots):
                                root_path = os.path.join(engine.repo_path, root_name)
                                if not os.path.isdir(root_path):
                                    continue
                                for dirpath, dirnames, filenames in os.walk(root_path):
                                    dirnames[:] = [
                                        d for d in dirnames
                                        if d not in excluded_dirs and not d.startswith(".")
                                    ]
                                    for filename in filenames:
                                        if filename in excluded_files or any(filename.endswith(suffix) for suffix in excluded_suffixes):
                                            continue
                                        file_path = os.path.join(dirpath, filename)
                                        rel_path = os.path.relpath(file_path, engine.repo_path)
                                        archive.write(file_path, rel_path)
                            for filename in sorted(allowed_files):
                                file_path = os.path.join(engine.repo_path, filename)
                                if os.path.isfile(file_path):
                                    archive.write(file_path, filename)

                        data = buffer.getvalue()
                        self.send_response(200)
                        self.send_header("Content-Type", "application/zip")
                        self.send_header("Content-Disposition", 'attachment; filename="srt1-core.zip"')
                        self.send_header("Content-Length", str(len(data)))
                        self.end_headers()
                        self.wfile.write(data)

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
                    mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "srt1_platform", "pwa", "mobile.html")
                    if not os.path.exists(mp):
                        mp = os.path.join(engine.repo_path, "srt1_platform", "pwa", "mobile.html")
                    if not os.path.exists(mp):
                        mp = os.path.join(engine.repo_path, "SRT1-CORE", "srt1_platform", "pwa", "mobile.html")
                    if os.path.exists(mp):
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        # Force no-cache — prevent stale Service Worker from serving old version
                        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                        self.send_header("Pragma", "no-cache")
                        self.send_header("Expires", "0")
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

                # ── Continuity Observatory Endpoints (GET-only, detective-only) ──

                elif path == "/api/continuity":
                    # Compute canonical document freshness and stabilization posture.
                    # This endpoint reports divergence. It does not fix divergence.
                    import time as _time
                    STALENESS_THRESHOLD_HOURS = 24
                    canonical_docs = [
                        "SRT1_CURRENT_STATE.md",
                        "SRT1_DECISIONS.md",
                        "SRT1_FRONTIER.md",
                        "SRT1_CONTEXT_INDEX.md",
                        "SRT1_CONSTITUTION.md",
                    ]
                    documents = []
                    for doc_name in canonical_docs:
                        doc_path = os.path.join(engine.repo_path, doc_name)
                        if os.path.exists(doc_path):
                            try:
                                mtime = os.path.getmtime(doc_path)
                                age_hours = (_time.time() - mtime) / 3600
                                if age_hours < STALENESS_THRESHOLD_HOURS:
                                    freshness = "FRESH"
                                else:
                                    freshness = "STALE"
                                from datetime import datetime as _dt
                                last_mod = _dt.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                                if age_hours < 1:
                                    age_display = f"{int(age_hours * 60)}m ago"
                                elif age_hours < 24:
                                    age_display = f"{age_hours:.1f}h ago"
                                else:
                                    age_display = f"{age_hours / 24:.1f}d ago"
                                documents.append({
                                    "name": doc_name,
                                    "freshness": freshness,
                                    "last_modified": last_mod,
                                    "age_hours": round(age_hours, 2),
                                    "age_display": age_display,
                                })
                            except OSError:
                                documents.append({
                                    "name": doc_name,
                                    "freshness": "DEGRADED",
                                    "last_modified": None,
                                    "age_hours": None,
                                    "age_display": "read error",
                                })
                        else:
                            documents.append({
                                "name": doc_name,
                                "freshness": "DEGRADED",
                                "last_modified": None,
                                "age_hours": None,
                                "age_display": "missing",
                            })

                    # Compute overall freshness
                    states = [d["freshness"] for d in documents]
                    if all(s == "FRESH" for s in states):
                        overall = "FRESH"
                    elif any(s == "DEGRADED" for s in states):
                        overall = "DEGRADED"
                    elif any(s == "STALE" for s in states):
                        overall = "STALE"
                    else:
                        overall = "UNKNOWN"

                    # Read constitution version if available
                    const_ver = "?"
                    const_path = os.path.join(engine.repo_path, "SRT1_CONSTITUTION.md")
                    if os.path.exists(const_path):
                        try:
                            with open(const_path, "r", encoding="utf-8") as cf:
                                for line in cf:
                                    if "CONSTITUTION_VERSION" in line:
                                        const_ver = line.split("**")[-2].strip() if "**" in line else line.split(":")[-1].strip()
                                        break
                        except Exception:
                            pass

                    # Stabilization posture (read from canonical state)
                    posture = []
                    stab_phase = "UNKNOWN"
                    state_path = os.path.join(engine.repo_path, "SRT1_CURRENT_STATE.md")
                    if os.path.exists(state_path):
                        try:
                            with open(state_path, "r", encoding="utf-8") as sf:
                                for line in sf:
                                    line = line.strip()
                                    if line.startswith("- **") and ":**" in line:
                                        parts = line.split(":**")
                                        if len(parts) == 2:
                                            label = parts[0].replace("- **", "").strip()
                                            value = parts[1].strip().rstrip(".")
                                            posture.append({"label": label, "value": value})
                                            if "Plateau" in label and "ACTIVE" in value:
                                                stab_phase = "ACTIVE"
                        except Exception:
                            pass

                    consistency_checks = []

                    self._json({
                        "freshness_state": overall,
                        "stabilization_phase": stab_phase,
                        "constitution_version": const_ver,
                        "data_source": "engine/canonical_docs",
                        "last_checked": _dt.now().isoformat(),
                        "documents": documents,
                        "posture": posture,
                        "consistency_checks": consistency_checks,
                    })

                # ── Workspace Constellation Endpoints ──

                elif path == "/api/constellation":
                    # NOTE: This is the backbone of the Constellation view.
                    # It reads the shared OperationalRegistry (~/.srt1/registry.json)
                    # to discover ALL running SRT-1 engines across the machine,
                    # then queries each one's /status endpoint for live metrics.
                    # This is what enables the "network of sandboxes" visualization.
                    import urllib.request
                    
                    constellation_data = {
                        "this_engine": {
                            "engine_id": getattr(engine, '_engine_id', None),
                            "port": engine.port,
                            "workspace": engine.repo_path,
                            "workspace_name": os.path.basename(engine.repo_path),
                        },
                        "engines": [],
                        "dependencies": {},
                        "cross_module_calls": [],
                        "summary": {},
                    }

                    # 1. Read OperationalRegistry for all known engines
                    if OperationalRegistry:
                        try:
                            registry = OperationalRegistry()
                            registry.cleanup_stale()
                            all_data = registry.get_all_engines()
                            now = datetime.now(timezone.utc) if hasattr(datetime, 'now') else datetime.utcnow()
                            
                            for eid, entry in all_data.get("engines", {}).items():
                                engine_info = {
                                    "engine_id": eid,
                                    "port": entry.get("port"),
                                    "workspace_path": entry.get("workspace_path", ""),
                                    "workspace_name": entry.get("workspace_name", ""),
                                    "status": entry.get("status", "UNKNOWN"),
                                    "manifest_hash": entry.get("manifest_hash", "")[:16],
                                    "registered_at": entry.get("registered_at"),
                                    "last_heartbeat": entry.get("last_heartbeat"),
                                    "pid": entry.get("pid"),
                                    # Live metrics — populated below if engine is reachable
                                    "live": None,
                                }

                                # 2. Query each RUNNING engine's /status for live data
                                # NOTE: This is cross-engine HTTP — each sandbox is truly
                                # independent and only talks via localhost HTTP. No filesystem coupling.
                                if entry.get("status") == "RUNNING" and entry.get("port"):
                                    try:
                                        status_url = f"http://127.0.0.1:{entry['port']}/status"
                                        req = urllib.request.Request(status_url, method="GET")
                                        req.add_header("User-Agent", "SRT1-Constellation/1.0")
                                        with urllib.request.urlopen(req, timeout=2) as resp:
                                            if resp.status == 200:
                                                live_data = json.loads(resp.read().decode())
                                                engine_info["live"] = {
                                                    # NOTE: /status uses codebase_files, codebase_symbols
                                                    # and enforcement.health.duplicates for violations
                                                    "files": live_data.get("codebase_files", 0),
                                                    "symbols": live_data.get("codebase_symbols", 0),
                                                    "violations": live_data.get("enforcement", {}).get("health", {}).get("duplicates", 0) if isinstance(live_data.get("enforcement"), dict) else 0,
                                                    "coherence": live_data.get("coherence", {}).get("label", "?") if isinstance(live_data.get("coherence"), dict) else str(live_data.get("coherence", "?")),
                                                }
                                    except Exception:
                                        # Engine registered but not responding — mark as stale
                                        engine_info["status"] = "STALE"
                                
                                constellation_data["engines"].append(engine_info)
                        except Exception as e:
                            constellation_data["registry_error"] = str(e)

                    # 3. Read workspace connector report for dependency edges
                    # NOTE: This file is generated by running:
                    #   python -m srt1_pro.workspace_connector --root .
                    # It contains the cross-module import map.
                    ws_report_path = os.path.join(engine.repo_path, ".srt1", "workspace_report.json")
                    if os.path.exists(ws_report_path):
                        try:
                            with open(ws_report_path, "r", encoding="utf-8") as wf:
                                ws_data = json.load(wf)
                                constellation_data["dependencies"] = ws_data.get("dependencies", {})
                                constellation_data["cross_module_calls"] = ws_data.get("cross_module_calls", [])
                                constellation_data["workspace_name"] = ws_data.get("workspace", "")
                        except Exception:
                            pass

                    # 4. Summary stats
                    engines = constellation_data["engines"]
                    running = [e for e in engines if e["status"] == "RUNNING"]
                    constellation_data["summary"] = {
                        "total_engines": len(engines),
                        "running_engines": len(running),
                        "total_files": sum((e.get("live") or {}).get("files", 0) for e in running),
                        "total_symbols": sum((e.get("live") or {}).get("symbols", 0) for e in running),
                        "cross_module_deps": len(constellation_data.get("cross_module_calls", [])),
                        "has_workspace_config": os.path.exists(ws_report_path),
                    }

                    self._json(constellation_data)

                elif path == "/constellation":
                    # Workspace Constellation — the command center for all engines
                    # NOTE: This is Level 2 in the navigation hierarchy.
                    # It sits above the per-module dashboard and below any
                    # future full-system supervisory view.
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    core_dir = os.path.dirname(script_dir)
                    candidates = [
                        os.path.join(core_dir, "srt1_platform", "pwa", "constellation.html"),
                        os.path.join(engine.repo_path, "srt1_platform", "pwa", "constellation.html"),
                    ]
                    const_path = None
                    for c in candidates:
                        if os.path.exists(c):
                            const_path = c
                            break
                    if const_path:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        with open(const_path, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "Workspace Constellation not found"}, 404)

                elif path == "/observatory":
                    # Continuity Observatory — separate page from dashboard
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    core_dir = os.path.dirname(script_dir)
                    candidates = [
                        os.path.join(core_dir, "srt1_platform", "pwa", "observatory.html"),
                        os.path.join(engine.repo_path, "srt1_platform", "pwa", "observatory.html"),
                    ]
                    obs_path = None
                    for c in candidates:
                        if os.path.exists(c):
                            obs_path = c
                            break
                    if obs_path:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        with open(obs_path, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({"error": "Continuity Observatory not found"}, 404)

                else:
                    import posixpath
                    from urllib.parse import unquote
                    serve_path = path
                    if serve_path == "/":
                        serve_path = "/dashboard.html"
                    
                    serve_path = posixpath.normpath(unquote(serve_path))
                    if serve_path.startswith('/'):
                        serve_path = serve_path[1:]
                    
                    # Consumer pages accessible under /consumer/ prefix
                    consumer_prefix = "consumer/"
                    actual_path = None
                    if serve_path.startswith(consumer_prefix):
                        consumer_file = serve_path[len(consumer_prefix):]
                        consumer_path = os.path.join(engine.repo_path, "seed-reflection", consumer_file)
                        if os.path.exists(consumer_path) and os.path.isfile(consumer_path):
                            actual_path = consumer_path
                    
                    # Dashboard PWA is the primary source for the engine homepage
                    if not actual_path:
                        pkg_pwa = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "srt1_platform", "pwa", serve_path)
                        if os.path.exists(pkg_pwa) and os.path.isfile(pkg_pwa):
                            actual_path = pkg_pwa
                            
                    if not actual_path:
                        dev_path = os.path.join(engine.repo_path, "srt1_platform", "pwa", serve_path)
                        if os.path.exists(dev_path) and os.path.isfile(dev_path):
                            actual_path = dev_path
                    
                    # Fallback: SRT1-CORE/srt1_platform/pwa
                    if not actual_path:
                        core_dev = os.path.join(engine.repo_path, "SRT1-CORE", "srt1_platform", "pwa", serve_path)
                        if os.path.exists(core_dev) and os.path.isfile(core_dev):
                            actual_path = core_dev
                    
                    if actual_path:
                        ext = os.path.splitext(actual_path)[1].lower()
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
                        with open(actual_path, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self._json({
                            "product": "SRT-1 v2.0",
                            "endpoints": {
                                "GET": [
                                    "/status", "/context", "/synopsis", "/manifest",
                                    "/dashboard", "/consumer", "/admin", "/health", "/observatory",
                                    "/constellation", "/api/constellation",
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
                print(f"DEBUG: do_POST called with path: {path} (raw self.path: {self.path})")

                # Optional private proxy routing. Public Core fails closed when absent.
                if path.startswith("/v1/"):
                    try:
                        from srt1_platform.proxy_engine import SCIAProxyEngine
                        # Hand over the HTTP Request object (self) and the engine context
                        SCIAProxyEngine.handle_proxy_request(self, engine)
                    except ImportError:
                        # Graceful degradation for public Core.
                        self.send_response(402)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        msg = {
                            "error": "Private proxy integration unavailable",
                            "message": "Public Core does not ship the managed proxy backend.",
                        }
                        self.wfile.write(json.dumps(msg).encode("utf-8"))
                    return

                if path == "/enforcement/override":
                    pass # Preserve legacy override route behavior.
                elif not self._check_auth(path):
                    return

                body = self._body()

                if path == "/api/v1/enforcement/nudge/toggle":
                    enabled = body.get("enabled", True)
                    engine.enforcement_nudge_enabled = bool(enabled)
                    return self._json({"status": "success", "nudge_enabled": engine.enforcement_nudge_enabled})

                elif path == "/api/v1/assistant-adapters":
                    result = engine._configure_assistant_adapters(body.get("assistant_adapters") or body.get("adapters") or [])
                    status_code = 200 if result.get("status") == "configured" else 400
                    return self._json(result, status_code)

                elif path.startswith("/api/v1/change-proposals/") and path.endswith("/review"):
                    proposal_id = path[len("/api/v1/change-proposals/"):-len("/review")].strip("/")
                    result = engine._review_change_proposal(
                        proposal_id,
                        action=body.get("action"),
                        actor=body.get("actor") or "human",
                        reason=body.get("reason") or "",
                    )
                    status_code = 200 if result.get("status") not in {"error", "not_found", "invalid_action", "blocked"} else 409
                    return self._json(result, status_code)

                elif path.startswith("/api/v1/change-proposals/") and path.endswith("/apply"):
                    proposal_id = path[len("/api/v1/change-proposals/"):-len("/apply")].strip("/")
                    result = engine._apply_change_proposal(
                        proposal_id,
                        actor=body.get("actor") or "human",
                    )
                    status_code = 200 if result.get("status") not in {"error", "not_found", "invalid_action", "blocked"} else 409
                    return self._json(result, status_code)

                elif path in {"/api/v1/slack/seed", "/api/v1/slack/command"}:
                    result = engine._plant_slack_seed(body)
                    status_code = 200 if result.get("status") == "seed_planted" else 400
                    return self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/repair-package"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/repair-package")].strip("/")
                    result = engine._repair_workcell_package(queue_seed_id)
                    status_code = 200 if result.get("status") in {"repaired", "degraded"} else 404
                    return self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/action"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/action")].strip("/")
                    result = engine._control_workcell_execution(
                        queue_seed_id,
                        action=body.get("action"),
                        actor=body.get("actor") or "human",
                        reason=body.get("reason") or "",
                    )
                    status_code = 200 if result.get("status") not in {
                        "error", "not_found", "invalid_action", "blocked"
                    } else 409
                    return self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/ack"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/ack")].strip("/")
                    result = engine._acknowledge_workcell_execution_job(
                        queue_seed_id,
                        acknowledgement=body.get("acknowledgement") or body.get("status") or "acknowledged",
                        job_id=body.get("job_id"),
                        actor=body.get("actor") or "assistant_runtime",
                        message=body.get("message") or "",
                        metadata=body.get("metadata") if isinstance(body.get("metadata"), dict) else {},
                    )
                    status_code = 200 if result.get("status") not in {
                        "error", "not_found", "invalid_acknowledgement"
                    } else 409
                    return self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/verify"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/verify")].strip("/")
                    result = engine._verify_workcell_execution(
                        queue_seed_id,
                        verified=body.get("verified", True),
                        actor=body.get("actor") or "dashboard_human",
                        details=body.get("details") if isinstance(body.get("details"), dict) else {},
                    )
                    status_code = 200 if result.get("status") not in {
                        "error", "not_found"
                    } else 409
                    return self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/dispatch"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/dispatch")].strip("/")
                    result = engine._dispatch_existing_workcell_execution(
                        queue_seed_id,
                        assistant_credentials=body.get("assistant_credentials"),
                        actor=body.get("actor") or "dashboard_human",
                        background=True,
                    )
                    status_code = 200 if result.get("status") in {
                        "dispatch_started", "dispatched"
                    } else 409
                    return self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and any(
                    path.endswith(suffix) for suffix in ("/pause", "/stop", "/cancel")
                ):
                    for suffix, action in (("/pause", "pause"), ("/stop", "stop"), ("/cancel", "cancel")):
                        if path.endswith(suffix):
                            queue_seed_id = path[len("/api/v1/workcells/"):-len(suffix)].strip("/")
                            result = engine._control_workcell_execution(
                                queue_seed_id,
                                action=action,
                                actor=body.get("actor") or "human",
                                reason=body.get("reason") or "",
                            )
                            status_code = 200 if result.get("status") not in {
                                "error", "not_found", "invalid_action", "blocked"
                            } else 409
                            return self._json(result, status_code)

                elif path.startswith("/api/v1/workcells/") and path.endswith("/validate-writes"):
                    queue_seed_id = path[len("/api/v1/workcells/"):-len("/validate-writes")].strip("/")
                    result = engine._validate_workcell_writes(
                        queue_seed_id,
                        proposed_paths=body.get("paths") or body.get("proposed_paths") or [],
                        actor=body.get("actor") or "assistant_runtime",
                    )
                    status_code = 200 if result.get("allowed") else 409
                    return self._json(result, status_code)

                elif path == "/api/v1/repositories/register-current":
                    result = engine._refresh_repository_activation()
                    status_code = 200 if result.get("status") in {"ready", "registered"} else 500
                    return self._json(result, status_code)

                elif path == "/api/v1/repositories/register-path":
                    result = engine._register_repository_path(body.get("path"))
                    status_code = 200 if result.get("status") in {"ready", "registered"} else 400
                    return self._json(result, status_code)

                elif path == "/api/v1/repositories/browse-folder":
                    result = engine._browse_repository_folder()
                    status_code = 200 if result.get("status") in {"ready", "registered", "cancelled"} else 400
                    return self._json(result, status_code)

                elif path == "/api/v1/repositories/activate":
                    repo_id = body.get("repo_id")
                    result = engine._activate_repository(repo_id)
                    status_code = 200 if result.get("status") in {"ready", "registered"} else 404
                    return self._json(result, status_code)

                elif path == "/api/v1/repositories/launch":
                    repo_id = body.get("repo_id")
                    result = engine._launch_repository_runtime(repo_id)
                    status_code = 200 if result.get("status") in {"ready", "running", "launching"} else 400
                    return self._json(result, status_code)

                elif path == "/api/v1/repositories/stop-runtime":
                    repo_id = body.get("repo_id")
                    result = engine._stop_repository_runtime(repo_id)
                    status_code = 200 if result.get("status") in {"stopped", "not_running"} else 400
                    return self._json(result, status_code)

                elif path == "/api/v1/runtime/shutdown":
                    result = engine._shutdown_current_runtime()
                    return self._json(result, 200)

                elif path == "/api/v1/auth/signup":
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
                    source = body.get("source", "api")
                    is_remediation_seed = engine._is_remediation_seed_payload(body)
                    block = None if is_remediation_seed else engine.srt_tool.check_enforcement("seed_dispatch")
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
                    priority = body.get("priority", 5)
                    auto_dispatch = body.get("auto_dispatch", True)
                    template_id = body.get("template_id")  # Optional: use specific template
                    queue_seed_id = engine._plant_seed(
                        task, source=source, priority=priority,
                        auto_dispatch=auto_dispatch,
                        template_id=template_id,
                        assistant_credentials=body.get("assistant_credentials"),
                    )
                    engine.task = task
                    threading.Thread(target=engine._generate_context_files, daemon=True).start()
                    response = engine._build_task_response(
                        task=task,
                        queue_seed_id=queue_seed_id,
                        auto_dispatch=auto_dispatch,
                    )
                    credential_summary = engine._normalize_assistant_credentials(
                        body.get("assistant_credentials")
                    )
                    response["assistant_credentials"] = {
                        "mode": credential_summary["mode"],
                        "providers": credential_summary["providers"],
                        "secret_persisted": False,
                    }
                    # Attach optional external trust provenance when configured.
                    if engine.signing_client:
                        try:
                            sig = engine.signing_client.sign(
                                {"task": task, "seed_id": engine.task_seed_id, "source": source},
                                operation_type="seed_dispatch"
                            )
                            if sig:
                                response["_provenance"] = sig.to_dict() if hasattr(sig, "to_dict") else str(sig)
                        except Exception as e:
                            logger.error(f"External signing failed: {e}")
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
                        # Attach optional external trust provenance when configured.
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
                    
                    if event_id == "MODIFIED_UNAUTHORIZED":
                        blocks = engine.srt_tool.get_active_blocks()
                        if blocks:
                            event_id = blocks[-1].event_id
                            
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
                        # Attach optional external trust provenance when configured.
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
                    old = engine.task
                    engine.task = None
                    engine.task_seed_id = None
                    engine.operations = []
                    engine.injections = []
                    engine.srt_tool = SRT(reflection_interval=engine.REFLECTION_INTERVAL)
                    self._json({"status": "reset", "previous_task": old})

                # ── Seed Queue POST Endpoints ──

                elif path in ("/seeds", "/task", "/api/v1/task"):
                    source = body.get("source", "mobile")
                    is_remediation_seed = engine._is_remediation_seed_payload(body)
                    block = None if is_remediation_seed else engine.srt_tool.check_enforcement("seed_dispatch")
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
                    priority = body.get("priority", 5)
                    tags = body.get("tags", [])

                    auto_dispatch = body.get("auto_dispatch", True)
                    queue_seed_id = engine._plant_seed(
                        intent,
                        source=source,
                        priority=priority,
                        auto_dispatch=auto_dispatch,
                        template_id=body.get("template_id"),
                        assistant_credentials=body.get("assistant_credentials"),
                    )
                    seed_data = engine.seed_queue.get_seed(queue_seed_id) if queue_seed_id else None
                    if hasattr(seed_data, "to_dict"):
                        seed_data = seed_data.to_dict()
                    response = engine._build_task_response(
                        task=intent,
                        queue_seed_id=queue_seed_id,
                        auto_dispatch=auto_dispatch,
                    )
                    credential_summary = engine._normalize_assistant_credentials(
                        body.get("assistant_credentials")
                    )
                    response.update({
                        "status": "seed_planted",
                        "seed": seed_data,
                        "tags": tags,
                        "assistant_credentials": {
                            "mode": credential_summary["mode"],
                            "providers": credential_summary["providers"],
                            "secret_persisted": False,
                        },
                        "message": "Seed planted. WorkCell execution prepared.",
                    })
                    self._json(response)

                elif path.startswith("/seeds/") and path.endswith("/complete"):
                    if not engine.seed_queue:
                        self._json({"error": "Seed queue not available"}, 503)
                        return
                    seed_id = path.replace("/seeds/", "").replace("/complete", "")
                    queue_seed_id = engine._resolve_queue_seed_id(seed_id)
                    if not queue_seed_id:
                        self._json({"error": f"Seed {seed_id} not found"}, 404)
                        return
                    summary = body.get("summary", "Manually completed")
                    files_modified = body.get("files_modified", [])
                    engine.seed_queue.propose_completion(
                        queue_seed_id,
                        summary=summary,
                        files_modified=files_modified,
                    )
                    if body.get("review_only") or body.get("awaiting_review"):
                        self._json({
                            "status": "awaiting_review",
                            "seed": engine.seed_queue.get_seed(queue_seed_id),
                            "message": "Completion proposed; awaiting review.",
                        })
                        return
                    engine.seed_queue.record_verification_result(
                        queue_seed_id,
                        verified=body.get("verified", True),
                        details={"source": "manual_complete_route"},
                    )
                    result = engine.seed_queue.accept_completion(
                        queue_seed_id,
                        summary=summary,
                        actor=body.get("actor", "human"),
                    )
                    if result:
                        # Also notify the bridge
                        if engine.bridge:
                            engine.bridge.mark_complete(
                                queue_seed_id, summary=summary,
                                files_modified=files_modified
                            )
                        self._json({
                            "status": "bloomed",
                            "seed": engine.seed_queue.get_seed(queue_seed_id),
                            "message": "🌸 Seed has BLOOMED!",
                        })
                    else:
                        self._json({"error": f"Seed {seed_id} not found"}, 404)

                elif path.startswith("/seeds/") and path.endswith("/fail"):
                    if not engine.seed_queue:
                        self._json({"error": "Seed queue not available"}, 503)
                        return
                    seed_id = path.replace("/seeds/", "").replace("/fail", "")
                    queue_seed_id = engine._resolve_queue_seed_id(seed_id)
                    if not queue_seed_id:
                        self._json({"error": f"Seed {seed_id} not found"}, 404)
                        return
                    reason = body.get("reason", "Manually marked as failed")
                    result = engine.seed_queue.wilt(queue_seed_id, reason=reason)
                    if result:
                        if engine.bridge:
                            engine.bridge.mark_failed(queue_seed_id, reason=reason)
                        self._json({
                            "status": "wilted",
                            "seed": engine.seed_queue.get_seed(queue_seed_id),
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

        import socket
        while True:
            try:
                server = ThreadedServer(("127.0.0.1", self.port), Handler)
                self._http_server = server
                break
            except OSError as e:
                # 98 is EADDRINUSE on Linux/Mac, 10048 is WSAEADDRINUSE on Windows
                if e.errno == 98 or e.errno == 10048:
                    print(f"  Port {self.port} in use. Falling back to {self.port + 1}...")
                    self.port += 1
                else:
                    raise

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n  SRT-1 stopped.")
            self._watcher_running = False
            server.server_close()

    def _get_dashboard_path(self) -> Optional[str]:
        """Find the developer dashboard HTML file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        core_dir = os.path.dirname(script_dir)
        candidates = [
            # pip-installed package location
            os.path.join(core_dir, "srt1_platform", "pwa", "dashboard.html"),
            os.path.join(self.repo_path, "srt1_platform", "pwa", "dashboard.html"),
            os.path.join(self.repo_path, "SRT1-CORE", "srt1_platform", "pwa", "dashboard.html"),
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
        print("  ║   Repo Continuity and Alignment for AI Assistants    ║")
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
        print("  ║                 SRT-1 CORE ENGINE IS LIVE           ║")
        print("  ╚══════════════════════════════════════════════════════╝")
        print()
        print(f"  Constellation: http://127.0.0.1:{self.port}/constellation")
        print(f"  Developer:     http://127.0.0.1:{self.port}/dashboard")
        print(f"  Observatory:   http://127.0.0.1:{self.port}/observatory")
        print(f"  Consumer:      http://127.0.0.1:{self.port}/consumer")
        print(f"  Admin:         http://127.0.0.1:{self.port}/admin")
        print(f"  Mobile:        http://127.0.0.1:{self.port}/mobile")
        print(f"  API:           http://127.0.0.1:{self.port}/status")
        print(f"  Seeds:         http://127.0.0.1:{self.port}/seeds")
        print()
        context_result = getattr(self, "_last_context_generation", {})
        written = context_result.get("files_written") or []
        print("  Assistant context:")
        if written:
            for filename in written:
                print(f"    ✓ {filename}")
        else:
            print(f"    ○ No assistant files updated ({context_result.get('reason', 'no writable context target')})")
        print()
        print("  Core Runtime:")
        print(f"    {'✓' if self.auth else '○'} Auth Surface        {'(enabled)' if self.auth else '(optional / unavailable)'}")
        print(f"    {'✓' if self.seed_queue else '○'} Seed Queue          {'(active)' if self.seed_queue else '(legacy fallback)'}")
        print(f"    {'✓' if self.bridge else '○'} Execution Bridge    {'(optional / connected)' if self.bridge else '(inactive)'}")
        print()
        print("  File watcher active. Changes auto-regenerate everything.")
        print()
        print("  Trust:      Core records trust state; external signing is optional.")
        print()
        print("  Press Ctrl+C to stop.")
        print()


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    import sys
    import os
    import json
    
    # ── INIT COMMAND INTERCEPT ──
    if len(sys.argv) > 1 and sys.argv[1] == "init":
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
    parser.description = "SRT-1 Core - local repo-continuity and alignment engine"
    parser.epilog = (
        "Initialization (Run Once):\n"
        "  srt1-code-indexer init\n\n"
        "Local repo-continuity engine:\n"
        "  srt1-code-indexer --repo_path .\n"
        "  srt1-code-indexer --repo_path . --task 'Fix login bug' --port 8080\n"
    )
    parser.add_argument("--repo_path", required=True, help="Path to the repository")
    parser.add_argument("--task", help="Current active task (optional override)")
    parser.add_argument("--port", type=int, default=7483, help="Server port (default: 7483)")
    args = parser.parse_args()

    engine = SRT1Engine(repo_path=args.repo_path, task=args.task, port=args.port)
    init_db()

    # ── FIRST-RUN TELEMETRY CONSENT ──
    # Only ask once. If consent file exists, skip entirely.
    consent_path = SRT1Engine._get_consent_path(args.repo_path)
    if not os.path.exists(consent_path):
        print()
        print("  ┌──────────────────────────────────────────────────────────┐")
        print("  │           SRT-1 Anonymous Telemetry (Optional)          │")
        print("  └──────────────────────────────────────────────────────────┘")
        print()
        print("  SRT-1 can send anonymous usage statistics once per day")
        print("  to help improve the product. Here is EXACTLY what is sent:")
        print()
        print("    ✓ Anonymous UUID (random, not tied to your identity)")
        print("    ✓ File count (number only, not file names)")
        print("    ✓ Symbol count")
        print("    ✓ Violation count")
        print("    ✓ OS type (Windows/Mac/Linux)")
        print("    ✓ SRT-1 version")
        print()
        print("  NEVER sent: file names, paths, source code, function")
        print("  names, repo names, or anything identifying you or your")
        print("  project. Every payload is logged to your dashboard so")
        print("  you can see exactly what was transmitted.")
        print()

        try:
            answer = input("  Allow anonymous telemetry? [Y/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = "n"

        consented = answer not in ("n", "no")
        SRT1Engine._save_telemetry_consent(os.path.abspath(args.repo_path), consented)

        if consented:
            # Store the anonymous ID in the consent file
            import uuid as _uuid
            consent_data_path = SRT1Engine._get_consent_path(os.path.abspath(args.repo_path))
            try:
                with open(consent_data_path, "r", encoding="utf-8") as _f:
                    _cdata = json.loads(_f.read())
                _cdata["anonymous_id"] = str(_uuid.uuid4())
                with open(consent_data_path, "w", encoding="utf-8") as _f:
                    _f.write(json.dumps(_cdata, indent=2))
            except Exception:
                pass
            print("\n  ✓ Thank you. Telemetry enabled. Every payload is visible")
            print("    in your dashboard activity feed.\n")
        else:
            print("\n  ✓ Understood. No telemetry will ever be sent.")
            print("    You can change this anytime in .srt1/consent.json\n")

    engine.start()


if __name__ == "__main__":
    main()
