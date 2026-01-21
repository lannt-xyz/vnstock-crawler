import json
import pandas as pd
from vnstock import Vnstock
from sqlalchemy.orm import Session
from app.models.financials import BalanceSheet, IncomeStatement, CashFlow
from app.models.ratios import Ratio
from app.logger import logger

class FinancialService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_save_balance_sheet(self, symbol: str, period: str = 'year'):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            data_df = stock.finance.balance_sheet(period=period)
            
            # Convert DataFrame to list of dicts
            data_list = data_df.to_dict('records')

            for item in data_list:
                bs = BalanceSheet(
                    symbol=item.get('ticker'),
                    period=period,
                    year=item.get('yearReport'),
                    quarter=None,
                    data=json.dumps(item)
                )
                self.db.add(bs)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching balance sheet for {symbol}: {e}")
            self.db.rollback()

    def fetch_and_save_income_statement(self, symbol: str, period: str = 'year'):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            data_df = stock.finance.income_statement(period=period)
            
            # Convert DataFrame to list of dicts
            data_list = data_df.to_dict('records')

            for item in data_list:
                is_ = IncomeStatement(
                    symbol=item.get('ticker'),
                    period=period,
                    year=item.get('yearReport'),
                    quarter=None,
                    data=json.dumps(item)
                )
                self.db.add(is_)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching income statement for {symbol}: {e}")
            self.db.rollback()

    def fetch_and_save_cash_flow(self, symbol: str, period: str = 'year'):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            data_df = stock.finance.cash_flow(period=period)
            
            # Convert DataFrame to list of dicts
            data_list = data_df.to_dict('records')

            for item in data_list:
                cf = CashFlow(
                    symbol=item.get('ticker'),
                    period=period,
                    year=item.get('yearReport'),
                    quarter=None,
                    data=json.dumps(item)
                )
                self.db.add(cf)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching cash flow for {symbol}: {e}")
            self.db.rollback()

    def fetch_and_save_ratios(self, symbol: str):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            data_df = stock.finance.ratio(period='quarter')
            
            # Handle MultiIndex columns by flattening them
            if isinstance(data_df.columns, pd.MultiIndex):
                data_df.columns = ['_'.join(col) if isinstance(col, tuple) else str(col) for col in data_df.columns]
            
            # Convert DataFrame to list of dicts
            data_list = data_df.to_dict('records')

            for item in data_list:
                ratio = Ratio(
                    symbol=item.get('ticker', symbol),
                    period='quarter',
                    year=item.get('yearReport'),
                    quarter=item.get('quarter'),
                    data=json.dumps(item)
                )
                self.db.add(ratio)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching ratios for {symbol}: {e}")
            self.db.rollback()