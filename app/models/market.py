from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class MarketListing(Base):
    __tablename__ = "market_listings"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True)
    company_name = Column(String(255))
    exchange = Column(String(50))
    sector = Column(String(100))
    industry = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MarketSector(Base):
    __tablename__ = "market_sectors"

    id = Column(Integer, primary_key=True, index=True)
    sector_name = Column(String(100))
    data = Column(Text)  # JSON of sector data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TopMover(Base):
    __tablename__ = "top_movers"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    type = Column(String(20))  # 'gainer' or 'loser'
    price_change = Column(Float)
    percent_change = Column(Float)
    volume = Column(Float)
    date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())