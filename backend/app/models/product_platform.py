from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class ProductPlatform(Base):
    __tablename__ = "product_platforms"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    platform = Column(String(50), nullable=False)
    product_url = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="platforms")
    price_history = relationship("PriceHistory", back_populates="platform", cascade="all, delete")