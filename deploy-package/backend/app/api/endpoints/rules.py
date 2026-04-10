from datetime import date

from fastapi import APIRouter, Depends, Query, Request

from app.core.auth import require_user
from app.core.response import build_response
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse
from app.services.rule_service import get_rule, list_rule_versions

router = APIRouter()


@router.get("/versions", response_model=ApiResponse)
def query_rule_versions(
    request: Request,
    province_code: str = Query(..., min_length=2, max_length=8),
    _: UserContext = Depends(require_user),
) -> ApiResponse:
    versions = list_rule_versions(province_code)
    return build_response(
        request=request,
        data={"province_code": province_code.upper(), "versions": versions},
    )


@router.get("", response_model=ApiResponse)
def query_rule(
    request: Request,
    province_code: str = Query(..., min_length=2, max_length=8),
    version: str | None = Query(default=None, min_length=1, max_length=32),
    trade_date: date | None = Query(default=None),
    _: UserContext = Depends(require_user),
) -> ApiResponse:
    rule = get_rule(province_code=province_code, version=version, trade_date=trade_date)
    return build_response(request=request, data=rule.model_dump(mode="json"))
