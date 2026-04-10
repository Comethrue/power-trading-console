from datetime import date

from pydantic import BaseModel, Field, model_validator


class ContractRequest(BaseModel):
    org_id: int = Field(..., ge=1)
    province_code: str = Field(..., min_length=2, max_length=8)
    contract_type: str = Field(..., pattern="^(MEDIUM_LONG|SPOT_DA|SPOT_RT)$")
    counterpart: str | None = Field(default=None, max_length=128)
    volume_mwh: float = Field(..., gt=0)
    price: float = Field(..., ge=0)
    start_date: date
    end_date: date
    remark: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class ContractResponse(BaseModel):
    contract_id: str
    status: str


class ContractDetail(BaseModel):
    contract_id: str
    org_id: int
    province_code: str
    contract_type: str
    counterpart: str | None = None
    volume_mwh: float
    price: float
    start_date: date
    end_date: date
    status: str
    remark: str | None = None
    created_at: str
    updated_at: str


class ContractStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(active|expired|cancelled)$")
