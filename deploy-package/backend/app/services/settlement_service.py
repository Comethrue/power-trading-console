"""结算对账增强服务：在任务基础上增加差异统计与汇总报告能力。"""

import json
from datetime import datetime, timezone
from uuid import uuid4

from app.core.errors import AppException, ErrorCode
from app.db.sqlite import get_connection
from app.schemas.settlement import (
    ReconcileTaskDetail,
    ReconcileTaskRequest,
    ReconcileTaskResponse,
)

VALID_STATUS_TRANSITIONS = {
    "queued": {"running", "failed"},
    "running": {"completed", "failed"},
    "completed": set(),
    "failed": set(),
}


def create_reconcile_task(payload: ReconcileTaskRequest, rule_version: str) -> ReconcileTaskResponse:
    task_id = f"REC-{uuid4().hex[:10].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO reconcile_tasks (
                task_id,
                org_id,
                province_code,
                rule_version,
                cycle_start,
                cycle_end,
                status,
                message,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                payload.org_id,
                payload.province_code.upper(),
                rule_version,
                payload.cycle_start.isoformat(),
                payload.cycle_end.isoformat(),
                "queued",
                None,
                now,
                now,
            ),
        )

    return ReconcileTaskResponse(
        task_id=task_id,
        status="queued",
        province_code=payload.province_code.upper(),
        rule_version=rule_version,
    )


