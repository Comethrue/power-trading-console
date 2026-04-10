from datetime import date

from pydantic import BaseModel, Field, model_validator


class ReconcileTaskRequest(BaseModel):
    org_id: int = Field(..., ge=1)
    province_code: str = Field(..., min_length=2, max_length=8)
    rule_version: str | None = Field(default=None, min_length=1, max_length=32)
    cycle_start: date
    cycle_end: date

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.cycle_end < self.cycle_start:
            raise ValueError("cycle_end must be greater than or equal to cycle_start")
        return self


class ReconcileTaskResponse(BaseModel):
    task_id: str
    status: str
    province_code: str
    rule_version: str


class ReconcileTaskStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(queued|running|completed|failed)$")
    message: str | None = Field(default=None, max_length=200)


class ReconcileTaskDetail(BaseModel):
    task_id: str
    org_id: int
    province_code: str
    rule_version: str
    cycle_start: date
    cycle_end: date
    status: str
    message: str | None = None
    created_at: str
    updated_at: str
