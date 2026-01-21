#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.trading_service import TradingService
from app.logger import logger

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python sync_trading.py <symbol>")
        sys.exit(1)

    symbol = sys.argv[1]
    db = SessionLocal()
    try:
        service = TradingService(db)
        logger.info(f"Syncing trading data for {symbol}...")
        service.fetch_and_save_insider(symbol)
        service.fetch_and_save_foreign(symbol)
        logger.info("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()