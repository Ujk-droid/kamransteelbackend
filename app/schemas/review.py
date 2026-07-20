from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.review import ReviewStatus


class ReviewCreate(BaseModel):
    client_name: str
    rating: int = Field(ge=1, le=5)
    review_text: str


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_name: str
    rating: int
    review_text: str
    status: ReviewStatus
    created_at: datetime
