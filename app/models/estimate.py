from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Numeric
from sqlmodel import Field, SQLModel


class Estimate(SQLModel, table=True):
    __tablename__ = "estimates"

    id: Optional[int] = Field(default=None, primary_key=True)
    category: str
    size: str
    color: str
    material: str
    cost: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))

    advance_percent: float = 50
    mid_percent: float = 25
    final_percent: float = 25

    image_url: Optional[str] = None
    image_public_id: Optional[str] = None

    extra_specs: Optional[list[dict]] = Field(default=None, sa_column=Column(JSON, nullable=True))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
