import json
from datetime import datetime, timezone

from app.db.sqlite import get_connection
from app.schemas.auth import UserContext


def write_audit_log(
    user: UserContext,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    request_id: str | None = None,
    details: dict | None = None,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO audit_logs (
                org_id, user_role, action, resource_type, resource_id, request_id, details_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.org_id,
                user.role,
                action,
                resource_type,
                resource_id,
                request_id,
                json.dumps(details or {}, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def list_audit_logs(
    page_no: int,
    page_size: int,
    user: UserContext,
    action: str | None = None,
) -> dict:
    offset = (page_no - 1) * page_size
    where_clauses = []
    params: list = []

    if not user.is_admin:
        where_clauses.append("org_id = ?")
        params.append(user.org_id)
    if action:
        where_clauses.append("action = ?")
        params.append(action)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with get_connection() as conn:
        total_row = conn.execute(
            f"SELECT COUNT(1) AS total FROM audit_logs {where_sql}",
            tuple(params),
        ).fetchone()
        rows = conn.execute(
            f"""
            SELECT id, org_id, user_role, action, resource_type, resource_id, request_id, details_json, created_at
            FROM audit_logs
            {where_sql}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params + [page_size, offset]),
        ).fetchall()

    items = [
        {
            "id": row["id"],
            "org_id": row["org_id"],
            "user_role": row["user_role"],
            "action": row["action"],
            "resource_type": row["resource_type"],
            "resource_id": row["resource_id"],
            "request_id": row["request_id"],
            "details_json": row["details_json"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]

    return {
        "page_no": page_no,
        "page_size": page_size,
        "total": int(total_row["total"]) if total_row else 0,
        "items": items,
    }