def get_reconcile_task(task_id: str, org_id: int, is_admin: bool) -> ReconcileTaskDetail | None:
    where_sql = "WHERE task_id = ?"
    params: tuple = (task_id,)
    if not is_admin:
        where_sql += " AND org_id = ?"
        params = (task_id, org_id)

    with get_connection() as conn:
        row = conn.execute(
            f"""
            SELECT task_id, org_id, province_code, rule_version, cycle_start, cycle_end,
                   status, message, created_at, updated_at
            FROM reconcile_tasks
            {where_sql}
            """,
            params,
        ).fetchone()

    if row is None:
        return None

    return ReconcileTaskDetail(
        task_id=row["task_id"],
        org_id=row["org_id"],
        province_code=row["province_code"],
        rule_version=row["rule_version"],
        cycle_start=row["cycle_start"],
        cycle_end=row["cycle_end"],
        status=row["status"],
        message=row["message"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def list_reconcile_tasks(
    page_no: int,
    page_size: int,
    org_id: int,
    is_admin: bool,
    status: str | None = None,
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

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with get_connection() as conn:
        total_row = conn.execute(
            f"SELECT COUNT(1) AS total FROM reconcile_tasks {where_sql}",
            tuple(params),
        ).fetchone()

        rows = conn.execute(
            f"""
            SELECT task_id, org_id, province_code, rule_version, cycle_start, cycle_end,
                   status, message, created_at, updated_at
            FROM reconcile_tasks
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params + [page_size, offset]),
        ).fetchall()

    items = [
        {
            "task_id": row["task_id"],
            "org_id": row["org_id"],
            "province_code": row["province_code"],
            "rule_version": row["rule_version"],
            "cycle_start": row["cycle_start"],
            "cycle_end": row["cycle_end"],
            "status": row["status"],
            "message": row["message"],
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


def update_reconcile_task_status(
    task_id: str,
    status: str,
    org_id: int,
    is_admin: bool,
    message: str | None = None,
) -> ReconcileTaskDetail:
    existing = get_reconcile_task(task_id, org_id=org_id, is_admin=is_admin)
    if existing is None:
        raise AppException(
            code=ErrorCode.RECONCILE_TASK_NOT_FOUND,
            message="reconcile task not found",
            status_code=404,
        )

    if status != existing.status and status not in VALID_STATUS_TRANSITIONS[existing.status]:
        raise AppException(
            code=ErrorCode.INVALID_STATUS_TRANSITION,
            message=f"invalid transition from {existing.status} to {status}",
            status_code=400,
        )

    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE reconcile_tasks
            SET status = ?, message = ?, updated_at = ?
            WHERE task_id = ?
            """,
            (status, message, now, task_id),
        )

    updated = get_reconcile_task(task_id, org_id=org_id, is_admin=is_admin)
    if updated is None:
        raise AppException(
            code=ErrorCode.RECONCILE_TASK_NOT_FOUND,
            message="reconcile task not found after update",
            status_code=404,
        )
    return updated


def get_reconcile_summary(
    task_id: str,
    org_id: int,
    is_admin: bool,
) -> dict:
    """生成结算汇总报告：统计结算周期内的申报数量、总电量、均价及差异。"""
    task = get_reconcile_task(task_id, org_id=org_id, is_admin=is_admin)
    if task is None:
        raise AppException(
            code=ErrorCode.RECONCILE_TASK_NOT_FOUND,
            message="reconcile task not found",
            status_code=404,
        )

    query_org_id = None if is_admin else org_id

    with get_connection() as conn:
        # 统计申报数据
        where_clauses = [
            "province_code = ?",
            "trade_date >= ?",
            "trade_date <= ?",
        ]
        params: list = [
            task.province_code,
            str(task.cycle_start),
            str(task.cycle_end),
        ]

        if query_org_id is not None:
            where_clauses.append("org_id = ?")
            params.append(query_org_id)

        where_sql = "WHERE " + " AND ".join(where_clauses)

        rows = conn.execute(
            f"""
            SELECT declaration_id, payload_json, trade_date, status
            FROM trade_declarations
            {where_sql}
            ORDER BY trade_date ASC
            """,
            tuple(params),
        ).fetchall()

    total_declarations = len(rows)
    total_volume_mwh = 0.0
    total_price_sum = 0.0
    slot_count = 0
    by_date: dict[str, dict] = {}

    for row in rows:
        trade_date = row["trade_date"]
        if trade_date not in by_date:
            by_date[trade_date] = {"declarations": 0, "volume_mwh": 0.0, "price_sum": 0.0, "slots": 0}

        by_date[trade_date]["declarations"] += 1

        try:
            payload = json.loads(row["payload_json"])
            timeslots = payload.get("timeslots", [])
            for ts in timeslots:
                vol = float(ts.get("volume_mwh", 0))
                price = float(ts.get("price", 0))
                total_volume_mwh += vol
                total_price_sum += price
                slot_count += 1
                by_date[trade_date]["volume_mwh"] += vol
                by_date[trade_date]["price_sum"] += price
                by_date[trade_date]["slots"] += 1
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue

    avg_price = round(total_price_sum / slot_count, 4) if slot_count > 0 else 0.0

    daily_summary = []
    for trade_date in sorted(by_date.keys()):
        d = by_date[trade_date]
        d_avg_price = round(d["price_sum"] / d["slots"], 4) if d["slots"] > 0 else 0.0
        daily_summary.append(
            {
                "trade_date": trade_date,
                "declarations": d["declarations"],
                "volume_mwh": round(d["volume_mwh"], 4),
                "avg_price": d_avg_price,
            }
        )

    # 与合同台账对比（若存在）
    contract_volume = 0.0
    deviation_mwh = 0.0
    with get_connection() as conn:
        cparams: list = [task.province_code]
        cwhere = "WHERE province_code = ? AND start_date <= ? AND end_date >= ? AND status = 'active'"
        cparams += [str(task.cycle_end), str(task.cycle_start)]
        if query_org_id is not None:
            cwhere += " AND org_id = ?"
            cparams.append(query_org_id)

        crows = conn.execute(
            f"SELECT volume_mwh FROM contracts {cwhere}",
            tuple(cparams),
        ).fetchall()

    for crow in crows:
        contract_volume += float(crow["volume_mwh"])

    if contract_volume > 0:
        deviation_mwh = round(total_volume_mwh - contract_volume, 4)

    return {
        "task_id": task_id,
        "province_code": task.province_code,
        "cycle_start": str(task.cycle_start),
        "cycle_end": str(task.cycle_end),
        "task_status": task.status,
        "total_declarations": total_declarations,
        "total_volume_mwh": round(total_volume_mwh, 4),
        "avg_price": avg_price,
        "contract_volume_mwh": round(contract_volume, 4),
        "deviation_mwh": deviation_mwh,
        "daily_summary": daily_summary,
    }
