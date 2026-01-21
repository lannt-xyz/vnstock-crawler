from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Ratio(Base):
    __tablename__ = "ratios"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    period = Column(String(20))
    year = Column(Integer)
    quarter = Column(Integer, nullable=True)
    data = Column(Text)  # JSON string of ratios
    created_at = Column(DateTime(timezone=True), server_default=func.now())