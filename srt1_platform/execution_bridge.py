"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: DATA_MODEL
Key Symbols: DispatchMethod, SCIADispatchBridge, __init__, configure, set_callbacks ... and 21 more

Extracted Purposes:
  - DispatchMethod: Constants for how seeds get dispatched to assistants.
  - SCIADispatchBridge: The Execution Bridge: dispatches seeds and monitors completion.
  - __init__: Args:
  ...
"""
#!/usr/bin/env python3
"""
SRT-1 Execution Bridge — Seed Dispatch & Completion Monitoring
================================================================

This is the bridge between SRT-1 and the AI code assistant.
When a seed is planted (from mobile, API, CLI, or dashboard),
the Execution Bridge:

    1. Takes the seed intent
    2. Generates a full-context blueprint (using SRT-1's codebase knowledge)
    3. Dispatches the blueprint to the code assistant via:
       - File-based dispatch: writes to .srt1/pending_seed.md
       - Context injection: updates AGENTS.md, CLAUDE.md, .cursorrules
       - Direct API: calls assistant's API if available (MCP, etc.)
    4. Monitors for completion (file watcher detects changes)
    5. Auto-advances the seed lifecycle (GROWING → BLOOMED)
    6. Sends notification back (webhook, file signal, or queue update)

The user plants a seed from their phone.
They go about their day.
The code assistant builds it.
The user gets notified: "🌸 BLOOMED — 3 files modified."

This is what makes SRT-1 different from ClawBot and other agents.
SRT-1 doesn't need full system access. It partners with whatever
assistant is already running. It's the connective tissue, not the body.

Author : William Darnell Jernigan IV (Architect)
License: Business Source License 1.1
"""

import os
import json
import time
import hashlib
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

from srt1_platform.assistant_adapters import (
    AssistantAdapterRegistry,
    WorkCellExecutionRequest,
)

logger = logging.getLogger("srt1.bridge")


class DispatchMethod:
    """Constants for how seeds get dispatched to assistants."""
    FILE_BASED = "file_based"         # Write to .srt1/pending_seed.md
    CONTEXT_INJECTION = "context"     # Update AGENTS.md, CLAUDE.md, etc.
    WEBHOOK = "webhook"               # POST to a webhook URL
    MCP = "mcp"                       # Model Context Protocol
    ASSISTANT_ADAPTER = "assistant_adapter"  # Model-agnostic bounded adapters


class SCIADispatchBridge:
    """
    The Execution Bridge: dispatches seeds and monitors completion.
    
    This runs as a background thread inside SRT-1. When a seed is
    planted, the bridge picks it up, generates the blueprint,
    dispatches it, and watches for the assistant to complete it.
    """

    # How often to check for pending seeds
    DISPATCH_INTERVAL = 5  # seconds

    # How often to check for completion signals
    MONITOR_INTERVAL = 10  # seconds

    # After this many seconds with no file changes, consider seed complete
    COMPLETION_QUIET_PERIOD = 120  # 2 minutes of no changes = done

    # Max time before a seed is considered stale
    STALE_TIMEOUT = 3600  # 1 hour

    def __init__(self, repo_path: str, srt1_dir: Optional[str] = None):
        """
        Args:
            repo_path: Path to the repository being worked on
            srt1_dir: Path to .srt1 directory (default: repo_path/.srt1)
        """
        self.repo_path = os.path.abspath(repo_path)
        self.srt1_dir = srt1_dir or os.path.join(self.repo_path, ".srt1")
        os.makedirs(self.srt1_dir, exist_ok=True)

        # Dispatch config
        self.dispatch_methods: List[str] = [
            DispatchMethod.FILE_BASED,
            DispatchMethod.CONTEXT_INJECTION,
        ]

        # Webhook config (optional)
        self.webhook_url: Optional[str] = None
        self.webhook_headers: Dict[str, str] = {}
        self.assistant_adapters: List[Dict[str, Any]] = []

        # Callbacks (set by SRT-1 engine)
        self._on_seed_dispatched: Optional[Callable] = None
        self._on_seed_completed: Optional[Callable] = None
        self._on_seed_failed: Optional[Callable] = None
        self._generate_blueprint: Optional[Callable] = None
        self._get_file_hashes: Optional[Callable] = None

        # Monitoring state
        self._active_dispatches: Dict[str, Dict] = {}  # seed_id -> dispatch info
        self._file_snapshots: Dict[str, Dict[str, str]] = {}  # seed_id -> {filepath: hash}
        self._last_change_time: Dict[str, float] = {}  # seed_id -> timestamp of last file change

        # Threading
        self._running = False
        self._dispatch_thread: Optional[threading.Thread] = None
        self._monitor_thread: Optional[threading.Thread] = None

        # Completion signals directory
        self.signals_dir = os.path.join(self.srt1_dir, "signals")
        os.makedirs(self.signals_dir, exist_ok=True)

        # Load config
        self._load_config()

    # -----------------------------------------------------------------
    # CONFIGURATION
    # -----------------------------------------------------------------

    def configure(self, webhook_url: Optional[str] = None,
                  dispatch_methods: Optional[List[str]] = None,
                  quiet_period: Optional[int] = None,
                  assistant_adapters: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Configure the execution bridge.
        
        Args:
            webhook_url: URL to POST completion notifications
            dispatch_methods: List of dispatch methods to use
            quiet_period: Seconds of no changes before considering complete
            assistant_adapters: Bounded assistant adapter configs
        """
        if webhook_url:
            self.webhook_url = webhook_url
            if DispatchMethod.WEBHOOK not in self.dispatch_methods:
                self.dispatch_methods.append(DispatchMethod.WEBHOOK)

        if dispatch_methods:
            self.dispatch_methods = dispatch_methods

        if quiet_period:
            self.COMPLETION_QUIET_PERIOD = quiet_period

        if assistant_adapters is not None:
            self.assistant_adapters = assistant_adapters
            if self.assistant_adapters and DispatchMethod.ASSISTANT_ADAPTER not in self.dispatch_methods:
                self.dispatch_methods.append(DispatchMethod.ASSISTANT_ADAPTER)
            if not self.assistant_adapters and DispatchMethod.ASSISTANT_ADAPTER in self.dispatch_methods:
                self.dispatch_methods = [
                    method for method in self.dispatch_methods
                    if method != DispatchMethod.ASSISTANT_ADAPTER
                ]

        self._save_config()

    def set_callbacks(self,
                      on_dispatched: Optional[Callable] = None,
                      on_completed: Optional[Callable] = None,
                      on_failed: Optional[Callable] = None,
                      generate_blueprint: Optional[Callable] = None,
                      get_file_hashes: Optional[Callable] = None) -> None:
        """Set callback functions from the SRT-1 engine."""
        if on_dispatched:
            self._on_seed_dispatched = on_dispatched
        if on_completed:
            self._on_seed_completed = on_completed
        if on_failed:
            self._on_seed_failed = on_failed
        if generate_blueprint:
            self._generate_blueprint = generate_blueprint
        if get_file_hashes:
            self._get_file_hashes = get_file_hashes

    # -----------------------------------------------------------------
    # DISPATCH: Send seed to the assistant
    # -----------------------------------------------------------------

    def dispatch_seed(self, seed_id: str, intent: str,
                      blueprint: Optional[str] = None,
                      blueprint_meta: Optional[Dict] = None,
                      execution_context: Optional[Dict[str, Any]] = None,
                      transient_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Dispatch a seed to the code assistant.
        
        This is the core action. It takes the seed intent and blueprint,
        then pushes it through all configured dispatch methods.
        
        Args:
            seed_id: The seed identifier
            intent: What the user wants to build
            blueprint: Pre-generated blueprint text (if None, will generate)
            blueprint_meta: Blueprint metadata (relevant_symbols, etc.)
            execution_context: WorkCell/package metadata for assistant adapters
            
        Returns:
            Dict with dispatch results per method
        """
        results = {}

        # Generate blueprint if not provided
        if not blueprint and self._generate_blueprint:
            bp_result = self._generate_blueprint(intent)
            blueprint = bp_result.get("blueprint", "")
            blueprint_meta = {
                "relevant_symbols": bp_result.get("relevant_symbols", 0),
                "relevant_files": bp_result.get("relevant_files", 0),
                "saved_to": bp_result.get("saved_to", ""),
            }
            
        # Take a snapshot of current file hashes for completion detection
        if self._get_file_hashes:
            self._file_snapshots[seed_id] = dict(self._get_file_hashes())
        self._last_change_time[seed_id] = time.time()

        # Dispatch through each configured method
        for method in self.dispatch_methods:
            try:
                if method == DispatchMethod.FILE_BASED:
                    results[method] = self._dispatch_file_based(seed_id, intent, blueprint)

                elif method == DispatchMethod.CONTEXT_INJECTION:
                    results[method] = self._dispatch_context_injection(seed_id, intent, blueprint)

                elif method == DispatchMethod.WEBHOOK:
                    results[method] = self._dispatch_webhook(seed_id, intent, blueprint)

                elif method == DispatchMethod.MCP:
                    results[method] = self._dispatch_mcp(seed_id, intent, blueprint)

                elif method == DispatchMethod.ASSISTANT_ADAPTER:
                    results[method] = self._dispatch_assistant_adapters(
                        seed_id=seed_id,
                        intent=intent,
                        blueprint=blueprint or "",
                        blueprint_meta=blueprint_meta or {},
                        execution_context=execution_context or {},
                        transient_credentials=transient_credentials or {},
                    )

            except Exception as e:
                results[method] = {"success": False, "error": str(e)}
                logger.error(f"Dispatch via {method} failed: {e}")

        # Track active dispatch
        self._active_dispatches[seed_id] = {
            "intent": intent,
            "dispatched_at": datetime.now().isoformat(),
            "methods": list(results.keys()),
            "results": results,
            "blueprint_meta": blueprint_meta,
        }

        # Notify callback
        if self._on_seed_dispatched:
            self._on_seed_dispatched(seed_id, results)

        logger.info(f"Seed {seed_id} dispatched via {', '.join(results.keys())}")

        return {
            "seed_id": seed_id,
            "dispatched": True,
            "methods": results,
            "monitoring": True,
        }

    def _dispatch_file_based(self, seed_id: str, intent: str,
                              blueprint: str) -> Dict:
        """
        File-based dispatch: write pending seed to .srt1/pending_seed.md
        
        The code assistant (already reading .srt1/) picks this up.
        """
        pending_path = os.path.join(self.srt1_dir, "pending_seed.md")
        active_path = os.path.join(self.srt1_dir, "active_seed.md")

        content = self._build_dispatch_document(seed_id, intent, blueprint)

        # Write both pending and active versions
        with open(pending_path, "w", encoding="utf-8") as f:
            f.write(content)
        with open(active_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "pending_path": pending_path,
            "active_path": active_path,
        }

    def _dispatch_context_injection(self, seed_id: str, intent: str,
                                     blueprint: str) -> Dict:
        """
        Context injection: update the AI context files with the seed task.
        
        This updates AGENTS.md, CLAUDE.md, .cursorrules so ANY assistant
        that reads these files automatically gets the seed.
        """
        # Build task injection block
        task_block = (
            f"\n\n## 🌱 ACTIVE SEED — {seed_id}\n\n"
            f"**TASK:** {intent}\n\n"
            f"**STATUS:** Dispatched, awaiting execution\n\n"
            f"**PRIORITY:** Execute this task NOW. This was planted remotely.\n\n"
            f"When complete, create a file at `.srt1/signals/{seed_id}_done.json` with:\n"
            f"```json\n"
            f'{{"seed_id": "{seed_id}", "status": "complete", '
            f'"files_modified": ["list", "of", "files"], '
            f'"summary": "what was done"}}\n'
            f"```\n\n"
            f"---\n\n"
        )

        files_updated = []
        context_files = [
            os.path.join(self.repo_path, "AGENTS.md"),
            os.path.join(self.repo_path, "CLAUDE.md"),
            os.path.join(self.repo_path, ".cursorrules"),
        ]

        for cf in context_files:
            if os.path.exists(cf):
                try:
                    with open(cf, "r", encoding="utf-8") as f:
                        existing = f.read()

                    # Remove any previous seed injection
                    marker_start = "## 🌱 ACTIVE SEED —"
                    if marker_start in existing:
                        # Find the section and replace it
                        idx = existing.index(marker_start)
                        # Find the end (next ## or end of file)
                        rest = existing[idx:]
                        end_markers = ["\n## ", "\n# "]
                        end_idx = len(rest)
                        for em in end_markers:
                            found = rest.find(em, len(marker_start))
                            if found > 0 and found < end_idx:
                                end_idx = found
                        existing = existing[:idx] + existing[idx + end_idx:]

                    # Inject after the first header
                    first_newline = existing.find("\n\n")
                    if first_newline > 0:
                        updated = existing[:first_newline] + task_block + existing[first_newline:]
                    else:
                        updated = task_block + existing

                    with open(cf, "w", encoding="utf-8") as f:
                        f.write(updated)
                    files_updated.append(cf)
                except IOError:
                    continue

        return {
            "success": True,
            "files_updated": files_updated,
        }

    def _dispatch_webhook(self, seed_id: str, intent: str,
                           blueprint: str) -> Dict:
        """Send seed to a webhook URL (for external integrations)."""
        if not self.webhook_url:
            return {"success": False, "error": "No webhook URL configured"}

        try:
            import urllib.request
            payload = json.dumps({
                "event": "seed_dispatched",
                "seed_id": seed_id,
                "intent": intent,
                "blueprint": blueprint[:5000],  # Truncate for webhook
                "repo": os.path.basename(self.repo_path),
                "timestamp": datetime.now().isoformat(),
            }).encode()

            headers = {
                "Content-Type": "application/json",
                **self.webhook_headers,
            }

            req = urllib.request.Request(self.webhook_url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {"success": True, "status_code": resp.status}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _dispatch_mcp(self, seed_id: str, intent: str,
                       blueprint: str) -> Dict:
        """Dispatch via Model Context Protocol (future integration)."""
        # MCP dispatch is a future capability
        return {
            "success": False,
            "error": "MCP dispatch not yet implemented. Use file-based or context injection.",
        }

    def _dispatch_assistant_adapters(
        self,
        seed_id: str,
        intent: str,
        blueprint: str,
        blueprint_meta: Dict[str, Any],
        execution_context: Dict[str, Any],
        transient_credentials: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Dispatch through model-agnostic assistant adapters."""
        if not self.assistant_adapters:
            return {
                "success": False,
                "error": "No assistant adapters configured",
                "adapters": {},
            }

        signal_path = os.path.join(self.signals_dir, f"{seed_id}_done.json")
        request = WorkCellExecutionRequest(
            seed_id=seed_id,
            intent=intent,
            blueprint=blueprint or "",
            repo_path=self.repo_path,
            srt1_dir=self.srt1_dir,
            workcell_package_path=(
                execution_context.get("workcell_package_path")
                or blueprint_meta.get("workcell_package_path")
                or blueprint_meta.get("package_path")
            ),
            allowed_paths=list(
                execution_context.get("allowed_paths")
                or blueprint_meta.get("allowed_paths")
                or []
            ),
            restricted_paths=list(
                execution_context.get("restricted_paths")
                or blueprint_meta.get("restricted_paths")
                or [".git/", ".srt1/seeds/", ".srt1/runtime/"]
            ),
            completion_signal_path=signal_path,
            trust_state=dict(
                execution_context.get("trust_state")
                or blueprint_meta.get("trust_state")
                or {"signature": "unsigned", "verification": "unverified", "lineage": "missing"}
            ),
            metadata={
                "blueprint_meta": blueprint_meta,
                "execution_context": execution_context,
                "credential_mode": execution_context.get("credential_mode") or "none",
                "credential_provider": execution_context.get("credential_provider") or "",
                "credential_providers": list(execution_context.get("credential_providers") or []),
            },
            transient_credentials=dict(transient_credentials or {}),
        )
        registry = AssistantAdapterRegistry(self.assistant_adapters)
        adapter_results = registry.dispatch_all(request)
        return {
            "success": any(result.get("status") == "dispatched" for result in adapter_results.values()),
            "adapters": adapter_results,
        }

    def _build_dispatch_document(self, seed_id: str, intent: str,
                                  blueprint: str) -> str:
        """Build the document that gets written to .srt1/pending_seed.md."""
        lines = [
            f"# 🌱 Active Seed: {seed_id}",
            f"",
            f"> **AUTO-DISPATCHED by SRT-1 Execution Bridge**",
            f"> Dispatched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> Source: Remote seed planting",
            f"",
            f"## Task",
            f"",
            f"**{intent}**",
            f"",
            f"## Instructions",
            f"",
            f"1. Execute the blueprint below completely.",
            f"2. Follow all existing patterns and conventions.",
            f"3. Do NOT create functions that already exist.",
            f"4. When done, create a completion signal:",
            f"",
            f"   Create `.srt1/signals/{seed_id}_done.json` with:",
            f"   ```json",
            f'   {{"seed_id": "{seed_id}", "status": "complete", '
            f'"files_modified": ["list files here"], '
            f'"summary": "what you did"}}',
            f"   ```",
            f"",
            f"## Blueprint",
            f"",
        ]

        if blueprint:
            lines.append(blueprint)
        else:
            lines.append(f"No blueprint generated. Use your codebase knowledge to implement: **{intent}**")

        lines.extend([
            f"",
            f"---",
            f"*SRT-1 Execution Bridge — {datetime.now().isoformat()}*",
        ])

        return "\n".join(lines)

    # -----------------------------------------------------------------
    # MONITORING: Watch for completion
    # -----------------------------------------------------------------

    def start_monitoring(self) -> None:
        """Start the background monitoring threads."""
        if self._running:
            return

        self._running = True

        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="srt1-bridge-monitor"
        )
        self._monitor_thread.start()

        logger.info("Execution Bridge monitoring started")

    def stop_monitoring(self) -> None:
        """Stop the monitoring threads."""
        self._running = False

    def _monitor_loop(self) -> None:
        """Background loop that checks for seed completion."""
        while self._running:
            try:
                self._check_completion_signals()
                self._check_file_changes()
                self._check_stale_seeds()
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")

            time.sleep(self.MONITOR_INTERVAL)

    def _check_completion_signals(self) -> None:
        """
        Check for explicit completion signals from the code assistant.
        
        The assistant creates .srt1/signals/<seed_id>_done.json when it's
        finished building a seed.
        """
        if not os.path.exists(self.signals_dir):
            return

        for filename in os.listdir(self.signals_dir):
            if not filename.endswith("_done.json"):
                continue

            signal_path = os.path.join(self.signals_dir, filename)
            try:
                with open(signal_path, "r", encoding="utf-8") as f:
                    signal = json.load(f)

                seed_id = signal.get("seed_id", "")
                if seed_id in self._active_dispatches:
                    # Seed completed via explicit signal!
                    self._handle_completion(
                        seed_id=seed_id,
                        files_modified=signal.get("files_modified", []),
                        summary=signal.get("summary", "Completed (signal received)"),
                        method="signal",
                    )

                    # Remove the signal file
                    os.remove(signal_path)

                    # Also remove the pending seed file
                    pending = os.path.join(self.srt1_dir, "pending_seed.md")
                    if os.path.exists(pending):
                        os.remove(pending)

            except (json.JSONDecodeError, IOError):
                continue

    def _check_file_changes(self) -> None:
        """
        Check if files have changed since dispatch (auto-completion detection).
        
        If files are being modified, the seed is GROWING.
        If files stop changing for COMPLETION_QUIET_PERIOD, the seed BLOOMED.
        """
        if not self._get_file_hashes:
            return

        current_hashes = dict(self._get_file_hashes())

        for seed_id in list(self._active_dispatches.keys()):
            if seed_id not in self._file_snapshots:
                continue

            original = self._file_snapshots[seed_id]
            changed_files = []

            for fpath, current_hash in current_hashes.items():
                original_hash = original.get(fpath)
                if original_hash and original_hash != current_hash:
                    changed_files.append(fpath)

            # Also check for new files
            new_files = set(current_hashes.keys()) - set(original.keys())
            changed_files.extend(new_files)

            if changed_files:
                # Files are being modified — seed is GROWING
                self._last_change_time[seed_id] = time.time()

                # Notify callback about file changes
                if self._on_seed_dispatched:
                    # The seed queue will update growth tracking
                    pass

            else:
                # No changes — check if quiet period has elapsed
                last_change = self._last_change_time.get(seed_id, time.time())
                quiet_duration = time.time() - last_change

                if quiet_duration >= self.COMPLETION_QUIET_PERIOD:
                    # Check if ANY files changed since dispatch
                    all_changes = []
                    for fpath, current_hash in current_hashes.items():
                        orig = original.get(fpath)
                        if orig and orig != current_hash:
                            all_changes.append(fpath)

                    if all_changes:
                        # Files were changed and things have been quiet — BLOOMED
                        self._handle_completion(
                            seed_id=seed_id,
                            files_modified=all_changes,
                            summary=f"Auto-detected completion: {len(all_changes)} files modified, "
                                    f"{int(quiet_duration)}s quiet period",
                            method="auto_detect",
                        )

    def _check_stale_seeds(self) -> None:
        """Check for seeds that have been stuck too long."""
        now = time.time()

        for seed_id, dispatch_info in list(self._active_dispatches.items()):
            dispatched_at = dispatch_info.get("dispatched_at", "")
            try:
                dt = datetime.fromisoformat(dispatched_at)
                age_seconds = (datetime.now() - dt).total_seconds()

                if age_seconds > self.STALE_TIMEOUT:
                    logger.warning(f"Seed {seed_id} is stale ({age_seconds/3600:.1f}h old)")

                    # Notify as failed/stale
                    if self._on_seed_failed:
                        self._on_seed_failed(seed_id, f"Stale — no completion after {age_seconds/3600:.1f}h")

            except ValueError:
                pass

    def _handle_completion(self, seed_id: str, files_modified: List[str],
                           summary: str, method: str) -> None:
        """Handle a seed completion event."""
        logger.info(f"🌸 SEED BLOOMED: {seed_id} via {method}")
        logger.info(f"   Files modified: {len(files_modified)}")
        logger.info(f"   Summary: {summary}")
        
        dispatch_info = self._active_dispatches.get(seed_id, {})

        # Record completion
        completion_record = {
            "seed_id": seed_id,
            "completed_at": datetime.now().isoformat(),
            "files_modified": files_modified,
            "summary": summary,
            "detection_method": method,
            "dispatch_info": dispatch_info,
        }

        # Save completion record
        history_dir = os.path.join(self.srt1_dir, "completed_seeds")
        os.makedirs(history_dir, exist_ok=True)
        record_path = os.path.join(history_dir, f"{seed_id}_completed.json")
        try:
            with open(record_path, "w", encoding="utf-8") as f:
                json.dump(completion_record, f, indent=2)
        except IOError:
            pass

        # Notify callback
        if self._on_seed_completed:
            self._on_seed_completed(seed_id, files_modified, summary)

        # Clean up active dispatch
        self._active_dispatches.pop(seed_id, None)
        self._file_snapshots.pop(seed_id, None)
        self._last_change_time.pop(seed_id, None)

        # Send webhook notification
        if self.webhook_url:
            self._notify_completion_webhook(seed_id, files_modified, summary)

        # Clean up context injection
        self._clean_context_injection(seed_id)

    def _notify_completion_webhook(self, seed_id: str, files_modified: List[str],
                                    summary: str) -> None:
        """Send a webhook notification about seed completion."""
        try:
            import urllib.request
            payload = json.dumps({
                "event": "seed_bloomed",
                "seed_id": seed_id,
                "files_modified": files_modified,
                "summary": summary,
                "repo": os.path.basename(self.repo_path),
                "timestamp": datetime.now().isoformat(),
            }).encode()

            req = urllib.request.Request(
                self.webhook_url,
                data=payload,
                headers={"Content-Type": "application/json", **self.webhook_headers},
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")

    def _clean_context_injection(self, seed_id: str) -> None:
        """Remove the seed injection from context files after completion."""
        context_files = [
            os.path.join(self.repo_path, "AGENTS.md"),
            os.path.join(self.repo_path, "CLAUDE.md"),
            os.path.join(self.repo_path, ".cursorrules"),
        ]

        marker = f"## 🌱 ACTIVE SEED — {seed_id}"

        for cf in context_files:
            if not os.path.exists(cf):
                continue
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    content = f.read()

                if marker in content:
                    idx = content.index(marker)
                    rest = content[idx:]
                    end_markers = ["\n## ", "\n# "]
                    end_idx = len(rest)
                    for em in end_markers:
                        found = rest.find(em, len(marker))
                        if 0 < found < end_idx:
                            end_idx = found
                    content = content[:idx] + content[idx + end_idx:]

                    with open(cf, "w", encoding="utf-8") as f:
                        f.write(content)
            except IOError:
                continue

    # -----------------------------------------------------------------
    # ACTIVE DISPATCH QUERIES
    # -----------------------------------------------------------------

    def get_active_dispatches(self) -> List[Dict]:
        """Get all currently active (dispatched, not yet completed) seeds."""
        dispatches = []
        for seed_id, info in self._active_dispatches.items():
            dispatches.append({
                "seed_id": seed_id,
                "intent": info.get("intent", ""),
                "dispatched_at": info.get("dispatched_at", ""),
                "methods": info.get("methods", []),
                "monitoring": True,
            })
        return dispatches

    def is_seed_dispatched(self, seed_id: str) -> bool:
        """Check if a seed is currently dispatched and being monitored."""
        return seed_id in self._active_dispatches

    # -----------------------------------------------------------------
    # MANUAL COMPLETION
    # -----------------------------------------------------------------

    def mark_complete(self, seed_id: str, summary: str = "",
                      files_modified: Optional[List[str]] = None) -> bool:
        """
        Manually mark a seed as complete (when auto-detection isn't used).
        This can be called from the mobile app or API.
        """
        if seed_id not in self._active_dispatches:
            return False

        self._handle_completion(
            seed_id=seed_id,
            files_modified=files_modified or [],
            summary=summary or "Manually marked as complete",
            method="manual",
        )
        return True

    def mark_failed(self, seed_id: str, reason: str = "") -> bool:
        """Manually mark a seed as failed."""
        if seed_id not in self._active_dispatches:
            return False

        if self._on_seed_failed:
            self._on_seed_failed(seed_id, reason or "Manually marked as failed")

        self._active_dispatches.pop(seed_id, None)
        self._file_snapshots.pop(seed_id, None)
        self._last_change_time.pop(seed_id, None)
        return True

    # -----------------------------------------------------------------
    # CONFIG PERSISTENCE
    # -----------------------------------------------------------------

    def _load_config(self) -> None:
        """Load bridge configuration."""
        config_path = os.path.join(self.srt1_dir, "bridge_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.webhook_url = config.get("webhook_url")
                self.webhook_headers = config.get("webhook_headers", {})
                self.dispatch_methods = config.get("dispatch_methods", self.dispatch_methods)
                self.assistant_adapters = config.get("assistant_adapters", [])
                self.COMPLETION_QUIET_PERIOD = config.get("quiet_period", self.COMPLETION_QUIET_PERIOD)
                self.STALE_TIMEOUT = config.get("stale_timeout", self.STALE_TIMEOUT)
            except (json.JSONDecodeError, IOError):
                pass

    def _save_config(self) -> None:
        """Save bridge configuration."""
        config_path = os.path.join(self.srt1_dir, "bridge_config.json")
        try:
            config = {
                "webhook_url": self.webhook_url,
                "webhook_headers": self.webhook_headers,
                "dispatch_methods": self.dispatch_methods,
                "assistant_adapters": self.assistant_adapters,
                "quiet_period": self.COMPLETION_QUIET_PERIOD,
                "stale_timeout": self.STALE_TIMEOUT,
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save bridge config: {e}")
