from datetime import date

from pydantic import BaseModel, Field


class DeviationRiskQuery(BaseModel):
    trade_date: date
    org_id: int = Field(..., ge=1)
    province_code: str = Field(..., min_length=2, max_length=8)
    rule_version: str | None = Field(default=None, min_length=1, max_length=32)


class DeviationRiskResponse(BaseModel):
    trade_date: date
    org_id: int
    province_code: str
    rule_version: str
    deviation_ratio: float
    deviation_risk_level: str
    expected_deviation_cost: float
