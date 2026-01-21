from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class InsiderTransaction(Base):
    __tablename__ = "insider_transactions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    date = Column(DateTime)
    insider_name = Column(String(255))
    position = Column(String(255))
    transaction_type = Column(String(50))
    shares = Column(Float)
    price = Column(Float)
    value = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())