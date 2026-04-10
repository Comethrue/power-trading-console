-- 合同台账表
CREATE TABLE IF NOT EXISTS contracts (
    contract_id   TEXT PRIMARY KEY,
    org_id        INTEGER NOT NULL,
    province_code TEXT NOT NULL,
    contract_type TEXT NOT NULL,   -- MEDIUM_LONG / SPOT_DA / SPOT_RT
    counterpart   TEXT,            -- 对手方名称（可选）
    volume_mwh    REAL NOT NULL,   -- 合同电量（MWh）
    price         REAL NOT NULL,   -- 合同价格（元/MWh）
    start_date    TEXT NOT NULL,   -- 合同开始日期
    end_date      TEXT NOT NULL,   -- 合同结束日期
    status        TEXT NOT NULL DEFAULT 'active',  -- active / expired / cancelled
    remark        TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_contracts_org
ON contracts (org_id);

CREATE INDEX IF NOT EXISTS idx_contracts_province
ON contracts (province_code);

CREATE INDEX IF NOT EXISTS idx_contracts_status
ON contracts (status);

CREATE INDEX IF NOT EXISTS idx_contracts_dates
ON contracts (start_date, end_date);
