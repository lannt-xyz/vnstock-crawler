from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Shareholder(Base):
    __tablename__ = "shareholders"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    shareholder_name = Column(String(255))
    ownership_percent = Column(Float)
    shares_owned = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())