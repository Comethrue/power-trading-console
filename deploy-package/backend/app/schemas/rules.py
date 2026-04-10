from datetime import date

from pydantic import BaseModel, Field


class TradeRuleConfig(BaseModel):
    price_min: float = Field(..., ge=0)
    price_max: float = Field(..., ge=0)
    volume_min: float = Field(..., ge=0)
    volume_max: float = Field(..., ge=0)
    timeslot_max_count: int = Field(..., ge=1)


class RiskRuleConfig(BaseModel):
    base_cost: float = Field(..., gt=0)
    medium_threshold: float = Field(..., ge=0, le=1)
    high_threshold: float = Field(..., ge=0, le=1)


class SettlementRuleConfig(BaseModel):
    max_cycle_days: int = Field(..., ge=1)
    deviation_penalty_coef: float = Field(..., gt=0)


class ProvinceRule(BaseModel):
    province_code: str = Field(..., min_length=2, max_length=8)
    version: str = Field(..., min_length=1, max_length=32)
    effective_start: date
    effective_end: date | None = None
    trade: TradeRuleConfig
    risk: RiskRuleConfig
    settlement: SettlementRuleConfig


class RuleVersionsResponse(BaseModel):
    province_code: str
    versions: list[str]
