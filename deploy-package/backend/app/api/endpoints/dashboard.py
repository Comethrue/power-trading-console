from fastapi import APIRouter, Depends, Request

from app.core.auth import require_user
from app.core.response import build_response
from app.db.sqlite import get_connection
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse

router = APIRouter()

# 与前端演示一致的十大重点省份（名称仅用于展示）
_PROVINCE_NAMES = {
    "GD": "广东",
    "JS": "江苏",
    "ZJ": "浙江",
    "SD": "山东",
    "NM": "内蒙古",
    "HE": "河北",
    "SC": "四川",
    "HA": "河南",
    "HB": "湖北",
    "AH": "安徽",
    "SX": "山西",
    "FJ": "福建",
    "LN": "辽宁",
    "SN": "陕西",
    "HN": "湖南",
}


@router.get("/stats", response_model=ApiResponse)
def dashboard_stats(
    request: Request,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    """看板统计：申报数、合同数、结算任务数、审计日志数及风险分布。"""
    org_filter = None if user.is_admin else user.org_id

    with get_connection() as conn:
        # 申报统计
        if org_filter is not None:
            total_declarations = conn.execute(
                "SELECT COUNT(1) AS c FROM trade_declarations WHERE org_id = ?", (org_filter,)
            ).fetchone()["c"]
            submitted_today = conn.execute(
                "SELECT COUNT(1) AS c FROM trade_declarations WHERE org_id = ? AND date(created_at) = date('now')",
                (org_filter,),
            ).fetchone()["c"]
        else:
            total_declarations = conn.execute(
                "SELECT COUNT(1) AS c FROM trade_declarations"
            ).fetchone()["c"]
            submitted_today = conn.execute(
                "SELECT COUNT(1) AS c FROM trade_declarations WHERE date(created_at) = date('now')"
            ).fetchone()["c"]

        # 合同统计
        if org_filter is not None:
            total_contracts = conn.execute(
                "SELECT COUNT(1) AS c FROM contracts WHERE org_id = ?", (org_filter,)
            ).fetchone()["c"]
            active_contracts = conn.execute(
                "SELECT COUNT(1) AS c FROM contracts WHERE org_id = ? AND status = 'active'", (org_filter,)
            ).fetchone()["c"]
        else:
            total_contracts = conn.execute(
                "SELECT COUNT(1) AS c FROM contracts"
            ).fetchone()["c"]
            active_contracts = conn.execute(
                "SELECT COUNT(1) AS c FROM contracts WHERE status = 'active'"
            ).fetchone()["c"]

        # 结算任务统计
        if org_filter is not None:
            total_tasks = conn.execute(
                "SELECT COUNT(1) AS c FROM reconcile_tasks WHERE org_id = ?", (org_filter,)
            ).fetchone()["c"]
            pending_tasks = conn.execute(
                "SELECT COUNT(1) AS c FROM reconcile_tasks WHERE org_id = ? AND status IN ('queued','running')",
                (org_filter,),
            ).fetchone()["c"]
        else:
            total_tasks = conn.execute(
                "SELECT COUNT(1) AS c FROM reconcile_tasks"
            ).fetchone()["c"]
            pending_tasks = conn.execute(
                "SELECT COUNT(1) AS c FROM reconcile_tasks WHERE status IN ('queued','running')"
            ).fetchone()["c"]

        # 审计日志统计
        if org_filter is not None:
            total_audit_logs = conn.execute(
                "SELECT COUNT(1) AS c FROM audit_logs WHERE org_id = ?", (org_filter,)
            ).fetchone()["c"]
        else:
            total_audit_logs = conn.execute(
                "SELECT COUNT(1) AS c FROM audit_logs"
            ).fetchone()["c"]

        # 市场价格统计（最新均价）
        latest_price_row = conn.execute(
            """
            SELECT AVG(price) AS avg_price, MAX(market_date) AS latest_date
            FROM market_prices
            WHERE market_date = (SELECT MAX(market_date) FROM market_prices)
            """
        ).fetchone()
        latest_avg_price = round(float(latest_price_row["avg_price"] or 0), 2)
        latest_market_date = latest_price_row["latest_date"]

        # 近7天申报趋势
        if org_filter is not None:
            trend_rows = conn.execute(
                """
                SELECT date(created_at) AS d, COUNT(1) AS cnt
                FROM trade_declarations
                WHERE org_id = ? AND date(created_at) >= date('now', '-6 days')
                GROUP BY d
                ORDER BY d ASC
                """,
                (org_filter,),
            ).fetchall()
        else:
            trend_rows = conn.execute(
                """
                SELECT date(created_at) AS d, COUNT(1) AS cnt
                FROM trade_declarations
                WHERE date(created_at) >= date('now', '-6 days')
                GROUP BY d
                ORDER BY d ASC
                """
            ).fetchall()

        trend = [{"date": row["d"], "count": row["cnt"]} for row in trend_rows]

        # 近约 4 周按周汇总（ISO 周序号）
        if org_filter is not None:
            week_rows = conn.execute(
                """
                SELECT strftime('%Y', created_at) || '-W' || strftime('%W', created_at) AS period,
                       COUNT(1) AS cnt
                FROM trade_declarations
                WHERE org_id = ? AND date(created_at) >= date('now', '-27 days')
                GROUP BY period
                ORDER BY period ASC
                """,
                (org_filter,),
            ).fetchall()
        else:
            week_rows = conn.execute(
                """
                SELECT strftime('%Y', created_at) || '-W' || strftime('%W', created_at) AS period,
                       COUNT(1) AS cnt
                FROM trade_declarations
                WHERE date(created_at) >= date('now', '-27 days')
                GROUP BY period
                ORDER BY period ASC
                """
            ).fetchall()

        trend_weeks = [{"period": row["period"], "count": row["cnt"]} for row in week_rows]

        # 近 6 个月按月汇总
        if org_filter is not None:
            month_rows = conn.execute(
                """
                SELECT strftime('%Y-%m', created_at) AS period, COUNT(1) AS cnt
                FROM trade_declarations
                WHERE org_id = ? AND date(created_at) >= date('now', '-180 days')
                GROUP BY period
                ORDER BY period ASC
                """,
                (org_filter,),
            ).fetchall()
        else:
            month_rows = conn.execute(
                """
                SELECT strftime('%Y-%m', created_at) AS period, COUNT(1) AS cnt
                FROM trade_declarations
                WHERE date(created_at) >= date('now', '-180 days')
                GROUP BY period
                ORDER BY period ASC
                """
            ).fetchall()

        trend_months = [{"period": row["period"], "count": row["cnt"]} for row in month_rows]

        # 最新交易日各省均价 Top（最多 10 省）
        mkt_rows = conn.execute(
            """
            SELECT province_code, AVG(price) AS avg_p
            FROM market_prices
            WHERE market_date = (SELECT MAX(market_date) FROM market_prices)
            GROUP BY province_code
            ORDER BY avg_p DESC
            LIMIT 10
            """
        ).fetchall()
        market_top = [
            {
                "province_code": row["province_code"],
                "province_name": _PROVINCE_NAMES.get(row["province_code"], row["province_code"]),
                "avg_price": round(float(row["avg_p"] or 0), 2),
            }
            for row in mkt_rows
        ]

    return build_response(
        request=request,
        data={
            "declarations": {
                "total": total_declarations,
                "submitted_today": submitted_today,
            },
            "contracts": {
                "total": total_contracts,
                "active": active_contracts,
            },
            "reconcile_tasks": {
                "total": total_tasks,
                "pending": pending_tasks,
            },
            "audit_logs": {
                "total": total_audit_logs,
            },
            "market": {
                "latest_avg_price": latest_avg_price,
                "latest_date": latest_market_date,
            },
            "declaration_trend_7d": trend,
            "declaration_trend_weeks": trend_weeks,
            "declaration_trend_months": trend_months,
            "market_top_provinces": market_top,
        },
    )
