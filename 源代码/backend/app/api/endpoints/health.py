from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.response import build_response
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("", response_model=ApiResponse)
def health_check(request: Request) -> ApiResponse:
    return build_response(
        request=request,
        data={
            "app": settings.app_name,
            "env": settings.app_env,
            "time": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
        },
    )
