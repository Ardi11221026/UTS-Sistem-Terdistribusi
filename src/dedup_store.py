import sqlite3
import os
from typing import Tuple, List, Optional
import threading

class DedupStore:
    def __init__(self, db_path: str = "./data/dedup.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self._lock:
            c = self._conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS processed (
                    topic TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    timestamp TEXT,
                    source TEXT,
                    payload TEXT,
                    PRIMARY KEY(topic, event_id)
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_topic ON processed(topic)")
            self._conn.commit()

    def is_processed(self, topic: str, event_id: str) -> bool:
        with self._lock:
            c = self._conn.cursor()
            c.execute(
                "SELECT 1 FROM processed WHERE topic=? AND event_id=? LIMIT 1",
                (topic, event_id),
            )
            return c.fetchone() is not None

    def mark_processed(self, topic: str, event_id: str, timestamp: str, source: str, payload: str):
        with self._lock:
            try:
                c = self._conn.cursor()
                c.execute(
                    "INSERT INTO processed (topic, event_id, timestamp, source, payload) VALUES (?, ?, ?, ?, ?)",
                    (topic, event_id, timestamp, source, payload),
                )
                self._conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def list_events(self, topic: Optional[str] = None) -> List[Tuple[str, str, str, str, str]]:
        with self._lock:
            c = self._conn.cursor()
            if topic:
                c.execute(
                    "SELECT topic, event_id, timestamp, source, payload FROM processed WHERE topic=? ORDER BY timestamp",
                    (topic,),
                )
            else:
                c.execute("SELECT topic, event_id, timestamp, source, payload FROM processed ORDER BY timestamp")
            return c.fetchall()

    def close(self):
        with self._lock:
            try:
                self._conn.close()
            except Exception:
                pass
