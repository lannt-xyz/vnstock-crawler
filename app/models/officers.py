from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    name = Column(String(255))
    position = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())