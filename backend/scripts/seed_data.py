"""
演示数据初始化脚本 - 向数据库中插入真实演示数据

此脚本在 FastAPI 应用启动时自动运行（lifespan 中调用），
也可以独立运行：
    python scripts/seed_data.py

演示数据包含：
  - 合同台账：广东(GD)、浙江(ZJ) 两个省份的合同
  - 交易申报：近8天的历史申报记录（每天96时段）
  - 结算对账：已完成和进行中的结算任务
  - 审计日志：系统操作历史

所有数据基于 2026-04-09 作为"今天"生成。
"""
import json
import os
import random
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# 使此脚本可独立运行（无论从 backend/ 还是项目根目录执行）
_root = Path(__file__).resolve().parents[1]
_db_path_cache = None


def _db_path():
    global _db_path_cache
    if _db_path_cache is not None:
        return _db_path_cache
    # 优先使用环境变量
    db_env = os.environ.get("APP_DATABASE_PATH", "")
    if db_env:
        _db_path_cache = Path(db_env)
        return _db_path_cache
    _db_path_cache = _root / "power_trading.db"
    return _db_path_cache


random.seed(42)

# 时间常量
TODAY = date(2026, 4, 9)
DAY_8_AGO = TODAY - timedelta(days=8)


def _timeslots(price_base, vol_base):
    """生成24小时96时段的价格和电量数据。"""
    slots = []
    for i in range(96):
        h = i // 4
        m = (i % 4) * 15
        h_end = (i + 1) // 4
        m_end = ((i + 1) % 4) * 15
        slot_label = "%02d:%02d-%02d:%02d" % (h, m, h_end, m_end)

        if 8 <= h < 11 or 17 <= h < 20:
            adj = random.uniform(1.10, 1.28)
        elif 12 <= h < 14:
            adj = random.uniform(0.85, 0.95)
        elif 0 <= h < 6:
            adj = random.uniform(0.82, 0.92)
        else:
            adj = random.uniform(0.96, 1.08)

        p = round(price_base * adj + random.uniform(-8, 8), 2)
        v = round(vol_base * adj + random.uniform(-3, 3), 2)
        slots.append({"slot": slot_label, "price": p, "volume_mwh": v})
    return slots


