from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class MacroData(Base):
    __tablename__ = "macro_data"

    id = Column(Integer, primary_key=True, index=True)
    indicator = Column(String(100))  # gdp, cpi, interest_rate, etc.
    price = Column(Float)
    changed_percent = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
