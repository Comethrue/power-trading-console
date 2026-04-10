"""
偏差风险计算服务。

算法说明：
  偏差率 = 近期申报中价格偏差均值 / 规则价格上限
  - 统计 org 在 trade_date 前 30 天内的申报记录
  - 每条申报按 timeslot 价格计算与规则中点价格的偏差比
  - 取均值作为 deviation_ratio（0~1 之间）
  - 若无历史数据则使用省份中性偏差率（0.25）
  偏差成本 = base_cost * (1 + deviation_ratio) * deviation_penalty_coef
"""

import json
from datetime import date, timedelta

from app.core.errors import AppException, ErrorCode
from app.db.sqlite import get_connection
from app.schemas.risk import DeviationRiskResponse
from app.services.rule_service import get_rule


def _calc_deviation_ratio_from_history(
    org_id: int,
    province_code: str,
    trade_date: date,
    price_min: float,
    price_max: float,
    lookback_days: int = 30,
) -> float:
    """基于近 lookback_days 天的历史申报，计算加权偏差率。

    偏差定义：每个 timeslot 的申报价格偏离规则价格区间中点的程度。
    偏差比 = abs(price - midpoint) / (price_max - price_min + 1)
    返回所有 timeslot 的均值，范围 [0, 1]。
    """
    window_start = (trade_date - timedelta(days=lookback_days)).isoformat()
    window_end = trade_date.isoformat()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT payload_json
            FROM trade_declarations
            WHERE org_id = ?
              AND province_code = ?
              AND trade_date >= ?
              AND trade_date < ?
              AND status != 'rejected'
            ORDER BY created_at DESC
            LIMIT 200
            """,
            (org_id, province_code.upper(), window_start, window_end),
        ).fetchall()

    if not rows:
        return 0.25  # 无历史数据时使用中性偏差率

    midpoint = (price_min + price_max) / 2.0
    price_range = max(price_max - price_min, 1.0)

    total_ratio = 0.0
    count = 0
    for row in rows:
        try:
            payload = json.loads(row["payload_json"])
            timeslots = payload.get("timeslots", [])
            for ts in timeslots:
                price = float(ts.get("price", midpoint))
                ratio = abs(price - midpoint) / price_range
                total_ratio += min(ratio, 1.0)
                count += 1
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue

    if count == 0:
        return 0.25

    return round(total_ratio / count, 4)


def calculate_deviation_risk(
    trade_date: date,
    org_id: int,
    province_code: str,
    rule_version: str | None = None,
) -> DeviationRiskResponse:
    rule = get_rule(
        province_code=province_code,
        version=rule_version,
        trade_date=trade_date,
    )

    # 基于真实历史申报数据计算偏差率
    deviation_ratio = _calc_deviation_ratio_from_history(
        org_id=org_id,
        province_code=province_code,
        trade_date=trade_date,
        price_min=rule.trade.price_min,
        price_max=rule.trade.price_max,
    )

    if deviation_ratio >= rule.risk.high_threshold:
        risk_level = "high"
    elif deviation_ratio >= rule.risk.medium_threshold:
        risk_level = "medium"
    else:
        risk_level = "low"

    expected_cost = round(
        rule.risk.base_cost * (1 + deviation_ratio) * rule.settlement.deviation_penalty_coef,
        2,
    )

    return DeviationRiskResponse(
        trade_date=trade_date,
        org_id=org_id,
        province_code=province_code.upper(),
        rule_version=rule.version,
        deviation_ratio=deviation_ratio,
        deviation_risk_level=risk_level,
        expected_deviation_cost=expected_cost,
    )