def _insert_contracts(conn):
    contracts = [
        # 广东(GD) - org 1001
        {
            "id": "CTR-20260401-A1B2C3D4",
            "org_id": 1001,
            "province_code": "GD",
            "contract_type": "MEDIUM_LONG",
            "counterpart": "广东能源集团",
            "volume_mwh": 5000,
            "price": 435.00,
            "start_date": "2026-04-01",
            "end_date": "2026-04-30",
            "status": "active",
            "remark": "4月月度中长期合同",
            "created_at": (TODAY - timedelta(days=8)).isoformat(),
        },
        {
            "id": "CTR-20260402-E5F6G7H8",
            "org_id": 1001,
            "province_code": "GD",
            "contract_type": "SPOT_DA",
            "counterpart": "广州电力交易中心",
            "volume_mwh": 1200,
            "price": 442.50,
            "start_date": "2026-04-08",
            "end_date": "2026-04-08",
            "status": "active",
            "remark": "日前现货日合同",
            "created_at": (TODAY - timedelta(days=1)).isoformat(),
        },
        {
            "id": "CTR-20260315-I9J0K1L2",
            "org_id": 1001,
            "province_code": "GD",
            "contract_type": "MEDIUM_LONG",
            "counterpart": "深圳能源集团",
            "volume_mwh": 3500,
            "price": 418.00,
            "start_date": "2026-03-15",
            "end_date": "2026-03-31",
            "status": "expired",
            "remark": "3月月度合同（已到期）",
            "created_at": "2026-03-15T08:00:00Z",
        },
        # 浙江(ZJ) - org 1001
        {
            "id": "CTR-20260403-M3N4O5P6",
            "org_id": 1001,
            "province_code": "ZJ",
            "contract_type": "MEDIUM_LONG",
            "counterpart": "浙江电力交易中心",
            "volume_mwh": 2800,
            "price": 462.00,
            "start_date": "2026-04-03",
            "end_date": "2026-04-30",
            "status": "active",
            "remark": "浙江中长期合同",
            "created_at": (TODAY - timedelta(days=6)).isoformat(),
        },
        # 广东(GD) - org 1002
        {
            "id": "CTR-20260405-Q7R8S9T0",
            "org_id": 1002,
            "province_code": "GD",
            "contract_type": "MEDIUM_LONG",
            "counterpart": "广东电网公司",
            "volume_mwh": 4200,
            "price": 428.00,
            "start_date": "2026-04-05",
            "end_date": "2026-04-30",
            "status": "active",
            "remark": "用户1002广东合同",
            "created_at": (TODAY - timedelta(days=4)).isoformat(),
        },
        {
            "id": "CTR-20260407-U1V2W3X4",
            "org_id": 1002,
            "province_code": "ZJ",
            "contract_type": "SPOT_DA",
            "counterpart": "浙江电网",
            "volume_mwh": 800,
            "price": 455.00,
            "start_date": "2026-04-09",
            "end_date": "2026-04-09",
            "status": "active",
            "remark": "今日日前现货",
            "created_at": (TODAY - timedelta(days=2)).isoformat(),
        },
        # 浙江(ZJ) - org 1002
        {
            "id": "CTR-20260320-Y5Z6A7B8",
            "org_id": 1002,
            "province_code": "ZJ",
            "contract_type": "MEDIUM_LONG",
            "counterpart": "浙江能源集团",
            "volume_mwh": 2000,
            "price": 450.00,
            "start_date": "2026-03-20",
            "end_date": "2026-03-31",
            "status": "expired",
            "remark": "3月合同（已到期）",
            "created_at": "2026-03-20T09:00:00Z",
        },
    ]
    inserted = 0
    for c in contracts:
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO contracts
                (contract_id, org_id, province_code, contract_type, counterpart,
                 volume_mwh, price, start_date, end_date, status, remark, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    c["id"], c["org_id"], c["province_code"], c["contract_type"],
                    c["counterpart"], c["volume_mwh"], c["price"],
                    c["start_date"], c["end_date"], c["status"], c["remark"],
                    c["created_at"], c["created_at"],
                ),
            )
            inserted += 1
        except Exception:
            pass
    return inserted


