from datetime import date
from typing import List

from pydantic import BaseModel, Field

from app.schemas.common import IdempotentPayload


class TimeslotDeclaration(BaseModel):
    slot: str = Field(..., description="Example: 09:00-09:15")
    volume_mwh: float = Field(..., ge=0)
    price: float = Field(..., ge=0)


class TradeDeclarationRequest(IdempotentPayload):
    province_code: str = Field(..., min_length=2, max_length=8)
    rule_version: str | None = Field(default=None, min_length=1, max_length=32)
    trade_date: date
    market_type: str = Field(..., min_length=2, max_length=32)
    timeslots: List[TimeslotDeclaration] = Field(..., min_length=1, max_length=96)


class TradeDeclarationResponse(BaseModel):
    declaration_id: str
    status: str
    rule_version: str
    duplicate: bool = False
