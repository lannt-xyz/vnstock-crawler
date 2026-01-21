#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.news_service import NewsService
from app.logger import logger

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python sync_news.py <symbol>")
        sys.exit(1)

    symbol = sys.argv[1]
    db = SessionLocal()
    try:
        service = NewsService(db)
        logger.info(f"Syncing news for {symbol}...")
        service.fetch_and_save_company_news(symbol)
        logger.info("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()