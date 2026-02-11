"""
db.py — Logger class using Python's sqlite3.
Stores: original_filename, new_filename, summary, category, timestamp.
Database file: content_alchemist.db (project root).
"""

import os
import sqlite3


class Logger:
    """SQLite-backed logger for processed file records."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "content_alchemist.db",
            )
        self.db_path = db_path
        self._init_db()

    # ── Private ─────────────────────────────────────────────────────

    def _connect(self):
        """Return a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Create the files table if it doesn't already exist."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_filename TEXT    NOT NULL,
                    new_filename      TEXT    NOT NULL,
                    category          TEXT    NOT NULL,
                    summary           TEXT,
                    dest_path         TEXT    NOT NULL,
                    timestamp         TEXT    DEFAULT (datetime('now', 'localtime'))
                );
            """)
            conn.commit()

    # ── Public API ──────────────────────────────────────────────────

    def log(self, original_filename: str, new_filename: str,
            category: str, summary: str, dest_path: str):
        """Insert a processed-file record."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO files
                    (original_filename, new_filename, category, summary, dest_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (original_filename, new_filename, category, summary, dest_path),
            )
            conn.commit()
        print(f"[logger] Saved record for '{new_filename}' in category '{category}'")

    def get_recent(self, limit: int = 20) -> list[dict]:
        """Return the most recent `limit` records."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM files ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def search_summary(self, query: str) -> list[dict]:
        """
        Keyword search on the summary column.
        Splits query into words and matches rows containing ALL words.
        """
        words = query.strip().split()
        if not words:
            return []

        conditions = " AND ".join(["summary LIKE ?"] * len(words))
        params = [f"%{w}%" for w in words]

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"SELECT * FROM files WHERE {conditions} ORDER BY timestamp DESC",
                params,
            ).fetchall()
        return [dict(row) for row in rows]

    def get_all(self) -> list[dict]:
        """Return all records, newest first."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM files ORDER BY timestamp DESC"
            ).fetchall()
        return [dict(row) for row in rows]


# ── Convenience singleton ───────────────────────────────────────────
# Other modules can do:  from db import logger
logger = Logger()
