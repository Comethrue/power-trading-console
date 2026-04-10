CREATE TABLE IF NOT EXISTS trade_declarations (
    declaration_id TEXT PRIMARY KEY,
    idempotency_key TEXT NOT NULL UNIQUE,
    province_code TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    trade_date TEXT NOT NULL,
    market_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reconcile_tasks (
    task_id TEXT PRIMARY KEY,
    org_id INTEGER NOT NULL,
    province_code TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    cycle_start TEXT NOT NULL,
    cycle_end TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS market_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    province_code TEXT NOT NULL,
    market_date TEXT NOT NULL,
    timeslot TEXT NOT NULL,
    price REAL NOT NULL,
    source TEXT,
    created_at TEXT NOT NULL
);
