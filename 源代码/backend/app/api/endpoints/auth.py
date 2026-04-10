from fastapi import APIRouter, Depends, Request

from app.core.auth import authenticate_user, create_access_token, require_user, _user_map
from app.core.config import settings
from app.core.errors import AppException, ErrorCode
from app.core.response import build_response
from app.schemas.auth import UserContext
from app.schemas.auth_api import LoginRequest, LoginResponse, LogoutRequest, RefreshRequest, RegisterRequest
from app.schemas.common import ApiResponse
from app.services.auth_session_service import (
    issue_refresh_token,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.services.user_credentials_service import (
    create_registered_user,
    username_exists_in_db,
    validate_username,
)

router = APIRouter()


def _login_response_for_user(request: Request, user: UserContext) -> ApiResponse:
    token, expires_in = create_access_token(
        username=user.username or "",
        org_id=user.org_id,
        role=user.role,
    )
    refresh_token, refresh_expires_in = issue_refresh_token(user)
    data = LoginResponse(
        access_token=token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        refresh_expires_in=refresh_expires_in,
        username=user.username or "",
        org_id=user.org_id,
        role=user.role,
    ).model_dump()
    return build_response(request=request, data=data)


@router.post("/register", response_model=ApiResponse)
def register(request: Request, payload: RegisterRequest) -> ApiResponse:
    uname = validate_username(payload.username)
    if uname is None:
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            message="用户名需 3–32 位，仅字母、数字、下划线，且不能使用保留账号",
            status_code=422,
        )

    for key in _user_map():
        if key.lower() == uname:
            raise AppException(
                code=ErrorCode.AUTH_USERNAME_TAKEN,
                message="用户名已被占用",
                status_code=409,
            )

    if username_exists_in_db(uname):
        raise AppException(
            code=ErrorCode.AUTH_USERNAME_TAKEN,
            message="用户名已被占用",
            status_code=409,
        )

    org_id, role = create_registered_user(uname, payload.password)
    user = UserContext(token="", org_id=org_id, role=role, username=uname)
    return _login_response_for_user(request, user)


@router.post("/login", response_model=ApiResponse)
def login(request: Request, payload: LoginRequest) -> ApiResponse:
    user = authenticate_user(payload.username, payload.password)
    if user is None:
        raise AppException(
            code=ErrorCode.AUTH_LOGIN_FAILED,
            message="invalid username or password",
            status_code=401,
        )

    if not user.username:
        user = UserContext(
            token=user.token,
            org_id=user.org_id,
            role=user.role,
            username=payload.username,
        )
    return _login_response_for_user(request, user)


@router.post("/refresh", response_model=ApiResponse)
def refresh(request: Request, payload: RefreshRequest) -> ApiResponse:
    rotated = rotate_refresh_token(payload.refresh_token)
    if rotated is None:
        raise AppException(
            code=ErrorCode.AUTH_REFRESH_INVALID,
            message="invalid or expired refresh token",
            status_code=401,
        )

    user, new_refresh_token, refresh_expires_in = rotated
    access_token, expires_in = create_access_token(
        username=user.username or "unknown",
        org_id=user.org_id,
        role=user.role,
    )
    data = LoginResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
        refresh_expires_in=refresh_expires_in,
        username=user.username or "unknown",
        org_id=user.org_id,
        role=user.role,
    ).model_dump()
    return build_response(request=request, data=data)


@router.post("/logout", response_model=ApiResponse)
def logout(
    request: Request,
    payload: LogoutRequest,
    _: UserContext = Depends(require_user),
) -> ApiResponse:
    revoked = revoke_refresh_token(payload.refresh_token)
    return build_response(request=request, data={"revoked": revoked})


@router.get("/sso/config", response_model=ApiResponse)
def sso_config(request: Request) -> ApiResponse:
    """公开：告知前端是否启用 OIDC Bearer 校验及 Issuer（不含密钥）。"""
    issuer = (settings.auth_oidc_issuer or "").strip()
    return build_response(
        request=request,
        data={
            "oidc_enabled": settings.auth_oidc_enabled,
            "issuer": issuer if settings.auth_oidc_enabled else "",
            "audience_configured": bool((settings.auth_oidc_audience or "").strip()),
            "jwks_url_configured": bool((settings.auth_oidc_jwks_url or "").strip()),
            "username_claim": settings.auth_oidc_username_claim,
            "org_id_claim": settings.auth_oidc_org_id_claim,
            "role_claim": settings.auth_oidc_role_claim,
        },
    )


@router.get("/whoami", response_model=ApiResponse)
def whoami(request: Request, user: UserContext = Depends(require_user)) -> ApiResponse:
    return build_response(
        request=request,
        data={
            "username": user.username,
            "org_id": user.org_id,
            "role": user.role,
            "is_admin": user.is_admin,
        },
    )
