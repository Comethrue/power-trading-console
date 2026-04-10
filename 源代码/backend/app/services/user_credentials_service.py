"""自助注册用户：PBKDF2-SHA256 存储，与 settings.auth_users 静态账号并存。"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timezone

from app.db.sqlite import get_connection

_ITERATIONS = 60_000

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
_RESERVED = frozenset(
    {
        "admin",
        "root",
        "system",
        "api",
        "support",
        "guest",
        "user1001",
        "user1002",
    }
)


def validate_username(username: str) -> str | None:
    u = username.strip().lower()
    if not _USERNAME_RE.match(u):
        return None
    if u in _RESERVED:
        return None
    return u


def hash_password(password: str) -> tuple[str, str]:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("ascii"),
        _ITERATIONS,
    )
    return salt, dk.hex()


def verify_password(password: str, salt: str, stored_hex: str) -> bool:
    try:
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("ascii"),
            _ITERATIONS,
        )
    except Exception:
        return False
    return hmac.compare_digest(dk.hex(), stored_hex)


def username_exists_in_db(username_lower: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM auth_registered_users WHERE username = ? LIMIT 1",
            (username_lower,),
        ).fetchone()
    return row is not None


def create_registered_user(username_lower: str, password: str) -> tuple[int, str]:
    """返回 (org_id, role)。"""
    salt, phash = hash_password(password)
    now = datetime.now(timezone.utc).isoformat()
    role = "trader"

    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(MAX(org_id), 19999) + 1 AS n FROM auth_registered_users"
        ).fetchone()
        org_id = int(row["n"])
        conn.execute(
            """
            INSERT INTO auth_registered_users (
                username, password_salt, password_hash, org_id, role, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username_lower, salt, phash, org_id, role, now),
        )

    return org_id, role


def verify_registered_user(username: str, password: str) -> dict | None:
    uname = username.strip().lower()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT username, password_salt, password_hash, org_id, role
            FROM auth_registered_users
            WHERE username = ?
            """,
            (uname,),
        ).fetchone()
    if row is None:
        return None
    if not verify_password(password, row["password_salt"], row["password_hash"]):
        return None
    return {
        "username": row["username"],
        "org_id": int(row["org_id"]),
        "role": str(row["role"]),
    }
