from typing import Any

from app.core.config import settings
from app.integrations.http_util import get_json


def fetch_meter_readings(
    meter_point_id: str,
    reading_date: str | None = None,
) -> Any:
    params: dict[str, str | int | None] = {"meter_point_id": meter_point_id}
    if reading_date:
        params["reading_date"] = reading_date
    return get_json(
        settings.metering_base_url,
        settings.metering_readings_path,
        api_key=settings.metering_api_key,
        timeout_sec=settings.metering_timeout_sec,
        params=params,
    )
