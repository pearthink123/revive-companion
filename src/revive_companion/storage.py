"""
State persistence for revive-companion.

Provides pluggable storage backends for engine state recovery across restarts.

Usage:
    from revive_companion.storage import JsonStateStore, SQLiteStateStore

    # JSON file storage (simple, single-user)
    store = JsonStateStore("state.json")
    store.save(engine)
    store.load(engine)

    # SQLite storage (multi-user, production)
    store = SQLiteStateStore("state.db")
    store.save(engine, user_id="user_123")
    store.load(engine, user_id="user_123")
"""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from .core.engine import PoissonEngine
from .core.models import Action, LogEntry


class BaseStateStore(ABC):
    """Abstract base for state persistence."""

    @abstractmethod
    def save(self, engine: PoissonEngine, user_id: str | None = None) -> None:
        """Save engine state."""
        ...

    @abstractmethod
    def load(self, engine: PoissonEngine, user_id: str | None = None) -> bool:
        """Load engine state. Returns True if state was loaded."""
        ...

    @abstractmethod
    def exists(self, user_id: str | None = None) -> bool:
        """Check if saved state exists."""
        ...

    @abstractmethod
    def delete(self, user_id: str | None = None) -> None:
        """Delete saved state."""
        ...


class JsonStateStore(BaseStateStore):
    """
    JSON file state storage. Good for single-user or development.

    Each user gets a separate JSON file: {base_path}/{user_id}.json
    Default (no user_id): {base_path}/state.json
    """

    def __init__(self, base_path: str | Path = "state"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _path_for(self, user_id: str | None) -> Path:
        if user_id:
            return self.base_path / f"{user_id}.json"
        return self.base_path / "state.json"

    def save(self, engine: PoissonEngine, user_id: str | None = None) -> None:
        path = self._path_for(user_id)
        data = {
            "probability": engine.probability,
            "miss_streak": engine.miss_streak,
            "last_send_time": engine.last_send_time.isoformat() if engine.last_send_time else None,
            "log": [entry.to_dict() for entry in engine.log],
            "saved_at": datetime.now().isoformat(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, engine: PoissonEngine, user_id: str | None = None) -> bool:
        path = self._path_for(user_id)
        if not path.exists():
            return False
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        engine.probability = data["probability"]
        engine.miss_streak = data["miss_streak"]
        engine.last_send_time = (
            datetime.fromisoformat(data["last_send_time"]) if data["last_send_time"] else None
        )
        engine.log = [LogEntry.from_dict(e) for e in data["log"]]
        return True

    def exists(self, user_id: str | None = None) -> bool:
        return self._path_for(user_id).exists()

    def delete(self, user_id: str | None = None) -> None:
        path = self._path_for(user_id)
        if path.exists():
            path.unlink()

    def list_users(self) -> list[str]:
        """List all user IDs with saved state."""
        return [p.stem for p in self.base_path.glob("*.json") if p.name != "state.json"]


class SQLiteStateStore(BaseStateStore):
    """
    SQLite state storage. Good for multi-user production use.

    Schema:
        CREATE TABLE engine_state (
            user_id TEXT PRIMARY KEY,
            probability REAL,
            miss_streak INTEGER,
            last_send_time TEXT,
            log_json TEXT,
            saved_at TEXT
        );
    """

    def __init__(self, db_path: str | Path = "state.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS engine_state (
                    user_id TEXT PRIMARY KEY,
                    probability REAL NOT NULL,
                    miss_streak INTEGER NOT NULL DEFAULT 0,
                    last_send_time TEXT,
                    log_json TEXT NOT NULL DEFAULT '[]',
                    saved_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save(self, engine: PoissonEngine, user_id: str | None = None) -> None:
        uid = user_id or "_default"
        now = datetime.now().isoformat()
        log_json = json.dumps([e.to_dict() for e in engine.log], ensure_ascii=False)
        last_send = engine.last_send_time.isoformat() if engine.last_send_time else None

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO engine_state (user_id, probability, miss_streak, last_send_time, log_json, saved_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    probability = excluded.probability,
                    miss_streak = excluded.miss_streak,
                    last_send_time = excluded.last_send_time,
                    log_json = excluded.log_json,
                    saved_at = excluded.saved_at
                """,
                (uid, engine.probability, engine.miss_streak, last_send, log_json, now),
            )
            conn.commit()

    def load(self, engine: PoissonEngine, user_id: str | None = None) -> bool:
        uid = user_id or "_default"
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT probability, miss_streak, last_send_time, log_json FROM engine_state WHERE user_id = ?",
                (uid,),
            ).fetchone()

        if row is None:
            return False

        engine.probability = row[0]
        engine.miss_streak = row[1]
        engine.last_send_time = datetime.fromisoformat(row[2]) if row[2] else None
        engine.log = [LogEntry.from_dict(e) for e in json.loads(row[3])]
        return True

    def exists(self, user_id: str | None = None) -> bool:
        uid = user_id or "_default"
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM engine_state WHERE user_id = ?", (uid,)
            ).fetchone()
        return row is not None

    def delete(self, user_id: str | None = None) -> None:
        uid = user_id or "_default"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM engine_state WHERE user_id = ?", (uid,))
            conn.commit()

    def list_users(self) -> list[str]:
        """List all user IDs with saved state."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT user_id FROM engine_state WHERE user_id != '_default'"
            ).fetchall()
        return [r[0] for r in rows]

    def count(self) -> int:
        """Total number of stored states."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM engine_state").fetchone()
        return row[0]
