from sqlalchemy.orm import Session

from app.crawler.cafef import CafefCrawler
from app.crawler.vietnambiz import VietnambizCrawler
from app.utils.decorators import cached_data, try_catch_decorator
from app.utils.gemini_api import generate
from app.utils.prompt_loader import PromptLoader, PromptTemplate
from app.utils.string_utils import clean_markdown_string


class MacroService:
    def __init__(self, db: Session):
        self.db = db
        self.cafef_crawler = CafefCrawler()
        self.vietnambiz = VietnambizCrawler()
        self.prompt_loader = PromptLoader()

    @cached_data(cache_key_prefix="macro_data", extension="md")
    @try_catch_decorator
    def fetch_and_save_macro_data(self):
        cafef_data = self.cafef_crawler.get_macro_data()
        vietnambiz_data = self.vietnambiz.get_macro_data()
        macro_data = f"Cafef Data:\n{cafef_data}\n\nVietnambiz Data:\n{vietnambiz_data}"
        prompt = self.prompt_loader.apply_template(
            PromptTemplate.MACRO_DATA, macro_data=macro_data
        )
        response = generate(prompt)
        markdown_text = clean_markdown_string(response)
        return markdown_text
