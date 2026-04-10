from fastapi import Request

from app.schemas.common import ApiResponse


def build_response(
    request: Request,
    data=None,
    success: bool = True,
    code: str = "OK",
    message: str = "ok",
) -> ApiResponse:
    request_id = getattr(request.state, "request_id", None)
    return ApiResponse(
        success=success,
        code=code,
        message=message,
        data=data,
        request_id=request_id,
    )
