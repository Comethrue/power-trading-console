ALTER TABLE trade_declarations ADD COLUMN org_id INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_trade_declarations_org
ON trade_declarations (org_id);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    user_role TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    request_id TEXT,
    details_json TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_org
ON audit_logs (org_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_action
ON audit_logs (action);
