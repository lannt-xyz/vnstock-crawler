from app.database import SessionLocal
from app.services.company_service import CompanyService
from app.services.financial_service import FinancialService
from app.services.trading_service import TradingService
from app.services.news_service import NewsService
from app.services.event_service import EventService
from app.services.market_service import MarketService
from app.services.macro_service import MacroService

def sync_company_data(symbol: str):
    db = SessionLocal()
    try:
        service = CompanyService(db)
        service.fetch_and_save_profile(symbol)
        service.fetch_and_save_shareholders(symbol)
        service.fetch_and_save_officers(symbol)
    finally:
        db.close()

def sync_financial_data(symbol: str):
    db = SessionLocal()
    try:
        service = FinancialService(db)
        service.fetch_and_save_balance_sheet(symbol)
        service.fetch_and_save_income_statement(symbol)
        service.fetch_and_save_cash_flow(symbol)
        service.fetch_and_save_ratios(symbol)
    finally:
        db.close()

def sync_trading_data(symbol: str):
    db = SessionLocal()
    try:
        service = TradingService(db)
        service.fetch_and_save_insider(symbol)
        service.fetch_and_save_foreign(symbol)
    finally:
        db.close()

def sync_news_data(symbol: str):
    db = SessionLocal()
    try:
        service = NewsService(db)
        service.fetch_and_save_company_news(symbol)
    finally:
        db.close()

def sync_event_data(symbol: str):
    db = SessionLocal()
    try:
        service = EventService(db)
        service.fetch_and_save_events(symbol)
    finally:
        db.close()

def sync_market_data():
    db = SessionLocal()
    try:
        service = MarketService(db)
        service.fetch_and_save_listing()
        service.fetch_and_save_sector()
        service.fetch_and_save_top_movers()
    finally:
        db.close()

def sync_macro_data():
    db = SessionLocal()
    try:
        service = MacroService(db)
        service.fetch_and_save_gdp()
        service.fetch_and_save_cpi()
        service.fetch_and_save_interest_rate()
        service.fetch_and_save_exchange_rate()
        service.fetch_and_save_commodity()

        # Also sync macro news
        news_service = NewsService(db)
        news_service.fetch_and_save_macro_news()
    finally:
        db.close()