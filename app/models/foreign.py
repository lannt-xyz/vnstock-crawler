from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class ForeignTransaction(Base):
    __tablename__ = "foreign_transactions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    date = Column(DateTime)
    net_buy_sell = Column(Float)
    buy_volume = Column(Float)
    sell_volume = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())