def _insert_declarations(conn):
    inserted = 0

    # org 1001, GD, 每天1条, 共8天
    for day_offset in range(8):
        trade_date = DAY_8_AGO + timedelta(days=day_offset)
        ts = _timeslots(price_base=425.0, vol_base=50.0)
        payload = {
            "province_code": "GD",
            "rule_version": "2026.04",
            "trade_date": trade_date.isoformat(),
            "market_type": "SPOT_DA",
            "idempotency_key": "dec-%s-1001-batch" % trade_date.strftime("%Y%m%d"),
            "timeslots": ts,
        }
        decl_id = "DEC-%s-%08X" % (trade_date.strftime("%Y%m%d"), 10010000 + day_offset)
        created = (trade_date + timedelta(hours=9)).isoformat()
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO trade_declarations
                (declaration_id, idempotency_key, org_id, province_code, rule_version,
                 trade_date, market_type, payload_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decl_id,
                    "1001:dec-%s-1001-batch" % trade_date.strftime("%Y%m%d"),
                    1001, "GD", "2026.04",
                    trade_date.isoformat(), "SPOT_DA",
                    json.dumps(payload, ensure_ascii=False),
                    "submitted", created, created,
                ),
            )
            inserted += 1
        except Exception:
            pass

    # org 1001, ZJ, 隔天1条, 共4条
    for day_offset in range(0, 8, 2):
        trade_date = DAY_8_AGO + timedelta(days=day_offset)
        ts = _timeslots(price_base=455.0, vol_base=40.0)
        payload = {
            "province_code": "ZJ",
            "rule_version": "2026.04",
            "trade_date": trade_date.isoformat(),
            "market_type": "SPOT_DA",
            "idempotency_key": "dec-%s-1001-zj-batch" % trade_date.strftime("%Y%m%d"),
            "timeslots": ts,
        }
        decl_id = "DEC-%s-%08X" % (trade_date.strftime("%Y%m%d"), 10020000 + day_offset)
        created = (trade_date + timedelta(hours=9, minutes=15)).isoformat()
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO trade_declarations
                (declaration_id, idempotency_key, org_id, province_code, rule_version,
                 trade_date, market_type, payload_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decl_id,
                    "1001:dec-%s-1001-zj-batch" % trade_date.strftime("%Y%m%d"),
                    1001, "ZJ", "2026.04",
                    trade_date.isoformat(), "SPOT_DA",
                    json.dumps(payload, ensure_ascii=False),
                    "submitted", created, created,
                ),
            )
            inserted += 1
        except Exception:
            pass

    # org 1002, GD, 每天1条, 共8天
    for day_offset in range(8):
        trade_date = DAY_8_AGO + timedelta(days=day_offset)
        ts = _timeslots(price_base=418.0, vol_base=45.0)
        payload = {
            "province_code": "GD",
            "rule_version": "2026.04",
            "trade_date": trade_date.isoformat(),
            "market_type": "SPOT_DA",
            "idempotency_key": "dec-%s-1002-batch" % trade_date.strftime("%Y%m%d"),
            "timeslots": ts,
        }
        decl_id = "DEC-%s-%08X" % (trade_date.strftime("%Y%m%d"), 10030000 + day_offset)
        created = (trade_date + timedelta(hours=9, minutes=30)).isoformat()
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO trade_declarations
                (declaration_id, idempotency_key, org_id, province_code, rule_version,
                 trade_date, market_type, payload_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decl_id,
                    "1002:dec-%s-1002-batch" % trade_date.strftime("%Y%m%d"),
                    1002, "GD", "2026.04",
                    trade_date.isoformat(), "SPOT_DA",
                    json.dumps(payload, ensure_ascii=False),
                    "submitted", created, created,
                ),
            )
            inserted += 1
        except Exception:
            pass

    return inserted


def _insert_reconcile_tasks(conn):
    tasks = [
        # org 1001 - 广东已完成
        {
            "id": "REC-1001GD00001",
            "org_id": 1001,
            "province_code": "GD",
            "rule_version": "2026.04",
            "cycle_start": "2026-03-01",
            "cycle_end": "2026-03-31",
            "status": "completed",
            "message": "3月结算已完成",
            "created_at": "2026-04-01T10:00:00Z",
        },
        # org 1001 - 广东进行中
        {
            "id": "REC-1001GD00002",
            "org_id": 1001,
            "province_code": "GD",
            "rule_version": "2026.04",
            "cycle_start": "2026-04-01",
            "cycle_end": "2026-04-08",
            "status": "running",
            "message": "4月上旬结算处理中",
            "created_at": "2026-04-09T08:30:00Z",
        },
        # org 1001 - 浙江已完成
        {
            "id": "REC-1001ZJ00003",
            "org_id": 1001,
            "province_code": "ZJ",
            "rule_version": "2026.04",
            "cycle_start": "2026-03-01",
            "cycle_end": "2026-03-31",
            "status": "completed",
            "message": "浙江3月结算完成",
            "created_at": "2026-04-02T09:00:00Z",
        },
        # org 1001 - 浙江排队中
        {
            "id": "REC-1001ZJ00004",
            "org_id": 1001,
            "province_code": "ZJ",
            "rule_version": "2026.04",
            "cycle_start": "2026-04-01",
            "cycle_end": "2026-04-08",
            "status": "queued",
            "message": None,
            "created_at": "2026-04-09T09:00:00Z",
        },
        # org 1002 - 广东已完成
        {
            "id": "REC-1002GD00005",
            "org_id": 1002,
            "province_code": "GD",
            "rule_version": "2026.04",
            "cycle_start": "2026-03-01",
            "cycle_end": "2026-03-31",
            "status": "completed",
            "message": "用户1002-3月结算",
            "created_at": "2026-04-01T11:00:00Z",
        },
        # org 1002 - 广东排队中
        {
            "id": "REC-1002GD00006",
            "org_id": 1002,
            "province_code": "GD",
            "rule_version": "2026.04",
            "cycle_start": "2026-04-01",
            "cycle_end": "2026-04-08",
            "status": "queued",
            "message": None,
            "created_at": "2026-04-09T08:45:00Z",
        },
    ]
    inserted = 0
    for t in tasks:
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO reconcile_tasks
                (task_id, org_id, province_code, rule_version, cycle_start, cycle_end,
                 status, message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    t["id"], t["org_id"], t["province_code"], t["rule_version"],
                    t["cycle_start"], t["cycle_end"], t["status"], t["message"],
                    t["created_at"], t["created_at"],
                ),
            )
            inserted += 1
        except Exception:
            pass
    return inserted


