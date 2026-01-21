import json
from vnstock import Vnstock
from sqlalchemy.orm import Session
from app.models.events import CompanyEvent
from app.logger import logger

class EventService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_save_events(self, symbol: str):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            data = stock.events()

            for item in data:
                event = CompanyEvent(
                    symbol=symbol,
                    event_type=item.get('event_type'),
                    title=item.get('title', '')[:255],
                    description=item.get('description'),
                    event_date=item.get('event_date')
                )
                self.db.add(event)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching events for {symbol}: {e}")
            self.db.rollback()