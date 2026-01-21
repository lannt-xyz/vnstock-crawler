import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.company_service import CompanyService
from app.logger import logger

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python sync_companies.py <symbol>")
        sys.exit(1)

    symbol = sys.argv[1]
    db = SessionLocal()
    try:
        service = CompanyService(db)
        logger.info(f"Syncing company data for {symbol}...")
        service.fetch_and_save_profile(symbol)
        service.fetch_and_save_shareholders(symbol)
        service.fetch_and_save_officers(symbol)
        logger.info("Done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()