from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator


class ExtraSpec(BaseModel):
    label: str
    value: str


class EstimateCreate(BaseModel):
    category: str
    size: str
    color: str
    material: str
    cost: Decimal
    advance_percent: float = 50
    mid_percent: float = 25
    final_percent: float = 25
    extra_specs: list[ExtraSpec] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_percentages_sum_to_100(self) -> "EstimateCreate":
        total = self.advance_percent + self.mid_percent + self.final_percent
        if abs(total - 100) > 0.01:
            raise ValueError(
                f"advance_percent + mid_percent + final_percent must add up to 100 (got {total})"
            )
        return self


class EstimateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    size: str
    color: str
    material: str
    cost: Decimal
    advance_percent: float
    mid_percent: float
    final_percent: float
    image_url: Optional[str] = None
    extra_specs: list[ExtraSpec] = Field(default_factory=list)
    created_at: datetime

    @field_validator("extra_specs", mode="before")
    @classmethod
    def _default_extra_specs(cls, v):
        return v or []

    @computed_field
    @property
    def advance_amount(self) -> Decimal:
        return (self.cost * Decimal(str(self.advance_percent)) / 100).quantize(Decimal("0.01"))

    @computed_field
    @property
    def mid_amount(self) -> Decimal:
        return (self.cost * Decimal(str(self.mid_percent)) / 100).quantize(Decimal("0.01"))

    @computed_field
    @property
    def final_amount(self) -> Decimal:
        return (self.cost * Decimal(str(self.final_percent)) / 100).quantize(Decimal("0.01"))


class GenerateImageRequest(BaseModel):
    custom_prompt: Optional[str] = None


class EstimateExtraction(BaseModel):
    category: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    cost: Optional[Decimal] = None
    extra_specs: list[ExtraSpec] = Field(default_factory=list)
