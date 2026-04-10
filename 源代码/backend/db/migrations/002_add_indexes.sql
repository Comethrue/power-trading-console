CREATE INDEX IF NOT EXISTS idx_trade_declarations_trade_date
ON trade_declarations (trade_date);

CREATE INDEX IF NOT EXISTS idx_trade_declarations_province
ON trade_declarations (province_code);

CREATE INDEX IF NOT EXISTS idx_reconcile_tasks_org
ON reconcile_tasks (org_id);

CREATE INDEX IF NOT EXISTS idx_reconcile_tasks_status
ON reconcile_tasks (status);

CREATE INDEX IF NOT EXISTS idx_market_prices_key
ON market_prices (province_code, market_date, timeslot);
