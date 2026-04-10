from datetime import datetime, timezone
from uuid import uuid4

from app.core.errors import AppException, ErrorCode
from app.db.sqlite import get_connection
from app.schemas.contracts import ContractDetail, ContractRequest, ContractResponse


def create_contract(payload: ContractRequest) -> ContractResponse:
    contract_id = f"CTR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO contracts (
                contract_id, org_id, province_code, contract_type, counterpart,
                volume_mwh, price, start_date, end_date, status, remark, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                contract_id,
                payload.org_id,
                payload.province_code.upper(),
                payload.contract_type,
                payload.counterpart,
                payload.volume_mwh,
                payload.price,
                payload.start_date.isoformat(),
                payload.end_date.isoformat(),
                "active",
                payload.remark,
                now,
                now,
            ),
        )

    return ContractResponse(contract_id=contract_id, status="active")


def get_contract_by_id(contract_id: str, org_id: int, is_admin: bool) -> ContractDetail | None:
    where_sql = "WHERE contract_id = ?"
    params: tuple = (contract_id,)
    if not is_admin:
        where_sql += " AND org_id = ?"
        params = (contract_id, org_id)

    with get_connection() as conn:
        row = conn.execute(
            f"""
            SELECT contract_id, org_id, province_code, contract_type, counterpart,
                   volume_mwh, price, start_date, end_date, status, remark, created_at, updated_at
            FROM contracts
            {where_sql}
            """,
            params,
        ).fetchone()

    if row is None:
        return None

    return ContractDetail(
        contract_id=row["contract_id"],
        org_id=row["org_id"],
        province_code=row["province_code"],
        contract_type=row["contract_type"],
        counterpart=row["counterpart"],
        volume_mwh=row["volume_mwh"],
        price=row["price"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        status=row["status"],
        remark=row["remark"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def list_contracts(
    page_no: int,
    page_size: int,
    org_id: int,
    is_admin: bool,
    status: str | None = None,
    contract_type: str | None = None,
) -> dict:
    offset = (page_no - 1) * page_size
    where_clauses: list[str] = []
    params: list = []

    if not is_admin:
        where_clauses.append("org_id = ?")
        params.append(org_id)

    if status:
        where_clauses.append("status = ?")
        params.append(status)

    if contract_type:
        where_clauses.append("contract_type = ?")
        params.append(contract_type)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with get_connection() as conn:
        total_row = conn.execute(
            f"SELECT COUNT(1) AS total FROM contracts {where_sql}",
            tuple(params),
        ).fetchone()

        rows = conn.execute(
            f"""
            SELECT contract_id, org_id, province_code, contract_type, counterpart,
                   volume_mwh, price, start_date, end_date, status, remark, created_at, updated_at
            FROM contracts
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params + [page_size, offset]),
        ).fetchall()

    items = [
        {
            "contract_id": row["contract_id"],
            "org_id": row["org_id"],
            "province_code": row["province_code"],
            "contract_type": row["contract_type"],
            "counterpart": row["counterpart"],
            "volume_mwh": row["volume_mwh"],
            "price": row["price"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "status": row["status"],
            "remark": row["remark"],
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


def update_contract_status(
    contract_id: str,
    status: str,
    org_id: int,
    is_admin: bool,
) -> ContractDetail:
    existing = get_contract_by_id(contract_id, org_id=org_id, is_admin=is_admin)
    if existing is None:
        raise AppException(
            code=ErrorCode.CONTRACT_NOT_FOUND,
            message="contract not found",
            status_code=404,
        )

    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE contracts
            SET status = ?, updated_at = ?
            WHERE contract_id = ?
            """,
            (status, now, contract_id),
        )

    updated = get_contract_by_id(contract_id, org_id=org_id, is_admin=is_admin)
    if updated is None:
        raise AppException(
            code=ErrorCode.CONTRACT_NOT_FOUND,
            message="contract not found after update",
            status_code=404,
        )
    return updated
