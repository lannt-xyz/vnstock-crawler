from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class BalanceSheet(Base):
    __tablename__ = "balance_sheets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    period = Column(String(20))  # quarter or year
    year = Column(Integer)
    quarter = Column(Integer, nullable=True)
    data = Column(Text)  # JSON string of balance sheet data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IncomeStatement(Base):
    __tablename__ = "income_statements"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    period = Column(String(20))
    year = Column(Integer)
    quarter = Column(Integer, nullable=True)
    data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CashFlow(Base):
    __tablename__ = "cash_flows"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    period = Column(String(20))
    year = Column(Integer)
    quarter = Column(Integer, nullable=True)
    data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())