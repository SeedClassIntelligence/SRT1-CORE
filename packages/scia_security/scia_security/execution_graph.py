"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: TRACING_AUDIT
Key Symbols: ExecutionNode, ExecutionGraph, __post_init__, __init__, _get_conn ... and 11 more

Extracted Purposes:
  - ExecutionNode: Node in execution graph
  - ExecutionGraph: Execution tracking with SQLite persistence.
  - _load_from_db: Reload full execution graph from SQLite on startup.
  ...
"""
#!/usr/bin/env python3
"""
Execution Graph — Enterprise Grade
Tracks and visualizes execution flow with SQLite persistence.

Every node is written to disk on creation and completion.
On startup, the full graph is reloaded from the database.
No execution history is lost on restart.
Thread-safe — all mutations protected by a lock.

Patent & Copyright: Seed-Class Intelligence Architecture (SCIA)
Author: William Darnell Jernigan IV (Architect)
"""

import json
import os
import sqlite3
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExecutionNode:
    """Node in execution graph"""
    id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    result: Any = None
    error: Optional[str] = None
    children: List[str] = None
    parent_id: Optional[str] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


from .db_utils import SQLiteDatabaseManager

class ExecutionGraph(SQLiteDatabaseManager):
    """Execution tracking with SQLite persistence.

    Every start_execution() and end_execution() writes to disk.
    On init, the full graph is reloaded from the database.
    """

    def __init__(self, db_path: str = None, encryption_key: str = None,
                 audit_log=None, actor_id: str = "system"):
        self.nodes: Dict[str, ExecutionNode] = {}
        self.root_nodes: List[str] = []
        self.current_node: Optional[str] = None
        self._actor_id = actor_id
        self._lock = threading.Lock()

        super().__init__(db_path or os.environ.get("EXECUTION_GRAPH_DB", "./data/execution_graph.db"))

        # Encryption at rest
        from .encryption import DataEncryptor
        self._encryptor = DataEncryptor(master_secret=encryption_key)

        # Access audit logging
        self._audit = audit_log

        self._init_graph_db()
        self._load_from_db()

    # ── SQLite Persistence ────────────────────────────────────────────

    def _init_graph_db(self):
        self._ensure_dir()
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_nodes (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                start_time  TEXT NOT NULL,
                end_time    TEXT,
                status      TEXT NOT NULL,
                result      TEXT,
                error       TEXT,
                children    TEXT NOT NULL,
                parent_id   TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_exec_status
            ON execution_nodes(status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_exec_parent
            ON execution_nodes(parent_id)
        """)
        conn.commit()
        self._close_conn(conn)

    def _load_from_db(self):
        """Reload full execution graph from SQLite on startup."""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT id, name, start_time, end_time, status, result, "
            "error, children, parent_id FROM execution_nodes ORDER BY rowid"
        )
        for row in cursor:
            node = ExecutionNode(
                id=row[0],
                name=row[1],
                start_time=datetime.fromisoformat(row[2]),
                end_time=datetime.fromisoformat(row[3]) if row[3] else None,
                status=row[4],
                result=json.loads(self._encryptor.decrypt(row[5])) if row[5] else None,
                error=self._encryptor.decrypt(row[6]) if row[6] else None,
                children=json.loads(row[7]),
                parent_id=row[8],
            )
            self.nodes[node.id] = node
            if node.parent_id is None:
                self.root_nodes.append(node.id)
        self._close_conn(conn)

    def _persist_node(self, node: ExecutionNode):
        """Write a single node to SQLite. Result and error encrypted at rest."""
        encrypted_result = (
            self._encryptor.encrypt(json.dumps(node.result, default=str))
            if node.result is not None else None
        )
        encrypted_error = (
            self._encryptor.encrypt(node.error)
            if node.error else None
        )
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO execution_nodes
               (id, name, start_time, end_time, status, result,
                error, children, parent_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                node.id,
                node.name,
                node.start_time.isoformat(),
                node.end_time.isoformat() if node.end_time else None,
                node.status,
                encrypted_result,
                encrypted_error,
                json.dumps(node.children),
                node.parent_id,
            ),
        )
        conn.commit()
        self._close_conn(conn)

    # ── Core Operations ───────────────────────────────────────────────

    # Validation limits
    MAX_NAME_LENGTH = 500
    MAX_NODE_ID_LENGTH = 64
    MAX_RESULT_SIZE = 100000

    def _audit_log(self, action: str, resource_id: str,
                   outcome: str = "success", metadata: dict = None):
        """Log an access event if audit logging is enabled."""
        if self._audit:
            self._audit.log(
                actor_id=self._actor_id,
                action=action,
                resource_type="execution_node",
                resource_id=resource_id,
                outcome=outcome,
                metadata=metadata,
            )
    MAX_ERROR_LENGTH = 10000

    def start_execution(self, name: str, node_id: str = None) -> str:
        """Start tracking execution. Thread-safe. Validates inputs. Persists immediately."""
        if not name or not isinstance(name, str):
            raise ValueError("Execution name is required and must be a string")
        if len(name) > self.MAX_NAME_LENGTH:
            raise ValueError(f"name exceeds maximum length ({self.MAX_NAME_LENGTH})")

        if node_id and len(node_id) > self.MAX_NODE_ID_LENGTH:
            raise ValueError(f"node_id exceeds maximum length ({self.MAX_NODE_ID_LENGTH})")

        if not node_id:
            import secrets
            node_id = f"exec_{secrets.token_hex(8)}"

        with self._lock:
            parent_id = self.current_node

            node = ExecutionNode(
                id=node_id,
                name=name,
                start_time=datetime.now(),
                parent_id=parent_id,
            )

            self.nodes[node_id] = node

            if parent_id and parent_id in self.nodes:
                self.nodes[parent_id].children.append(node_id)
                self._persist_node(self.nodes[parent_id])
            else:
                self.root_nodes.append(node_id)

            self.current_node = node_id
            self._persist_node(node)

        self._audit_log("start_execution", node_id, metadata={"name": name})
        return node_id

    def end_execution(self, node_id: str, result: Any = None, error: str = None):
        """End tracking execution. Thread-safe. Validates inputs. Persists immediately."""
        # Validate result size
        if result is not None and len(str(result)) > self.MAX_RESULT_SIZE:
            result = str(result)[:self.MAX_RESULT_SIZE] + "...[truncated]"

        # Validate error length
        if error and len(error) > self.MAX_ERROR_LENGTH:
            error = error[:self.MAX_ERROR_LENGTH] + "...[truncated]"

        with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.end_time = datetime.now()
                node.status = "error" if error else "completed"
                node.result = result
                node.error = error
                self._persist_node(node)

            self.current_node = self._find_parent(node_id)

        if node_id in self.nodes:
            self._audit_log(
                "end_execution", node_id,
                outcome="error" if error else "success",
                metadata={"status": self.nodes[node_id].status},
            )

    def _find_parent(self, node_id: str) -> Optional[str]:
        """Find parent of given node. Uses stored parent_id for O(1) lookup."""
        node = self.nodes.get(node_id)
        if node and node.parent_id:
            return node.parent_id
        return None

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        total_nodes = len(self.nodes)
        completed = sum(1 for node in self.nodes.values() if node.status == "completed")
        errors = sum(1 for node in self.nodes.values() if node.status == "error")

        return {
            "total_executions": total_nodes,
            "completed": completed,
            "errors": errors,
            "success_rate": completed / total_nodes if total_nodes > 0 else 0
        }

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific node's details."""
        node = self.nodes.get(node_id)
        if not node:
            return None
        return {
            "id": node.id,
            "name": node.name,
            "start_time": node.start_time.isoformat(),
            "end_time": node.end_time.isoformat() if node.end_time else None,
            "status": node.status,
            "result": node.result,
            "error": node.error,
            "children": node.children,
            "parent_id": node.parent_id,
        }

    def get_subtree(self, root_id: str) -> List[Dict[str, Any]]:
        """Get all nodes in a subtree starting from root_id."""
        result = []
        queue = [root_id]
        visited = set()
        while queue:
            nid = queue.pop(0)
            if nid in visited or nid not in self.nodes:
                continue
            visited.add(nid)
            node = self.nodes[nid]
            result.append(self.get_node(nid))
            queue.extend(node.children)
        return result
