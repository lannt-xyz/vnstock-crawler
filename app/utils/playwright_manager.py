from bs4 import BeautifulSoup
from playwright.sync_api import Page, sync_playwright
from playwright_stealth import Stealth
from tenacity import retry, stop_after_attempt, wait_random


class PlaywrightManager:
    _instance = None
    _playwright = None
    _browser = None

    @classmethod
    def get_browser(cls):
        if cls._browser is None:
            cls._playwright = sync_playwright().start()
            cls._browser = cls._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-webrtc",
                    "--disable-features=WebRTC-HW-Decoding,WebRTC-HW-Encoding",
                    "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--no-sandbox",
                ],
                slow_mo=1000,
            )
        return cls._browser

    @classmethod
    def get_page(cls) -> Page:
        browser = cls.get_browser()
        context = browser.new_context(no_viewport=True)
        context.set_default_timeout(15000)
        page = context.new_page()
        stealth = Stealth()
        stealth.apply_stealth_sync(page)

        return page

    @classmethod
    def close_all(cls):
        if cls._browser:
            cls._browser.close()
        if cls._playwright:
            cls._playwright.stop()

    @classmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=2, max=5),
    )
    def fetch_text(cls, url: str, selector: str = None) -> str:
        page: Page = PlaywrightManager.get_page()
        html_content = ""
        try:
            page.goto(url)
            if selector:
                element = page.wait_for_selector(selector)
                html_content = element.inner_text()
            else:
                html_content = page.content()
        finally:
            page.context.close()

        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator=" ", strip=True)
