-- 自助注册账号（PBKDF2 密码哈希），与静态 APP_AUTH_USERS 并存
CREATE TABLE IF NOT EXISTS auth_registered_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL COLLATE NOCASE,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    org_id INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT 'trader',
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_registered_users_username
    ON auth_registered_users(username);

CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_registered_users_org
    ON auth_registered_users(org_id);
