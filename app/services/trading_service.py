import json
from vnstock import Vnstock
from sqlalchemy.orm import Session
from app.models.insider import InsiderTransaction
from app.models.foreign import ForeignTransaction
from app.logger import logger

class TradingService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_save_insider(self, symbol: str):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            data = stock.trading.insider()

            for item in data:
                insider = InsiderTransaction(
                    symbol=symbol,
                    date=item.get('date'),
                    insider_name=item.get('insider_name', '')[:255],
                    position=item.get('position', '')[:255],
                    transaction_type=item.get('transaction_type'),
                    shares=item.get('shares'),
                    price=item.get('price'),
                    value=item.get('value')
                )
                self.db.add(insider)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching insider for {symbol}: {e}")
            self.db.rollback()

    def fetch_and_save_foreign(self, symbol: str):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            data = stock.trading.foreign()

            for item in data:
                foreign = ForeignTransaction(
                    symbol=symbol,
                    date=item.get('date'),
                    net_buy_sell=item.get('net_buy_sell'),
                    buy_volume=item.get('buy_volume'),
                    sell_volume=item.get('sell_volume')
                )
                self.db.add(foreign)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching foreign for {symbol}: {e}")
            self.db.rollback()