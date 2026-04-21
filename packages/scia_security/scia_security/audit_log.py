"""
SCIA Access Audit Logger — Enterprise Grade

Records every read, write, and delete operation across memory
and security modules. Persisted to SQLite. Append-only — entries
cannot be modified or deleted after creation.

Every audit entry records:
- who (actor_id)
- what (action)
- which (resource_type + resource_id)
- when (timestamp)
- outcome (success/failure)
- context (metadata)

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

import json
import os
import sqlite3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AuditEntry:
    """A single audit log entry — immutable once written."""
    entry_id: str
    timestamp: str
    actor_id: str
    action: str           # store, retrieve, delete, start, end, encrypt, decrypt
    resource_type: str    # memory_node, execution_node, reflex_pattern
    resource_id: str
    outcome: str          # success, failure, rejected, truncated
    metadata: Dict[str, Any] = field(default_factory=dict)


class AccessAuditLog:
    """Append-only audit log persisted to SQLite.

    Once an entry is written, it cannot be modified or deleted.
    The log is the source of truth for who accessed what.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.environ.get(
            "SCIA_AUDIT_DB", "./data/access_audit.db"
        )
        self._persistent_conn: Optional[sqlite3.Connection] = None
        self._init_audit_db()

    def _get_audit_conn(self) -> sqlite3.Connection:
        if self.db_path == ":memory:":
            if self._persistent_conn is None:
                self._persistent_conn = sqlite3.connect(":memory:")
            return self._persistent_conn
        return sqlite3.connect(self.db_path)

    def _close_audit_conn(self, conn: sqlite3.Connection):
        if conn is not self._persistent_conn:
            conn.close()

    def _init_audit_db(self):
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        conn = self._get_audit_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                entry_id      TEXT PRIMARY KEY,
                timestamp     TEXT NOT NULL,
                actor_id      TEXT NOT NULL,
                action        TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id   TEXT NOT NULL,
                outcome       TEXT NOT NULL,
                metadata      TEXT
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_log(actor_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_log(resource_type, resource_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_log(timestamp)"
        )
        conn.commit()
        self._close_audit_conn(conn)

    def log(self, actor_id: str, action: str, resource_type: str,
            resource_id: str, outcome: str = "success",
            metadata: Optional[Dict[str, Any]] = None) -> str:
        """Append an audit entry. Returns the entry_id."""
        import secrets
        entry_id = f"audit_{secrets.token_hex(8)}"
        ts = datetime.now().isoformat()

        conn = self._get_audit_conn()
        conn.execute(
            """INSERT INTO audit_log
               (entry_id, timestamp, actor_id, action, resource_type,
                resource_id, outcome, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry_id, ts, actor_id, action, resource_type,
                resource_id, outcome,
                json.dumps(metadata or {}),
            ),
        )
        conn.commit()
        self._close_audit_conn(conn)
        return entry_id

    def query_by_actor(self, actor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit entries for a specific actor."""
        return self._query(
            "SELECT * FROM audit_log WHERE actor_id = ? ORDER BY timestamp DESC LIMIT ?",
            (actor_id, limit),
        )

    def query_by_resource(self, resource_type: str, resource_id: str,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit entries for a specific resource."""
        return self._query(
            "SELECT * FROM audit_log WHERE resource_type = ? AND resource_id = ? "
            "ORDER BY timestamp DESC LIMIT ?",
            (resource_type, resource_id, limit),
        )

    def query_by_action(self, action: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit entries for a specific action type."""
        return self._query(
            "SELECT * FROM audit_log WHERE action = ? ORDER BY timestamp DESC LIMIT ?",
            (action, limit),
        )

    def query_failures(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all failed/rejected operations."""
        return self._query(
            "SELECT * FROM audit_log WHERE outcome != 'success' "
            "ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )

    def count(self) -> int:
        """Total number of audit entries."""
        conn = self._get_audit_conn()
        row = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()
        self._close_audit_conn(conn)
        return row[0]

    def _query(self, sql: str, params: tuple) -> List[Dict[str, Any]]:
        conn = self._get_audit_conn()
        rows = conn.execute(sql, params).fetchall()
        self._close_audit_conn(conn)
        cols = ["entry_id", "timestamp", "actor_id", "action",
                "resource_type", "resource_id", "outcome", "metadata"]
        results = []
        for row in rows:
            entry = dict(zip(cols, row))
            entry["metadata"] = json.loads(entry["metadata"]) if entry["metadata"] else {}
            results.append(entry)
        return results
