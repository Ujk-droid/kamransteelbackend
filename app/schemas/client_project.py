from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ClientProjectImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    created_at: datetime


class ClientProjectCreate(BaseModel):
    client_name: str
    category: str
    description: str


class ClientProjectUpdate(BaseModel):
    client_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ClientProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_name: str
    category: str
    description: str
    created_at: datetime
    images: List[ClientProjectImageRead] = []
