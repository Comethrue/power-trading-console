from datetime import date

from fastapi import APIRouter, Depends, Query, Request

from app.core.auth import require_user
from app.core.errors import AppException, ErrorCode
from app.core.response import build_response
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse
from app.services.risk_service import calculate_deviation_risk

router = APIRouter()


@router.get("/deviation", response_model=ApiResponse)
def get_deviation_risk(
    request: Request,
    trade_date: date = Query(...),
    org_id: int = Query(..., ge=1),
    province_code: str = Query(..., min_length=2, max_length=8),
    rule_version: str | None = Query(default=None, min_length=1, max_length=32),
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    if not user.is_admin and org_id != user.org_id:
        raise AppException(
            code=ErrorCode.FORBIDDEN,
            message="cannot query risk for other org",
            status_code=403,
        )
    result = calculate_deviation_risk(
        trade_date=trade_date,
        org_id=org_id,
        province_code=province_code,
        rule_version=rule_version,
    )
    return build_response(request=request, data=result.model_dump())
