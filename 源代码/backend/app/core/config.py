from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Power Trading AI Platform"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_path: str = "./power_trading.db"
    auth_enabled: bool = True
    auth_tokens: str = "admin-token:0:admin,user1001-token:1001:trader,user1002-token:1002:trader"
    auth_users: str = (
        "admin:admin123:0:admin,"
        "user1001:pass1001:1001:trader,"
        "user1002:pass1002:1002:trader"
    )
    auth_jwt_enabled: bool = True
    auth_jwt_secret: str = "change-this-secret-in-production"
    auth_jwt_exp_minutes: int = 120
    auth_refresh_exp_minutes: int = 10080

    # OIDC / SSO：校验第三方签发的 RS256 JWT（Bearer），与本地 JWT / 静态令牌并存
    auth_oidc_enabled: bool = False
    auth_oidc_issuer: str = ""
    auth_oidc_audience: str = ""
    auth_oidc_jwks_url: str = ""
    auth_oidc_discovery_timeout_sec: float = 10.0
    auth_oidc_username_claim: str = "sub"
    auth_oidc_org_id_claim: str = "org_id"
    auth_oidc_role_claim: str = "role"
    auth_oidc_default_role: str = "trader"

    # 外部系统：交易中心、计量（HTTP JSON）。未配置 base_url 时接口返回「未配置」。
    trading_center_base_url: str = ""
    trading_center_api_key: str = ""
    trading_center_timeout_sec: float = 15.0
    trading_center_clearing_path: str = "/v1/clearing/snapshot"
    trading_center_market_prices_path: str = "/v1/market/prices"

    metering_base_url: str = ""
    metering_api_key: str = ""
    metering_timeout_sec: float = 15.0
    metering_readings_path: str = "/v1/meter/readings"

    # 前端静态文件挂载（设置为 0 或 false 时，/console 路径将不挂载前端，用于前后端分离部署）
    mount_frontend_dist: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
    )


settings = Settings()