def _insert_audit_logs(conn):
    # (org_id, role, action, resource_type, resource_id, created_at, details_dict)
    logs = [
        (1001, "trader", "contract_create", "contract",
         "CTR-20260401-A1B2C3D4", "2026-04-01T08:05:00Z",
         {"org_id": 1001, "province_code": "GD", "contract_type": "MEDIUM_LONG"}),
        (1001, "trader", "trade_declaration_create", "trade_declaration",
         "DEC-%s-%08X" % (DAY_8_AGO.strftime("%Y%m%d"), 10010000),
         (DAY_8_AGO + timedelta(hours=9)).isoformat(),
         {"province_code": "GD", "rule_version": "2026.04", "duplicate": False}),
        (1001, "trader", "reconcile_task_create", "reconcile_task",
         "REC-1001GD00001", "2026-04-01T10:00:00Z",
         {"org_id": 1001, "province_code": "GD", "rule_version": "2026.04"}),
        (1001, "trader", "reconcile_task_status_update", "reconcile_task",
         "REC-1001GD00001", "2026-04-01T10:30:00Z",
         {"status": "running"}),
        (1001, "trader", "reconcile_task_status_update", "reconcile_task",
         "REC-1001GD00001", "2026-04-01T14:00:00Z",
         {"status": "completed"}),
        (1001, "trader", "trade_declaration_create", "trade_declaration",
         "DEC-%s-%08X" % (DAY_8_AGO.strftime("%Y%m%d"), 10020000),
         (DAY_8_AGO + timedelta(days=1, hours=9)).isoformat(),
         {"province_code": "ZJ", "rule_version": "2026.04", "duplicate": False}),
        (1001, "trader", "reconcile_task_create", "reconcile_task",
         "REC-1001ZJ00003", "2026-04-02T09:00:00Z",
         {"org_id": 1001, "province_code": "ZJ", "rule_version": "2026.04"}),
        (1001, "trader", "reconcile_task_status_update", "reconcile_task",
         "REC-1001ZJ00003", "2026-04-02T10:00:00Z",
         {"status": "completed"}),
        (1001, "trader", "contract_create", "contract",
         "CTR-20260402-E5F6G7H8", "2026-04-02T08:00:00Z",
         {"org_id": 1001, "province_code": "GD", "contract_type": "SPOT_DA"}),
        (1001, "trader", "contract_create", "contract",
         "CTR-20260403-M3N4O5P6", "2026-04-03T08:30:00Z",
         {"org_id": 1001, "province_code": "ZJ", "contract_type": "MEDIUM_LONG"}),
        (1001, "trader", "reconcile_task_create", "reconcile_task",
         "REC-1001GD00002", "2026-04-09T08:30:00Z",
         {"org_id": 1001, "province_code": "GD", "rule_version": "2026.04"}),
        (1001, "trader", "reconcile_task_create", "reconcile_task",
         "REC-1001ZJ00004", "2026-04-09T09:00:00Z",
         {"org_id": 1001, "province_code": "ZJ", "rule_version": "2026.04"}),
        (1002, "trader", "contract_create", "contract",
         "CTR-20260405-Q7R8S9T0", "2026-04-05T08:00:00Z",
         {"org_id": 1002, "province_code": "GD", "contract_type": "MEDIUM_LONG"}),
        (1002, "trader", "trade_declaration_create", "trade_declaration",
         "DEC-%s-%08X" % (DAY_8_AGO.strftime("%Y%m%d"), 10030000),
         (DAY_8_AGO + timedelta(hours=9, minutes=30)).isoformat(),
         {"province_code": "GD", "rule_version": "2026.04", "duplicate": False}),
        (1002, "trader", "reconcile_task_create", "reconcile_task",
         "REC-1002GD00005", "2026-04-01T11:00:00Z",
         {"org_id": 1002, "province_code": "GD", "rule_version": "2026.04"}),
        (1002, "trader", "reconcile_task_status_update", "reconcile_task",
         "REC-1002GD00005", "2026-04-01T11:30:00Z",
         {"status": "completed"}),
        (1002, "trader", "contract_create", "contract",
         "CTR-20260407-U1V2W3X4", "2026-04-07T08:00:00Z",
         {"org_id": 1002, "province_code": "ZJ", "contract_type": "SPOT_DA"}),
        (1002, "trader", "reconcile_task_create", "reconcile_task",
         "REC-1002GD00006", "2026-04-09T08:45:00Z",
         {"org_id": 1002, "province_code": "GD", "rule_version": "2026.04"}),
    ]

    inserted = 0
    for (org_id, role, action, rtype, rid, created_at, details) in logs:
        try:
            conn.execute(
                """
                INSERT INTO audit_logs
                (org_id, user_role, action, resource_type, resource_id, request_id, details_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (org_id, role, action, rtype, rid, None, json.dumps(details, ensure_ascii=False), created_at),
            )
            inserted += 1
        except Exception:
            pass
    return inserted


# 全国电力市场「十大重点省份」演示（与前端 constants 对齐）
TOP10 = [
    ("GD", "广东", 1.00),
    ("JS", "江苏", 1.03),
    ("ZJ", "浙江", 1.06),
    ("SD", "山东", 0.98),
    ("NM", "内蒙古", 0.92),
    ("HE", "河北", 0.95),
    ("SC", "四川", 0.88),
    ("HA", "河南", 0.94),
    ("HB", "湖北", 0.96),
    ("AH", "安徽", 1.01),
]


def _insert_top10_market_from_gd(conn):
    """将广东各交易日电价曲线按省间价差系数复制到其他重点省（库内可查询的完整多日曲线）。"""
    date_rows = conn.execute(
        """
        SELECT DISTINCT market_date AS d FROM market_prices
        WHERE province_code = 'GD'
        ORDER BY market_date
        """
    ).fetchall()
    if not date_rows:
        return 0
    inserted = 0
    for drow in date_rows:
        latest = drow["d"]
        base = conn.execute(
            """
            SELECT timeslot, price FROM market_prices
            WHERE province_code = 'GD' AND market_date = ?
            ORDER BY timeslot
            """,
            (latest,),
        ).fetchall()
        if not base:
            continue
        for code, _name, mult in TOP10:
            if code == "GD":
                continue
            n = conn.execute(
                "SELECT COUNT(1) AS c FROM market_prices WHERE province_code = ? AND market_date = ?",
                (code, latest),
            ).fetchone()["c"]
            if n > 0:
                continue
            for r in base:
                ts, price = r["timeslot"], float(r["price"])
                p = round(price * mult + random.uniform(-2, 2), 2)
                try:
                    conn.execute(
                        """
                        INSERT INTO market_prices
                        (province_code, market_date, timeslot, price, source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (code, latest, ts, p, "top10_seed", datetime.now(timezone.utc).isoformat()),
                    )
                    inserted += 1
                except Exception:
                    pass
    return inserted


def _insert_top10_contracts(conn):
    """每省一条中长期合同（org 1001），便于台账展示十大省。"""
    inserted = 0
    for i, (code, name, _m) in enumerate(TOP10):
        cid = "CTR-TOP10-%s-%04d" % (code, 20260400 + i)
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO contracts
                (contract_id, org_id, province_code, contract_type, counterpart,
                 volume_mwh, price, start_date, end_date, status, remark, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid,
                    1001,
                    code,
                    "MEDIUM_LONG",
                    "%s省电力交易中心" % name,
                    2000 + i * 100,
                    round(400.0 + i * 3.5 + random.uniform(-5, 5), 2),
                    "2026-04-01",
                    "2026-04-30",
                    "active",
                    "十大重点省份演示合同",
                    (TODAY - timedelta(days=3)).isoformat(),
                    (TODAY - timedelta(days=3)).isoformat(),
                ),
            )
            inserted += 1
        except Exception:
            pass
    return inserted


