from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime
from sqlmodel import Field, SQLModel


class ContactMessage(SQLModel, table=True):
    __tablename__ = "contact_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str
    is_read: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="false"),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
