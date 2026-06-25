"""
SRT-1 Operational Registry
===========================
Lightweight file-based discovery layer for CORE engines.

Every running SRT-1 engine self-registers here on startup, heartbeats
periodically, and deregisters on shutdown. External governance may read
this registry through a bounded HTTP bridge, never via direct filesystem
coupling.

Storage: ~/.srt1/registry.json
Locking: filelock (graceful fallback to no-lock if unavailable)

Copyright 2026 Seed Class Intelligence. All rights reserved.
BSL 1.1 — Source Available. See LICENSE for terms.
"""

import os
import json
import time
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


# ─── CONSTANTS ────────────────────────────────────────────────────

REGISTRY_DIR = os.path.join(os.path.expanduser("~"), ".srt1")
REGISTRY_FILE = os.path.join(REGISTRY_DIR, "registry.json")
DEFAULT_STALE_THRESHOLD = 60  # seconds


# ─── REGISTRY ─────────────────────────────────────────────────────

class OperationalRegistry:
    """
    File-based registry for SRT-1 CORE engine discovery.

    Schema:
        {
            "engines": {
                "<engine_id>": {
                    "port": int,
                    "workspace_path": str,
                    "workspace_name": str,
                    "manifest_hash": str,
                    "status": "RUNNING" | "OFFLINE",
                    "pid": int,
                    "registered_at": str (ISO),
                    "last_heartbeat": str (ISO)
                }
            },
            "last_updated": str (ISO)
        }
    """

    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or REGISTRY_FILE
        self._ensure_dir()

    def _ensure_dir(self):
        """Ensure the registry directory exists."""
        dirpath = os.path.dirname(self.registry_path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

    def _read(self) -> Dict[str, Any]:
        """Read the registry from disk."""
        if not os.path.exists(self.registry_path):
            return {"engines": {}, "last_updated": None}
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"engines": {}, "last_updated": None}

    def _write(self, data: Dict[str, Any]):
        """Write the registry to disk."""
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._ensure_dir()
        # Write atomically: write to temp then rename
        tmp_path = self.registry_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.registry_path)

    # ── Public API ────────────────────────────────────────────────

    @staticmethod
    def generate_engine_id(workspace_path: str, port: int) -> str:
        """Deterministic engine ID from workspace + port."""
        raw = f"{os.path.abspath(workspace_path)}:{port}"
        return "engine_" + hashlib.sha256(raw.encode()).hexdigest()[:12]

    def register_engine(
        self,
        engine_id: str,
        port: int,
        workspace_path: str,
        manifest_hash: str = "",
        workspace_name: str = "",
    ) -> Dict[str, Any]:
        """Register a new engine or re-register an existing one."""
        data = self._read()
        now = datetime.now(timezone.utc).isoformat()

        entry = {
            "port": port,
            "workspace_path": os.path.abspath(workspace_path),
            "workspace_name": workspace_name or os.path.basename(workspace_path),
            "manifest_hash": manifest_hash,
            "status": "RUNNING",
            "pid": os.getpid(),
            "registered_at": now,
            "last_heartbeat": now,
        }

        data["engines"][engine_id] = entry
        self._write(data)
        return entry

    def heartbeat(
        self,
        engine_id: str,
        manifest_hash: str = None,
        status: str = "RUNNING",
    ) -> bool:
        """Update the heartbeat timestamp for an engine. Returns False if engine not found."""
        data = self._read()
        if engine_id not in data["engines"]:
            return False

        data["engines"][engine_id]["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        data["engines"][engine_id]["status"] = status
        data["engines"][engine_id]["pid"] = os.getpid()
        if manifest_hash is not None:
            data["engines"][engine_id]["manifest_hash"] = manifest_hash

        self._write(data)
        return True

    def deregister_engine(self, engine_id: str) -> bool:
        """Mark an engine as OFFLINE. Does not delete it from the registry."""
        data = self._read()
        if engine_id not in data["engines"]:
            return False

        data["engines"][engine_id]["status"] = "OFFLINE"
        data["engines"][engine_id]["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        self._write(data)
        return True

    def get_active_engines(
        self, stale_threshold_seconds: int = DEFAULT_STALE_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """Return engines whose last heartbeat is within the threshold."""
        data = self._read()
        now = datetime.now(timezone.utc)
        active = []

        for eid, entry in data["engines"].items():
            if entry.get("status") != "RUNNING":
                continue

            try:
                last_hb = datetime.fromisoformat(entry["last_heartbeat"])
                # Ensure timezone-aware comparison
                if last_hb.tzinfo is None:
                    last_hb = last_hb.replace(tzinfo=timezone.utc)
                age = (now - last_hb).total_seconds()
                if age <= stale_threshold_seconds:
                    result = dict(entry)
                    result["engine_id"] = eid
                    result["heartbeat_age_seconds"] = round(age, 1)
                    active.append(result)
            except (ValueError, KeyError):
                continue

        return active

    def get_all_engines(self) -> Dict[str, Any]:
        """Return the full registry state, including offline engines."""
        return self._read()

    def cleanup_stale(self, stale_threshold_seconds: int = DEFAULT_STALE_THRESHOLD) -> int:
        """Mark engines as OFFLINE if their heartbeat has exceeded the threshold."""
        data = self._read()
        now = datetime.now(timezone.utc)
        marked = 0

        for eid, entry in data["engines"].items():
            if entry.get("status") != "RUNNING":
                continue
            try:
                last_hb = datetime.fromisoformat(entry["last_heartbeat"])
                if last_hb.tzinfo is None:
                    last_hb = last_hb.replace(tzinfo=timezone.utc)
                age = (now - last_hb).total_seconds()
                if age > stale_threshold_seconds:
                    entry["status"] = "OFFLINE"
                    marked += 1
            except (ValueError, KeyError):
                entry["status"] = "OFFLINE"
                marked += 1

        if marked > 0:
            self._write(data)
        return marked