def _insert_top10_declarations(conn):
    """各省在最近 8 天内若干申报，保证趋势图有量。"""
    inserted = 0
    for j, (code, _name, _m) in enumerate(TOP10):
        for day_offset in range(0, 8, 2):
            trade_date = DAY_8_AGO + timedelta(days=day_offset)
            ts = _timeslots(price_base=420.0 + j * 2, vol_base=40.0 + j)
            payload = {
                "province_code": code,
                "rule_version": "2026.04",
                "trade_date": trade_date.isoformat(),
                "market_type": "SPOT_DA",
                "idempotency_key": "dec-top10-%s-%s" % (code, trade_date.strftime("%Y%m%d")),
                "timeslots": ts,
            }
            decl_id = "DEC-TOP10-%s-%s" % (code, trade_date.strftime("%Y%m%d"))
            created = (trade_date + timedelta(hours=10, minutes=j % 5)).isoformat()
            try:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO trade_declarations
                    (declaration_id, idempotency_key, org_id, province_code, rule_version,
                     trade_date, market_type, payload_json, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        decl_id,
                        "1001:" + payload["idempotency_key"],
                        1001,
                        code,
                        "2026.04",
                        trade_date.isoformat(),
                        "SPOT_DA",
                        json.dumps(payload, ensure_ascii=False),
                        "submitted",
                        created,
                        created,
                    ),
                )
                inserted += 1
            except Exception:
                pass
    return inserted


