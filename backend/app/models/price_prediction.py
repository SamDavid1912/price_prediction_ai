from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class PricePrediction(Base):
    __tablename__ = "price_predictions"

    id = Column(Integer, primary_key=True, index=True)
    product_platform_id = Column(Integer, ForeignKey("product_platforms.id", ondelete="CASCADE"))
    predicted_price = Column(Numeric(10, 2))
    predicted_drop = Column(Numeric(10, 2))
    best_buy_time = Column(DateTime)
    confidence_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, server_default=func.now())