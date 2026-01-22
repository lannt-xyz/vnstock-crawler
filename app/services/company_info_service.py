import json

from sqlalchemy.orm import Session

from app.crawler.cafef import CafefCrawler
from app.utils.date_util import DateUtils
from app.utils.decorators import cached_data, try_catch_decorator
from app.utils.gemini_api import generate
from app.utils.prompt_loader import PromptLoader, PromptTemplate
from app.utils.string_utils import clean_markdown_string


class CompanyInfoService:
    def __init__(self, db: Session):
        self.cafef_crawler = CafefCrawler()
        self.db = db
        self.prompt_loader = PromptLoader()

    @cached_data(cache_key_prefix="ticker_snapshot", extension="json")
    @try_catch_decorator
    def fetch_and_save_ticker_snapshot(self, ticker: str):
        # page =
        pass

    @try_catch_decorator
    def fetch_and_save_company_profiles(self, ticker: str):
        extracted_data = self._fetch_company_profile(ticker)

    @cached_data(cache_key_prefix="company_profile", extension="md")
    @try_catch_decorator
    def _fetch_company_profile(self, ticker: str):
        # If not in cache, fetch from web and process
        company_text = self.cafef_crawler.get_company_profile(ticker.upper())
        prompt = self.prompt_loader.apply_template(
            PromptTemplate.COMPANY_PROFILE, company_text=company_text
        )

        generated_response = generate(prompt)
        markdown = clean_markdown_string(generated_response)
        return markdown

    @try_catch_decorator
    def _save_company_data(self, ticker: str, data: dict):
        company_profile_dict = data.get("company_profile", {})
        if not company_profile_dict:
            return

        # first delete existing record if any
        self.db.query(CompanyProfile).filter(
            CompanyProfile.symbol == ticker.upper()
        ).delete()
        self.db.flush()

        # then create new record
        company_profile = CompanyProfile(**company_profile_dict)
        ## save to DB or further processing can be done here
        self.db.add(company_profile)
        self.db.commit()

    @try_catch_decorator
    def _save_balance_sheets(self, ticker: str, extracted_data: dict):
        ballance_sheets = extracted_data.get("balance_sheets", [])
        if not ballance_sheets:
            return

        # First delete existing records
        self.db.query(BalanceSheet).filter(
            BalanceSheet.symbol == ticker.upper()
        ).delete()
        self.db.flush()

        # Then add new records
        for sheet in ballance_sheets:
            # Lấy phần data (là một dict) và chuyển thành string JSON
            raw_data = sheet.get("data")
            json_data_string = (
                json.dumps(raw_data, ensure_ascii=False)
                if isinstance(raw_data, dict)
                else raw_data
            )
            new_sheet = BalanceSheet(
                symbol=ticker.upper(),
                period=sheet.get("period"),
                year=sheet.get("year"),
                quarter=sheet.get("quarter"),
                data=json_data_string,
            )
            self.db.add(new_sheet)
        self.db.commit()

    @try_catch_decorator
    def _save_income_statements(self, ticker: str, extracted_data: dict):
        income_statements = extracted_data.get("income_statements", [])
        if not income_statements:
            return

        # First delete existing records
        self.db.query(IncomeStatement).filter(
            IncomeStatement.symbol == ticker.upper()
        ).delete()
        self.db.flush()

        # Then add new records
        for statement in income_statements:
            raw_data = statement.get("data")
            json_data_string = (
                json.dumps(raw_data, ensure_ascii=False)
                if isinstance(raw_data, dict)
                else raw_data
            )
            income_statement = IncomeStatement(
                symbol=ticker.upper(),
                period=statement.get("period"),
                year=statement.get("year"),
                quarter=statement.get("quarter"),
                data=json_data_string,
            )
            # save to DB or further processing can be done here
            self.db.add(income_statement)
        self.db.commit()

    @try_catch_decorator
    def _save_cash_flows(self, ticker: str, extracted_data: dict):
        cash_flows = extracted_data.get("cash_flows", [])
        if not cash_flows:
            return

        # First delete existing records
        self.db.query(CashFlow).filter(CashFlow.symbol == ticker.upper()).delete()
        self.db.flush()

        # Then add new records
        for flow in cash_flows:
            raw_data = flow.get("data")
            json_data_string = (
                json.dumps(raw_data, ensure_ascii=False)
                if isinstance(raw_data, dict)
                else raw_data
            )
            cash_flow = CashFlow(
                symbol=ticker.upper(),
                period=flow.get("period"),
                year=flow.get("year"),
                quarter=flow.get("quarter"),
                data=json_data_string,
            )
            # save to DB or further processing can be done here
            self.db.add(cash_flow)
        self.db.commit()

    @try_catch_decorator
    def _save_officers(self, ticker: str, extracted_data: dict):
        officers = extracted_data.get("officers", [])
        if not officers:
            return

        # First delete existing records
        self.db.query(Officer).filter(Officer.symbol == ticker.upper()).delete()
        self.db.flush()

        # Then add new records
        for off in officers:
            officer = Officer(
                symbol=ticker.upper(),
                name=off.get("name"),
                position=off.get("position"),
            )
            # save to DB or further processing can be done here
            self.db.add(officer)
        self.db.commit()

    @try_catch_decorator
    def _save_ratios(self, ticker: str, extracted_data: dict):
        ratios = extracted_data.get("ratios", [])
        if not ratios:
            return

        # First delete existing records
        self.db.query(Ratio).filter(Ratio.symbol == ticker.upper()).delete()
        self.db.flush()

        # Then add new records
        for rat in ratios:
            raw_data = rat.get("data")
            json_data_string = (
                json.dumps(raw_data, ensure_ascii=False)
                if isinstance(raw_data, dict)
                else raw_data
            )
            ratio = Ratio(
                symbol=ticker.upper(),
                period=rat.get("period"),
                year=rat.get("year"),
                quarter=rat.get("quarter"),
                data=json_data_string,
            )
            # save to DB or further processing can be done here
            self.db.add(ratio)
        self.db.commit()

    @try_catch_decorator
    def _save_shareholders(self, ticker: str, extracted_data: dict):
        shareholders = extracted_data.get("shareholders", [])
        if not shareholders:
            return

        # First delete existing records
        self.db.query(Shareholder).filter(Shareholder.symbol == ticker.upper()).delete()
        self.db.flush()

        # Then add new records
        for sh in shareholders:
            shareholder = Shareholder(
                symbol=ticker.upper(),
                shareholder_name=sh.get("shareholder_name"),
                ownership_percent=sh.get("ownership_percent"),
                shares_owned=sh.get("shares_owned"),
            )
            # save to DB or further processing can be done here
            self.db.add(shareholder)
        self.db.commit()

    @try_catch_decorator
    def _save_insider_transactions(self, ticker: str, extracted_data: dict):
        insider_transactions = extracted_data.get("insider_transactions", [])
        if not insider_transactions:
            return

        # First delete existing records
        self.db.query(InsiderTransaction).filter(
            InsiderTransaction.symbol == ticker.upper()
        ).delete()
        self.db.flush()

        # Then add new records
        for it in insider_transactions:
            insider_transaction = InsiderTransaction(
                symbol=ticker.upper(),
                date=DateUtils.parse_date(it.get("date")),
                insider_name=it.get("insider_name"),
                position=it.get("position"),
                transaction_type=it.get("transaction_type"),
                shares=it.get("shares"),
                price=it.get("price"),
                value=it.get("value"),
            )
            # save to DB or further processing can be done here
            self.db.add(insider_transaction)
        self.db.commit()

    @try_catch_decorator
    def _save_foreign_transactions(self, ticker: str, extracted_data: dict):
        foreign_transactions = extracted_data.get("foreign_transactions", [])
        if not foreign_transactions:
            return

        # First delete existing records
        self.db.query(ForeignTransaction).filter(
            ForeignTransaction.symbol == ticker.upper()
        ).delete()
        self.db.flush()

        # Then add new records
        for ft in foreign_transactions:
            foreign_transaction = ForeignTransaction(
                symbol=ticker.upper(),
                date=DateUtils.parse_date(ft.get("date")),
                net_buy_sell=ft.get("net_buy_sell"),
                buy_volume=ft.get("buy_volume"),
                sell_volume=ft.get("sell_volume"),
            )
            # save to DB or further processing can be done here
            self.db.add(foreign_transaction)
        self.db.commit()
