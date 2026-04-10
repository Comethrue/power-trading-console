from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool = True
    code: str = "OK"
    message: str = "ok"
    data: Any = None
    request_id: str | None = None


class IdempotentPayload(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=128)
