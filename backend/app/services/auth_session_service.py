import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.db.sqlite import get_connection
from app.schemas.auth import UserContext


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _is_expired(expires_at: str) -> bool:
    try:
        dt = datetime.fromisoformat(expires_at)
        return dt <= datetime.now(timezone.utc)
    except Exception:
        return True


def issue_refresh_token(user: UserContext) -> tuple[str, int]:
    raw_token = secrets.token_urlsafe(48)
    token_hash = _hash_token(raw_token)
    now = _utcnow_iso()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=settings.auth_refresh_exp_minutes)).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO auth_refresh_sessions (
                token_hash, username, org_id, role, expires_at, revoked_at, replaced_by_hash, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                token_hash,
                user.username or "",
                user.org_id,
                user.role,
                expires_at,
                None,
                None,
                now,
                now,
            ),
        )

    return raw_token, settings.auth_refresh_exp_minutes * 60


def _get_active_session_by_raw_token(raw_token: str) -> dict | None:
    token_hash = _hash_token(raw_token)
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, token_hash, username, org_id, role, expires_at, revoked_at
            FROM auth_refresh_sessions
            WHERE token_hash = ?
            """,
            (token_hash,),
        ).fetchone()

    if row is None:
        return None
    if row["revoked_at"] is not None:
        return None
    if _is_expired(row["expires_at"]):
        return None

    return {
        "id": row["id"],
        "token_hash": row["token_hash"],
        "username": row["username"],
        "org_id": row["org_id"],
        "role": row["role"],
        "expires_at": row["expires_at"],
    }


def rotate_refresh_token(raw_token: str) -> tuple[UserContext, str, int] | None:
    session = _get_active_session_by_raw_token(raw_token)
    if session is None:
        return None

    user = UserContext(
        token="",
        username=session["username"] or None,
        org_id=int(session["org_id"]),
        role=session["role"],
    )
    new_raw, new_exp_seconds = issue_refresh_token(user)
    new_hash = _hash_token(new_raw)
    now = _utcnow_iso()

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE auth_refresh_sessions
            SET revoked_at = ?, replaced_by_hash = ?, updated_at = ?
            WHERE token_hash = ?
            """,
            (now, new_hash, now, session["token_hash"]),
        )

    return user, new_raw, new_exp_seconds


def revoke_refresh_token(raw_token: str) -> bool:
    token_hash = _hash_token(raw_token)
    now = _utcnow_iso()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT token_hash, revoked_at
            FROM auth_refresh_sessions
            WHERE token_hash = ?
            """,
            (token_hash,),
        ).fetchone()
        if row is None:
            return False
        if row["revoked_at"] is not None:
            return True
        conn.execute(
            """
            UPDATE auth_refresh_sessions
            SET revoked_at = ?, updated_at = ?
            WHERE token_hash = ?
            """,
            (now, now, token_hash),
        )
    return True
