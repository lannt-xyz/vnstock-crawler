#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.financial_service import FinancialService
from app.logger import logger

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python sync_financials.py <symbol>")
        sys.exit(1)

    symbol = sys.argv[1]
    db = SessionLocal()
    try:
        service = FinancialService(db)
        logger.info(f"Syncing financial data for {symbol}...")
        service.fetch_and_save_balance_sheet(symbol)
        service.fetch_and_save_income_statement(symbol)
        service.fetch_and_save_cash_flow(symbol)
        service.fetch_and_save_ratios(symbol)
        logger.info("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()