from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class FAQ(SQLModel, table=True):
    __tablename__ = "faqs"

    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    answer: str
    display_order: int = 0

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
