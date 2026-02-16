from pydantic import BaseModel


class ProductCreate(BaseModel):
    user_id: int
    product_url: str
    product_name: str
    platform: str

    class Config:
        from_attributes = True
