from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base



class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    product_name = Column(String(255), nullable=False)
    product_url = Column(String(500), nullable=False)
    platform = Column(String(100), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
