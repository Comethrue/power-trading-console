import json
from datetime import datetime, timezone
from uuid import uuid4

from app.db.sqlite import get_connection
from app.schemas.trades import TradeDeclarationRequest, TradeDeclarationResponse


def create_declaration(
    payload: TradeDeclarationRequest,
    rule_version: str,
    org_id: int,
) -> TradeDeclarationResponse:
    dedupe_key = f"{org_id}:{payload.idempotency_key}"
    with get_connection() as conn:
        existing = conn.execute(
            """
            SELECT declaration_id, status, rule_version
            FROM trade_declarations
            WHERE idempotency_key = ?
            """,
            (dedupe_key,),
        ).fetchone()

    if existing is not None:
        return TradeDeclarationResponse(
            declaration_id=existing["declaration_id"],
            status=existing["status"],
            rule_version=existing["rule_version"],
            duplicate=True,
        )

    declaration_id = f"DEC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    payload_json = json.dumps(payload.model_dump(mode="json"), ensure_ascii=False)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO trade_declarations (
                declaration_id,
                idempotency_key,
                org_id,
                province_code,
                rule_version,
                trade_date,
                market_type,
                payload_json,
                status,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                declaration_id,
                dedupe_key,
                org_id,
                payload.province_code.upper(),
                rule_version,
                payload.trade_date.isoformat(),
                payload.market_type,
                payload_json,
                "submitted",
                now,
                now,
            ),
        )

    return TradeDeclarationResponse(
        declaration_id=declaration_id,
        status="submitted",
        rule_version=rule_version,
        duplicate=False,
    )


def get_declaration_by_id(declaration_id: str, org_id: int, is_admin: bool) -> dict | None:
    where_sql = "WHERE declaration_id = ?"
    params: tuple = (declaration_id,)
    if not is_admin:
        where_sql += " AND org_id = ?"
        params = (declaration_id, org_id)

    with get_connection() as conn:
        row = conn.execute(
            f"""
            SELECT declaration_id, org_id, province_code, rule_version, trade_date, market_type, payload_json, status, created_at, updated_at
            FROM trade_declarations
            {where_sql}
            """,
            params,
        ).fetchone()

    if row is None:
        return None

    payload = json.loads(row["payload_json"])
    return {
        "declaration_id": row["declaration_id"],
        "org_id": row["org_id"],
        "province_code": row["province_code"],
        "rule_version": row["rule_version"],
        "trade_date": row["trade_date"],
        "market_type": row["market_type"],
        "status": row["status"],
        "payload": payload,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_declarations(page_no: int, page_size: int, org_id: int, is_admin: bool) -> dict:
    offset = (page_no - 1) * page_size
    where_sql = ""
    params: tuple = ()
    if not is_admin:
        where_sql = "WHERE org_id = ?"
        params = (org_id,)

    with get_connection() as conn:
        total_row = conn.execute(
            f"SELECT COUNT(1) AS total FROM trade_declarations {where_sql}",
            params,
        ).fetchone()
        rows = conn.execute(
            f"""
            SELECT declaration_id, org_id, province_code, rule_version, trade_date, market_type, status, created_at, updated_at
            FROM trade_declarations
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            params + (page_size, offset),
        ).fetchall()

    items = [
        {
            "declaration_id": row["declaration_id"],
            "org_id": row["org_id"],
            "province_code": row["province_code"],
            "rule_version": row["rule_version"],
            "trade_date": row["trade_date"],
            "market_type": row["market_type"],
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]

    return {
        "page_no": page_no,
        "page_size": page_size,
        "total": int(total_row["total"]) if total_row else 0,
        "items": items,
    }
