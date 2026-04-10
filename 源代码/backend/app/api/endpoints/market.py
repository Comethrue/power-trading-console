from fastapi import APIRouter, Depends, Query, Request

from app.core.auth import require_user
from app.core.response import build_response
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse
from app.services.market_service import list_market_prices, list_province_price_metrics

router = APIRouter()


@router.get("/province-metrics", response_model=ApiResponse)
def province_price_metrics(
    request: Request,
    _: UserContext = Depends(require_user),
) -> ApiResponse:
    """十大重点省份：最新交易日电价统计（数据库聚合）。"""
    rows = list_province_price_metrics()
    return build_response(request=request, data={"provinces": rows})


@router.get("/prices", response_model=ApiResponse)
def query_market_prices(
    request: Request,
    province_code: str | None = Query(default=None, min_length=2, max_length=8),
    market_date: str | None = Query(default=None),
    page_no: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    _: UserContext = Depends(require_user),
) -> ApiResponse:
    result = list_market_prices(
        province_code=province_code,
        market_date=market_date,
        page_no=page_no,
        page_size=page_size,
    )
    return build_response(request=request, data=result)
