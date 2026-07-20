from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


class ClientProject(SQLModel, table=True):
    __tablename__ = "client_projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_name: str
    category: str
    description: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    images: List["ClientProjectImage"] = Relationship(
        back_populates="client_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ClientProjectImage(SQLModel, table=True):
    __tablename__ = "client_project_images"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_project_id: int = Field(foreign_key="client_projects.id")
    image_url: str
    public_id: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    client_project: Optional[ClientProject] = Relationship(back_populates="images")
