from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_random

from app.utils.decorators import log_execution_time
from app.utils.playwright_manager import PlaywrightManager


class VietnambizCrawler:
    BASE_URL = "https://data.vietnambiz.vn"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=1, max=3),
    )
    @log_execution_time
    def get_macro_data(self):
        page = PlaywrightManager().get_page()
        url = f"{self.BASE_URL}/macro-economic"
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")

        text = soup.get_text(separator=" ", strip=True)
        return text
