from sqlalchemy import Column, Integer, Numeric, Boolean, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_platform_id = Column(Integer, ForeignKey("product_platforms.id", ondelete="CASCADE"))
    price = Column(Numeric(10, 2), nullable=False)
    availability = Column(Boolean, default=True)
    seller = Column(String(255))
    recorded_at = Column(DateTime, server_default=func.now())

    platform = relationship("ProductPlatform", back_populates="price_history")