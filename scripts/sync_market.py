#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.market_service import MarketService
from app.logger import logger

def main():
    db = SessionLocal()
    try:
        service = MarketService(db)
        logger.info("Syncing market data...")
        service.fetch_and_save_listing()
        service.fetch_and_save_sector()
        service.fetch_and_save_top_movers()
        logger.info("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()