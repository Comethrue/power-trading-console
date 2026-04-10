import logging

import httpx
from fastapi import APIRouter, Depends, Query, Request

from app.core.auth import require_user
from app.core.config import settings
from app.core.errors import AppException, ErrorCode
from app.core.response import build_response
from app.integrations import metering as metering_client
from app.integrations import trading_center as tc_client
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status", response_model=ApiResponse)
def integration_status(
    request: Request,
    _: UserContext = Depends(require_user),
) -> ApiResponse:
    data = {
        "trading_center": {
            "configured": bool((settings.trading_center_base_url or "").strip()),
            "timeout_sec": settings.trading_center_timeout_sec,
        },
        "metering": {
            "configured": bool((settings.metering_base_url or "").strip()),
            "timeout_sec": settings.metering_timeout_sec,
        },
    }
    return build_response(request=request, data=data)


@router.get("/trading-center/clearing-snapshot", response_model=ApiResponse)
def trading_center_clearing(
    request: Request,
    trade_date: str | None = Query(default=None),
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    if not (settings.trading_center_base_url or "").strip():
        raise AppException(
            code=ErrorCode.INTEGRATION_NOT_CONFIGURED,
            message="trading center base URL is not configured (APP_TRADING_CENTER_BASE_URL)",
            status_code=503,
        )
    org_id = None if user.is_admin else user.org_id
    try:
        payload = tc_client.fetch_clearing_snapshot(org_id=org_id, trade_date=trade_date)
    except httpx.HTTPStatusError as exc:
        logger.warning("trading center HTTP error: %s", exc)
        raise AppException(
            code=ErrorCode.INTEGRATION_UPSTREAM_ERROR,
            message=f"trading center returned {exc.response.status_code}",
            status_code=502,
        ) from exc
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("trading center request failed: %s", exc)
        raise AppException(
            code=ErrorCode.INTEGRATION_UPSTREAM_ERROR,
            message="trading center request failed",
            status_code=502,
        ) from exc
    return build_response(request=request, data={"source": "trading_center", "payload": payload})


@router.get("/trading-center/market-prices", response_model=ApiResponse)
def trading_center_market_prices(
    request: Request,
    province_code: str | None = Query(default=None, min_length=2, max_length=8),
    market_date: str | None = Query(default=None),
    _: UserContext = Depends(require_user),
) -> ApiResponse:
    if not (settings.trading_center_base_url or "").strip():
        raise AppException(
            code=ErrorCode.INTEGRATION_NOT_CONFIGURED,
            message="trading center base URL is not configured (APP_TRADING_CENTER_BASE_URL)",
            status_code=503,
        )
    try:
        payload = tc_client.fetch_market_prices(
            province_code=province_code.upper() if province_code else None,
            market_date=market_date,
        )
    except httpx.HTTPStatusError as exc:
        logger.warning("trading center HTTP error: %s", exc)
        raise AppException(
            code=ErrorCode.INTEGRATION_UPSTREAM_ERROR,
            message=f"trading center returned {exc.response.status_code}",
            status_code=502,
        ) from exc
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("trading center request failed: %s", exc)
        raise AppException(
            code=ErrorCode.INTEGRATION_UPSTREAM_ERROR,
            message="trading center request failed",
            status_code=502,
        ) from exc
    return build_response(request=request, data={"source": "trading_center", "payload": payload})


@router.get("/metering/readings", response_model=ApiResponse)
def metering_readings(
    request: Request,
    meter_point_id: str = Query(..., min_length=1, max_length=128),
    reading_date: str | None = Query(default=None),
    _: UserContext = Depends(require_user),
) -> ApiResponse:
    if not (settings.metering_base_url or "").strip():
        raise AppException(
            code=ErrorCode.INTEGRATION_NOT_CONFIGURED,
            message="metering base URL is not configured (APP_METERING_BASE_URL)",
            status_code=503,
        )
    try:
        payload = metering_client.fetch_meter_readings(meter_point_id, reading_date)
    except httpx.HTTPStatusError as exc:
        logger.warning("metering HTTP error: %s", exc)
        raise AppException(
            code=ErrorCode.INTEGRATION_UPSTREAM_ERROR,
            message=f"metering system returned {exc.response.status_code}",
            status_code=502,
        ) from exc
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("metering request failed: %s", exc)
        raise AppException(
            code=ErrorCode.INTEGRATION_UPSTREAM_ERROR,
            message="metering request failed",
            status_code=502,
        ) from exc
    return build_response(request=request, data={"source": "metering", "payload": payload})
