#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.macro_service import MacroService
from app.services.news_service import NewsService
from app.logger import logger

def main():
    db = SessionLocal()
    try:
        macro_service = MacroService(db)
        news_service = NewsService(db)
        logger.info("Syncing macro data...")
        macro_service.fetch_and_save_gdp()
        macro_service.fetch_and_save_cpi()
        macro_service.fetch_and_save_interest_rate()
        macro_service.fetch_and_save_exchange_rate()
        macro_service.fetch_and_save_commodity()
        news_service.fetch_and_save_macro_news()
        logger.info("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()