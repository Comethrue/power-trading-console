from fastapi import APIRouter, Depends, Query, Request

from app.core.errors import AppException, ErrorCode
from app.core.auth import require_user
from app.core.response import build_response
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse
from app.schemas.trades import TradeDeclarationRequest
from app.services.audit_service import write_audit_log
from app.services.rule_service import resolve_trade_rule, validate_trade_with_rule
from app.services.trade_service import create_declaration, get_declaration_by_id, list_declarations

router = APIRouter()


@router.post("/declarations", response_model=ApiResponse)
def submit_declaration(
    request: Request,
    payload: TradeDeclarationRequest,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    rule = resolve_trade_rule(payload)
    validate_trade_with_rule(payload, rule)
    result = create_declaration(payload, rule_version=rule.version, org_id=user.org_id)
    write_audit_log(
        user=user,
        action="trade_declaration_create",
        resource_type="trade_declaration",
        resource_id=result.declaration_id,
        request_id=getattr(request.state, "request_id", None),
        details={
            "duplicate": result.duplicate,
            "province_code": payload.province_code,
            "rule_version": result.rule_version,
        },
    )
    return build_response(request=request, data=result.model_dump())


@router.get("/declarations/{declaration_id}", response_model=ApiResponse)
def get_declaration(
    request: Request,
    declaration_id: str,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    declaration = get_declaration_by_id(
        declaration_id=declaration_id,
        org_id=user.org_id,
        is_admin=user.is_admin,
    )
    if declaration is None:
        raise AppException(
            code=ErrorCode.TRADE_DECLARATION_NOT_FOUND,
            message="declaration not found",
            status_code=404,
        )

    return build_response(request=request, data=declaration)


@router.get("/declarations", response_model=ApiResponse)
def query_declarations(
    request: Request,
    page_no: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    result = list_declarations(
        page_no=page_no,
        page_size=page_size,
        org_id=user.org_id,
        is_admin=user.is_admin,
    )
    return build_response(request=request, data=result)
