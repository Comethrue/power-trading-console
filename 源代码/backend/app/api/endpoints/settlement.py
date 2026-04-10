from fastapi import APIRouter, Depends, Query, Request

from app.core.auth import require_user
from app.core.errors import AppException, ErrorCode
from app.core.response import build_response
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse
from app.schemas.settlement import ReconcileTaskRequest, ReconcileTaskStatusUpdateRequest
from app.services.audit_service import write_audit_log
from app.services.rule_service import resolve_settlement_rule, validate_settlement_with_rule
from app.services.settlement_service import (
    create_reconcile_task as enqueue_reconcile_task,
    get_reconcile_task,
    get_reconcile_summary,
    list_reconcile_tasks,
    update_reconcile_task_status,
)

router = APIRouter()


@router.post("/reconcile/tasks", response_model=ApiResponse)
def create_reconcile_task(
    request: Request,
    payload: ReconcileTaskRequest,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    if not user.is_admin and payload.org_id != user.org_id:
        raise AppException(
            code=ErrorCode.FORBIDDEN,
            message="cannot create task for other org",
            status_code=403,
        )

    if user.is_admin and payload.org_id <= 0:
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            message="org_id must be positive",
            status_code=422,
        )

    rule = resolve_settlement_rule(payload)
    validate_settlement_with_rule(payload, rule)
    result = enqueue_reconcile_task(payload, rule_version=rule.version)
    write_audit_log(
        user=user,
        action="reconcile_task_create",
        resource_type="reconcile_task",
        resource_id=result.task_id,
        request_id=getattr(request.state, "request_id", None),
        details={
            "org_id": payload.org_id,
            "province_code": payload.province_code,
            "rule_version": result.rule_version,
        },
    )
    return build_response(request=request, data=result.model_dump())


@router.get("/reconcile/tasks/{task_id}", response_model=ApiResponse)
def query_reconcile_task(
    request: Request,
    task_id: str,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    task = get_reconcile_task(task_id=task_id, org_id=user.org_id, is_admin=user.is_admin)
    if task is None:
        raise AppException(
            code=ErrorCode.RECONCILE_TASK_NOT_FOUND,
            message="reconcile task not found",
            status_code=404,
        )
    return build_response(request=request, data=task.model_dump(mode="json"))


@router.get("/reconcile/tasks", response_model=ApiResponse)
def query_reconcile_task_list(
    request: Request,
    page_no: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(default=None, pattern="^(queued|running|completed|failed)$"),
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    result = list_reconcile_tasks(
        page_no=page_no,
        page_size=page_size,
        org_id=user.org_id,
        is_admin=user.is_admin,
        status=status,
    )
    return build_response(request=request, data=result)


@router.patch("/reconcile/tasks/{task_id}/status", response_model=ApiResponse)
def update_reconcile_task(
    request: Request,
    task_id: str,
    payload: ReconcileTaskStatusUpdateRequest,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    result = update_reconcile_task_status(
        task_id=task_id,
        status=payload.status,
        org_id=user.org_id,
        is_admin=user.is_admin,
        message=payload.message,
    )
    write_audit_log(
        user=user,
        action="reconcile_task_status_update",
        resource_type="reconcile_task",
        resource_id=task_id,
        request_id=getattr(request.state, "request_id", None),
        details={"status": payload.status, "message": payload.message},
    )
    return build_response(request=request, data=result.model_dump(mode="json"))


@router.get("/reconcile/tasks/{task_id}/summary", response_model=ApiResponse)
def reconcile_task_summary(
    request: Request,
    task_id: str,
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    """查询结算任务的汇总报告：申报总量、均价、合同对比差异及逐日明细。"""
    summary = get_reconcile_summary(
        task_id=task_id,
        org_id=user.org_id,
        is_admin=user.is_admin,
    )
    return build_response(request=request, data=summary)
