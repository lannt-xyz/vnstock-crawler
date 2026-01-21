from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class CompanyNews(Base):
    __tablename__ = "company_news"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    title = Column(String(500))
    content = Column(Text)
    url = Column(String(500))
    published_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MacroNews(Base):
    __tablename__ = "macro_news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    content = Column(Text)
    url = Column(String(500))
    published_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())