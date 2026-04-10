"""Verify OIDC / SSO access tokens (RS256) via JWKS."""

from functools import lru_cache

import httpx
import jwt
from jwt import PyJWKClient, PyJWTError

from app.core.config import settings
from app.schemas.auth import UserContext


@lru_cache(maxsize=2)
def _discover_jwks_uri(issuer: str) -> str:
    base = issuer.rstrip("/")
    url = f"{base}/.well-known/openid-configuration"
    with httpx.Client(timeout=settings.auth_oidc_discovery_timeout_sec) as client:
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.json()
    jwks = data.get("jwks_uri")
    if not jwks:
        raise ValueError("openid-configuration missing jwks_uri")
    return str(jwks)


def _jwks_url() -> str:
    if settings.auth_oidc_jwks_url.strip():
        return settings.auth_oidc_jwks_url.strip()
    issuer = settings.auth_oidc_issuer.strip()
    if not issuer:
        raise ValueError("auth_oidc_jwks_url or auth_oidc_issuer required")
    return _discover_jwks_uri(issuer)


_jwk_client: PyJWKClient | None = None


def _get_jwk_client() -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        _jwk_client = PyJWKClient(_jwks_url())
    return _jwk_client


def reset_oidc_jwks_cache() -> None:
    """Test hook: clear JWKS client after settings change."""
    global _jwk_client
    _jwk_client = None
    _discover_jwks_uri.cache_clear()


def verify_oidc_access_token(token: str) -> UserContext | None:
    if not settings.auth_oidc_enabled:
        return None
    issuer = settings.auth_oidc_issuer.strip()
    if not issuer and not settings.auth_oidc_jwks_url.strip():
        return None

    try:
        jwks_client = _get_jwk_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        decode_kwargs: dict = {
            "algorithms": ["RS256"],
            "options": {"verify_aud": False, "verify_iss": bool(issuer)},
        }
        if issuer:
            decode_kwargs["issuer"] = issuer.rstrip("/")
        if settings.auth_oidc_audience.strip():
            decode_kwargs["audience"] = settings.auth_oidc_audience.strip()
            decode_kwargs["options"]["verify_aud"] = True

        payload = jwt.decode(token, signing_key.key, **decode_kwargs)

        username = str(payload.get(settings.auth_oidc_username_claim) or payload.get("sub") or "")
        role = str(payload.get(settings.auth_oidc_role_claim) or settings.auth_oidc_default_role)
        raw_org = payload.get(settings.auth_oidc_org_id_claim)
        if raw_org is None:
            return None
        try:
            org_id = int(raw_org)
        except (TypeError, ValueError):
            return None

        return UserContext(token=token, org_id=org_id, role=role, username=username or None)
    except PyJWTError:
        return None
    except (httpx.HTTPError, ValueError, KeyError):
        return None
