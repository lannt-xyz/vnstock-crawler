from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class CompanyEvent(Base):
    __tablename__ = "company_events"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    event_type = Column(String(100))
    title = Column(String(500))
    description = Column(Text)
    event_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())