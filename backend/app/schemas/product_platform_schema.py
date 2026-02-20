from pydantic import BaseModel


class ProductPlatformCreate(BaseModel):
    product_id: int
    platform: str
    product_url: str


class ProductPlatformResponse(ProductPlatformCreate):
    id: int

    class Config:
        from_attributes = True