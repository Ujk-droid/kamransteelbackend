from datetime import datetime

from pydantic import BaseModel


class ContactMessageCreate(BaseModel):
    name: str
    email: str
    message: str


class ContactMessageRead(BaseModel):
    id: int
    name: str
    email: str
    message: str
    is_read: bool
    created_at: datetime
