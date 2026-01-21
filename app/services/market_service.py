import json
from vnstock import Vnstock
from sqlalchemy.orm import Session
from app.models.market import MarketListing, MarketSector, TopMover
from app.logger import logger

class MarketService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_save_listing(self):
        try:
            market = Vnstock().market()
            data = market.listing()

            for item in data:
                listing = MarketListing(
                    symbol=item.get('symbol'),
                    company_name=item.get('company_name', '')[:255],
                    exchange=item.get('exchange'),
                    sector=item.get('sector', '')[:255],
                    industry=item.get('industry', '')[:255]
                )
                existing = self.db.query(MarketListing).filter(MarketListing.symbol == item.get('symbol')).first()
                if not existing:
                    self.db.add(listing)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching market listing: {e}")
            self.db.rollback()

    def fetch_and_save_sector(self):
        try:
            market = Vnstock().market()
            data = market.sector()

            for item in data:
                sector = MarketSector(
                    sector_name=item.get('sector_name', '')[:255],
                    data=json.dumps(item)
                )
                self.db.add(sector)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching market sector: {e}")
            self.db.rollback()

    def fetch_and_save_top_movers(self):
        try:
            market = Vnstock().market()
            gainers = market.top_gainers()
            losers = market.top_losers()

            for item in gainers:
                mover = TopMover(
                    symbol=item.get('symbol'),
                    type='gainer',
                    price_change=item.get('price_change'),
                    percent_change=item.get('percent_change'),
                    volume=item.get('volume'),
                    date=item.get('date')
                )
                self.db.add(mover)

            for item in losers:
                mover = TopMover(
                    symbol=item.get('symbol'),
                    type='loser',
                    price_change=item.get('price_change'),
                    percent_change=item.get('percent_change'),
                    volume=item.get('volume'),
                    date=item.get('date')
                )
                self.db.add(mover)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching top movers: {e}")
            self.db.rollback()