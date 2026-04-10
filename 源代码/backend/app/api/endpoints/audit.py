from fastapi import APIRouter, Depends, Query, Request

from app.core.auth import require_user
from app.core.response import build_response
from app.schemas.auth import UserContext
from app.schemas.common import ApiResponse
from app.services.audit_service import list_audit_logs

router = APIRouter()


@router.get("/logs", response_model=ApiResponse)
def query_audit_logs(
    request: Request,
    page_no: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    action: str | None = Query(default=None),
    user: UserContext = Depends(require_user),
) -> ApiResponse:
    result = list_audit_logs(
        page_no=page_no,
        page_size=page_size,
        user=user,
        action=action,
    )
    return build_response(request=request, data=result)
