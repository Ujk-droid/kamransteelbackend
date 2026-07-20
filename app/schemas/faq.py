from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FAQCreate(BaseModel):
    question: str
    answer: str
    display_order: int = 0


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    display_order: Optional[int] = None


class FAQRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    answer: str
    display_order: int
    created_at: datetime


class AskRequest(BaseModel):
    message: str


class AskResponse(BaseModel):
    matched: bool
    answer: str
    faq_id: Optional[int] = None
