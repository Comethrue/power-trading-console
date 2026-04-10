from app.db.sqlite import get_connection

# 与前端 TOP10_POWER_PROVINCES、演示种子数据一致
TOP10_PROVINCE_CODES = (
    "GD",
    "JS",
    "ZJ",
    "SD",
    "NM",
    "HE",
    "SC",
    "HA",
    "HB",
    "AH",
)


def list_province_price_metrics() -> list[dict]:
    """各省最新交易日现货电价汇总（库内真实聚合，用于下拉指标展示）。"""
    placeholders = ",".join("?" * len(TOP10_PROVINCE_CODES))
    params = list(TOP10_PROVINCE_CODES)
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT mp.province_code,
                   mp.market_date,
                   ROUND(AVG(mp.price), 2) AS avg_price,
                   ROUND(MIN(mp.price), 2) AS min_price,
                   ROUND(MAX(mp.price), 2) AS max_price,
                   COUNT(1) AS point_count
            FROM market_prices mp
            INNER JOIN (
                SELECT province_code, MAX(market_date) AS md
                FROM market_prices
                WHERE province_code IN ({placeholders})
                GROUP BY province_code
            ) latest
              ON latest.province_code = mp.province_code
             AND latest.md = mp.market_date
            WHERE mp.province_code IN ({placeholders})
            GROUP BY mp.province_code, mp.market_date
            ORDER BY mp.province_code
            """,
            params + params,
        ).fetchall()

    return [
        {
            "province_code": row["province_code"],
            "market_date": row["market_date"],
            "avg_price": float(row["avg_price"] or 0),
            "min_price": float(row["min_price"] or 0),
            "max_price": float(row["max_price"] or 0),
            "point_count": int(row["point_count"] or 0),
        }
        for row in rows
    ]


def list_market_prices(
    province_code: str | None = None,
    market_date: str | None = None,
    page_no: int = 1,
    page_size: int = 20,
) -> dict:
    offset = (page_no - 1) * page_size
    where_clauses = []
    params: list = []

    if province_code:
        where_clauses.append("province_code = ?")
        params.append(province_code.upper())
    if market_date:
        where_clauses.append("market_date = ?")
        params.append(market_date)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with get_connection() as conn:
        total_row = conn.execute(
            f"SELECT COUNT(1) AS total FROM market_prices {where_sql}",
            tuple(params),
        ).fetchone()

        rows = conn.execute(
            f"""
            SELECT province_code, market_date, timeslot, price, source
            FROM market_prices
            {where_sql}
            ORDER BY market_date DESC, timeslot ASC
            LIMIT ? OFFSET ?
            """,
            tuple(params + [page_size, offset]),
        ).fetchall()

    items = [
        {
            "province_code": row["province_code"],
            "market_date": row["market_date"],
            "timeslot": row["timeslot"],
            "price": row["price"],
            "source": row["source"],
        }
        for row in rows
    ]

    return {
        "page_no": page_no,
        "page_size": page_size,
        "total": int(total_row["total"]) if total_row else 0,
        "items": items,
    }
