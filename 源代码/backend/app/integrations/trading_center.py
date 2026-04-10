from typing import Any

from app.core.config import settings
from app.integrations.http_util import get_json


def fetch_clearing_snapshot(
    org_id: int | None = None,
    trade_date: str | None = None,
) -> Any:
    params: dict[str, str | int | None] = {}
    if org_id is not None:
        params["org_id"] = org_id
    if trade_date:
        params["trade_date"] = trade_date
    return get_json(
        settings.trading_center_base_url,
        settings.trading_center_clearing_path,
        api_key=settings.trading_center_api_key,
        timeout_sec=settings.trading_center_timeout_sec,
        params=params or None,
    )


def fetch_market_prices(
    province_code: str | None = None,
    market_date: str | None = None,
) -> Any:
    params: dict[str, str | int | None] = {}
    if province_code:
        params["province_code"] = province_code
    if market_date:
        params["market_date"] = market_date
    return get_json(
        settings.trading_center_base_url,
        settings.trading_center_market_prices_path,
        api_key=settings.trading_center_api_key,
        timeout_sec=settings.trading_center_timeout_sec,
        params=params or None,
    )
