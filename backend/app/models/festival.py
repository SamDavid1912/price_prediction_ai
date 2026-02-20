from sqlalchemy import Column, Integer, String, Date
from app.db.database import Base


class Festival(Base):
    __tablename__ = "festivals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    festival_date = Column(Date)
    expected_discount_level = Column(String(50))