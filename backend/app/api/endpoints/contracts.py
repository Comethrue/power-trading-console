from fastapi import APIRouter, Depends, Query, Request

from app.core.auth import require_user
from app.core.errors import AppException, ErrorCode
from app.core.response import build_response
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse
from app.schemas.contracts import ContractRequest, ContractStatusUpdateRequest
from app.services.audit_service import write_audit_log
from app.services.contract_service import (
    create_contract,
    get_contract_by_id,
    list_contracts,
    update_contract_status,
)

router = APIRouter()


@router.post("/contracts", response_model=ApiResponse)
def submit_contract(
    request: Request,
    payload: ContractRequest,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    if not user.is_admin and payload.org_id != user.org_id:
        raise AppException(
            code=ErrorCode.FORBIDDEN,
            message="cannot create contract for other org",
            status_code=403,
        )

    if user.is_admin and payload.org_id <= 0:
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            message="org_id must be positive",
            status_code=422,
        )

    result = create_contract(payload)
    write_audit_log(
        user=user,
        action="contract_create",
        resource_type="contract",
        resource_id=result.contract_id,
        request_id=getattr(request.state, "request_id", None),
        details={
            "org_id": payload.org_id,
            "province_code": payload.province_code,
            "contract_type": payload.contract_type,
        },
    )
    return build_response(request=request, data=result.model_dump())


@router.get("/contracts/{contract_id}", response_model=ApiResponse)
def get_contract(
    request: Request,
    contract_id: str,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    contract = get_contract_by_id(
        contract_id=contract_id,
        org_id=user.org_id,
        is_admin=user.is_admin,
    )
    if contract is None:
        raise AppException(
            code=ErrorCode.CONTRACT_NOT_FOUND,
            message="contract not found",
            status_code=404,
        )

    return build_response(request=request, data=contract.model_dump(mode="json"))


@router.get("/contracts", response_model=ApiResponse)
def query_contracts(
    request: Request,
    page_no: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(default=None, pattern="^(active|expired|cancelled)$"),
    contract_type: str | None = Query(default=None, pattern="^(MEDIUM_LONG|SPOT_DA|SPOT_RT)$"),
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    result = list_contracts(
        page_no=page_no,
        page_size=page_size,
        org_id=user.org_id,
        is_admin=user.is_admin,
        status=status,
        contract_type=contract_type,
    )
    return build_response(request=request, data=result)


@router.patch("/contracts/{contract_id}/status", response_model=ApiResponse)
def update_contract(
    request: Request,
    contract_id: str,
    payload: ContractStatusUpdateRequest,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    result = update_contract_status(
        contract_id=contract_id,
        status=payload.status,
        org_id=user.org_id,
        is_admin=user.is_admin,
    )
    write_audit_log(
        user=user,
        action="contract_status_update",
        resource_type="contract",
        resource_id=contract_id,
        request_id=getattr(request.state, "request_id", None),
        details={"status": payload.status},
    )
    return build_response(request=request, data=result.model_dump(mode="json"))
