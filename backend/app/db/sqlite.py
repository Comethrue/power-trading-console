import sqlite3
from pathlib import Path

from app.core.config import settings


def _db_path() -> Path:
    return Path(settings.database_path).resolve()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    from app.db.migrate import apply_migrations

    _db_path().parent.mkdir(parents=True, exist_ok=True)
    apply_migrations()
