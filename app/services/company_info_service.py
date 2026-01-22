from sqlalchemy.orm import Session

from app.crawler.cafef import CafefCrawler
from app.utils.decorators import cached_data, try_catch_decorator
from app.utils.gemini_api import generate
from app.utils.prompt_loader import PromptLoader, PromptTemplate
from app.utils.string_utils import clean_markdown_string


class CompanyInfoService:
    def __init__(self, db: Session):
        self.cafef_crawler = CafefCrawler()
        self.db = db
        self.prompt_loader = PromptLoader()

    @cached_data(cache_key_prefix="company_profile", extension="md")
    @try_catch_decorator
    def fetch_and_save_company_profiles(self, ticker: str):
        company_text = self.cafef_crawler.get_company_profile(ticker.upper())
        prompt = self.prompt_loader.apply_template(
            PromptTemplate.COMPANY_PROFILE, company_text=company_text
        )

        generated_response = generate(prompt)
        markdown = clean_markdown_string(generated_response)
        return markdown
