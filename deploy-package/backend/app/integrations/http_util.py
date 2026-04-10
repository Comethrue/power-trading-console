from typing import Any

import httpx

from app.core.config import settings


def get_json(
    base_url: str,
    path: str,
    *,
    api_key: str,
    timeout_sec: float,
    params: dict[str, str | int | None] | None = None,
) -> Any:
    base = base_url.rstrip("/")
    p = path if path.startswith("/") else f"/{path}"
    url = f"{base}{p}"
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    query = {k: v for k, v in (params or {}).items() if v is not None and v != ""}
    with httpx.Client(timeout=timeout_sec) as client:
        resp = client.get(url, headers=headers, params=query)
        resp.raise_for_status()
        return resp.json()
