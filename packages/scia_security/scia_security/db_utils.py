import os
import sqlite3
from typing import Optional

class SQLiteDatabaseManager:
    """Base class for SQLite database management to prevent duplicate connection logic."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._persistent_conn: Optional[sqlite3.Connection] = None

    def _get_conn(self) -> sqlite3.Connection:
        if self.db_path == ":memory:":
            if self._persistent_conn is None:
                self._persistent_conn = sqlite3.connect(":memory:")
            return self._persistent_conn
        return sqlite3.connect(self.db_path)

    def _close_conn(self, conn: sqlite3.Connection):
        if conn is not self._persistent_conn:
            conn.close()

    def _ensure_dir(self):
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