def _insert_top10_reconcile(conn):
    inserted = 0
    for k, (code, name, _m) in enumerate(TOP10):
        tid = "REC-TOP10-%s-%04d" % (code, k + 1)
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO reconcile_tasks
                (task_id, org_id, province_code, rule_version, cycle_start, cycle_end,
                 status, message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tid,
                    1001,
                    code,
                    "2026.04",
                    "2026-04-01",
                    "2026-04-08",
                    "queued" if k % 3 else "running",
                    "%s 省结算队列演示" % name,
                    (TODAY - timedelta(hours=k)).isoformat(),
                    (TODAY - timedelta(hours=k)).isoformat(),
                ),
            )
            inserted += 1
        except Exception:
            pass
    return inserted


def run_seed(clear=False):
    db = _db_path()
    if not db.exists():
        print("[seed_data] 数据库不存在: %s，请先启动一次 API 以初始化数据库。" % db)
        return

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    if clear:
        print("[seed_data] 清空现有业务数据...")
        conn.execute("DELETE FROM audit_logs")
        conn.execute("DELETE FROM reconcile_tasks")
        conn.execute("DELETE FROM trade_declarations")
        conn.execute("DELETE FROM contracts")

    print("[seed_data] 插入演示数据...")

    c_contracts = _insert_contracts(conn)
    print("  合同台账: %d 条" % c_contracts)

    c_decls = _insert_declarations(conn)
    print("  交易申报: %d 条" % c_decls)

    c_tasks = _insert_reconcile_tasks(conn)
    print("  结算任务: %d 条" % c_tasks)

    c_audit = _insert_audit_logs(conn)
    print("  审计日志: %d 条" % c_audit)

    c_mkt = _insert_top10_market_from_gd(conn)
    print("  十大省市场电价: %d 条时点" % c_mkt)

    c_tc = _insert_top10_contracts(conn)
    print("  十大省补充合同: %d 条" % c_tc)

    c_td = _insert_top10_declarations(conn)
    print("  十大省补充申报: %d 条" % c_td)

    c_tr = _insert_top10_reconcile(conn)
    print("  十大省结算任务: %d 条" % c_tr)

    conn.commit()
    conn.close()

    print("[seed_data] 完成！演示数据已就绪。")
    print("  建议启动后用 admin 或 user1001 登录，打开 http://127.0.0.1:8000/console/")


if __name__ == "__main__":
    clear = "--clear" in sys.argv or "-c" in sys.argv
    run_seed(clear=clear)
