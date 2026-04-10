CREATE TABLE IF NOT EXISTS auth_refresh_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL,
    org_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    replaced_by_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_auth_refresh_sessions_username
ON auth_refresh_sessions (username);

CREATE INDEX IF NOT EXISTS idx_auth_refresh_sessions_org
ON auth_refresh_sessions (org_id);
