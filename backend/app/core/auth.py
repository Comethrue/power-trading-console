import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.errors import AppException, ErrorCode
from app.core.oidc import verify_oidc_access_token
from app.schemas.auth import UserContext

bearer = HTTPBearer(auto_error=False)


@dataclass
class UserRecord:
    username: str
    password: str
    org_id: int
    role: str


@lru_cache(maxsize=1)
def _token_map() -> dict[str, UserContext]:
    mapping: dict[str, UserContext] = {}
    for item in settings.auth_tokens.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split(":")
        if len(parts) != 3:
            continue
        token, org_id, role = parts
        try:
            mapping[token] = UserContext(token=token, org_id=int(org_id), role=role, username=None)
        except ValueError:
            continue
    return mapping


@lru_cache(maxsize=1)
def _user_map() -> dict[str, UserRecord]:
    mapping: dict[str, UserRecord] = {}
    for item in settings.auth_users.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split(":")
        if len(parts) != 4:
            continue
        username, password, org_id, role = parts
        try:
            mapping[username] = UserRecord(
                username=username,
                password=password,
                org_id=int(org_id),
                role=role,
            )
        except ValueError:
            continue
    return mapping


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def _jwt_sign(header_payload: str) -> str:
    digest = hmac.new(
        settings.auth_jwt_secret.encode("utf-8"),
        header_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _b64url_encode(digest)


def create_access_token(username: str, org_id: int, role: str) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.auth_jwt_exp_minutes)
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "org_id": org_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": secrets.token_hex(8),
    }
    header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}"
    signature = _jwt_sign(signing_input)
    token = f"{signing_input}.{signature}"
    return token, settings.auth_jwt_exp_minutes * 60


def _verify_jwt(token: str) -> UserContext | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        header_raw = _b64url_decode(header_b64)
        header = json.loads(header_raw.decode("utf-8"))
        if header.get("alg") != "HS256":
            return None
        signing_input = f"{header_b64}.{payload_b64}"
        expected_sig = _jwt_sign(signing_input)
        if not hmac.compare_digest(expected_sig, signature_b64):
            return None

        payload_raw = _b64url_decode(payload_b64)
        payload = json.loads(payload_raw.decode("utf-8"))

        exp = int(payload.get("exp", 0))
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if exp <= now_ts:
            return None

        username = str(payload.get("sub", ""))
        org_id = int(payload.get("org_id", 0))
        role = str(payload.get("role", "trader"))
        return UserContext(token=token, org_id=org_id, role=role, username=username or None)
    except Exception:
        return None


def authenticate_user(username: str, password: str) -> UserContext | None:
    user = _user_map().get(username)
    if user is not None:
        if user.password != password:
            return None
        return UserContext(
            token="",
            org_id=user.org_id,
            role=user.role,
            username=user.username,
        )

    from app.services.user_credentials_service import verify_registered_user

    ru = verify_registered_user(username, password)
    if ru is None:
        return None
    return UserContext(
        token="",
        org_id=ru["org_id"],
        role=ru["role"],
        username=ru["username"],
    )


def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> UserContext:
    if not settings.auth_enabled:
        return UserContext(token="dev-admin", org_id=0, role="admin", username="dev-admin")

    if credentials is None:
        raise AppException(
            code=ErrorCode.AUTH_REQUIRED,
            message="authorization required",
            status_code=401,
        )

    token = credentials.credentials
    user = _token_map().get(token)
    if user is None and settings.auth_jwt_enabled:
        user = _verify_jwt(token)
    if user is None:
        user = verify_oidc_access_token(token)
    if user is None:
        raise AppException(
            code=ErrorCode.AUTH_INVALID,
            message="invalid token",
            status_code=401,
        )
    return user
