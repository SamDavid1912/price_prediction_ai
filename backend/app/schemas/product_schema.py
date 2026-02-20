from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None


class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True
