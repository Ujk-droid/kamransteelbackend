from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ProductImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    created_at: datetime


class ProductCreate(BaseModel):
    title: str
    category: str
    description: str


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str
    description: str
    created_at: datetime
    images: List[ProductImageRead] = []
