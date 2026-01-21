import re
import requests

from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_random
from playwright.sync_api import Page

from app.logger import logger
from app.utils.cache_service import CacheService
from app.utils.playwright_manager import PlaywrightManager

class CafefCrawler:
    BASE_URL = "https://cafef.vn"
    def __init__(self):
        self.cache = CacheService()


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=1, max=3),
    )
    def get_all_companies(self):
        cache_key = "cafef_companies"
        
        # 1. Thử lấy từ cache
        cached_data = self.cache.get(cache_key)
        if cached_data:
            print(f"Loaded {cache_key} from cache.")
            return cached_data

        # Nếu không có file cache hợp lệ, lấy dữ liệu mới từ endpoint
        endpoint_url = "https://cafef1.mediacdn.vn/Search/company.json"
        response = requests.get(endpoint_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from {endpoint_url}")

        # Parse dữ liệu từ response
        response_data = response.json()

        # 3. Lưu vào cache cho lần sau
        self.cache.set(cache_key, response_data)
        print(f"Fetched new data and saved to cache: {cache_key}")

        return response_data


    def _get_company_url(self, ticker: str):
        companies = self.get_all_companies()
        for company in companies:
            if company['Symbol'] == ticker:
                return f"{self.BASE_URL}{company['RedirectUrl']}"
        return None

    def _get_page_content(self, page: Page):
        # Lấy content từ page
        page_text = page.content()
        soup = BeautifulSoup(page_text, 'html.parser')
        
        # Thử tìm các vùng chứa nội dung chính (thứ tự ưu tiên từ hẹp đến rộng)
        # CafeF thường dùng 'content' hoặc 'left_col' cho phần thông tin doanh nghiệp
        main_content = soup.find('div', class_='content') or \
                    soup.find('div', id='content') or \
                    soup.find('div', class_='pagewrap') or \
                    soup.find('div', id='pagewrap')
        
        if main_content:
            return main_content.get_text(separator=' ', strip=True)
            
        return soup.get_text(separator=' ', strip=True)

    def _get_selector_content(self, page: Page, selector: str):
        try:
            element = page.query_selector(selector)
            if element:
                html_content = element.inner_html()
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logger.warning(f"Error while fetching content for selector {selector}: {e}")
        return ""

    def _get_table_by_selector(self, page: Page, selector: str):
        try:
            element = page.query_selector(selector)
            if element:
                html_content = element.inner_html()
                soup = BeautifulSoup(html_content, 'html.parser')
                rows = soup.find_all('tr')
                table_text = []
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    cols_text = [col.get_text(strip=True) for col in cols]
                    table_text.append(','.join(cols_text))
                return '\n'.join(table_text)
        except Exception as e:
            logger.warning(f"Error while fetching table for selector {selector}: {e}")
        return ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=1, max=3),
    )
    def get_company_profile(self, symbol: str):
        company_url = self._get_company_url(symbol)
        if not company_url:
            raise Exception(f"Company with symbol {symbol} not found on Cafef")

        profile_data = []
        page = PlaywrightManager.get_page()
        try:
            page.goto(company_url, timeout=15000)
            profile_data.append(self._get_page_content(page))
            page_text = page.content()
            soup = BeautifulSoup(page_text, 'html.parser')

            # Lấy thêm thông tin từ tab "Thông tin cơ bản" từ thẻ a có chứa text tương ứng
            basic_info_tab = soup.find('a', string=re.compile('Thông tin cơ bản'))
            if basic_info_tab and 'href' in basic_info_tab.attrs:
                basic_info_url = f"{self.BASE_URL}{basic_info_tab['href']}"
                page.goto(basic_info_url, timeout=15000)
                profile_data.append(self._get_page_content(page))
            
            # Lấy thêm thông tin từ tab "Ban lãnh đạo & Sở hữu" từ thẻ a có text tương ứng
            leadership_tab = soup.find('a', string=re.compile('Ban lãnh đạo & Sở hữu'))
            if leadership_tab and 'href' in leadership_tab.attrs:
                leadership_url = f"{self.BASE_URL}{leadership_tab['href']}"
                page.goto(leadership_url, timeout=15000)
                profile_data.append(self._get_page_content(page))
            
            # Lấy thêm thông tin từ tab "Danh sách cổ đông" từ thẻ h2 có text tương ứng
            # Định nghĩa bộ lọc
            h2_locators = page.locator("h2.owner-tab")

            # Lặp qua số lượng phần tử
            for i in range(h2_locators.count()):
                current_h2 = h2_locators.nth(i)
                text = current_h2.inner_text()
                if any(keyword in text for keyword in ["Danh sách cổ đông", "Đang sở hữu", "GD CĐ nội bộ & CĐ lớn"]):
                    current_h2.click()
                    page.wait_for_timeout(1000)
                    profile_data.append(self._get_page_content(page))

                    # Trong trường hợp, tồn tại thẻ a có class là `info-menu-item` và text chứa `Khối ngoại`, lấy href rồi truy cập
                    foreign_investors_tab = page.locator("a.info-menu-item", has_text=re.compile('Khối ngoại'))
                    if foreign_investors_tab.count() > 0:
                        foreign_investors_tab.click()
                        page.wait_for_timeout(1000)
                        profile_data.append(self._get_page_content(page))

            # Back về trang công ty chính
            page.goto(company_url, timeout=15000)
            # Lấy thêm thông tin từ tab "Tài nguyên - Nguồn vốn" từ thẻ h2 có text tương ứng
            resource_tab = page.locator("h2", has_text=re.compile('Tài nguyên - Nguồn vốn'))
            if resource_tab:
                resource_tab.click()
                page.wait_for_timeout(1000)
                profile_data.append(self._get_page_content(page))

            # Lấy thêm thông tin từ tab "Chỉ số tài chính" từ thẻ h2 có text tương ứng
            financial_tab = page.locator("h2", has_text=re.compile('Chỉ số tài chính'))
            if financial_tab:
                financial_tab.click()
                page.wait_for_timeout(1000)
                profile_data.append(self._get_page_content(page))

            # Lấy thêm thông tin từ tab "Công ty con & liên kết" từ thẻ h2 có text tương ứng
            subsidiaries_tab = page.locator("h2", has_text=re.compile('Công ty con & liên kết'))
            if subsidiaries_tab:
                subsidiaries_tab.click()
                page.wait_for_timeout(1000)
                profile_data.append(self._get_page_content(page))

        except Exception as e:
            logger.warning(f"Error while fetching profile for {symbol} from Cafef: {e}")
        finally:
            page.context.close()
        return " ".join(profile_data)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=1, max=3),
    )
    def get_macro_data(self):
        endpoint_url = f"{self.BASE_URL}/du-lieu.chn"
        page = PlaywrightManager.get_page()
        page.goto(endpoint_url, timeout=15000)
        try:
            # find the h3 tag with text contains `Hàng hóa`, `Tỷ giá`, `Tiền mã hóa`
            h3_locators = page.locator("h3")
            macro_data = {}
            for i in range(h3_locators.count()):
                current_h3 = h3_locators.nth(i)
                text = current_h3.inner_text()
                if "Hàng hóa" in text:
                    current_h3.click()
                    page.wait_for_timeout(1000)
                    commodity_text = self._get_table_by_selector(page, "table#dataBusiness")
                    macro_data['commodity'] = commodity_text
                elif "Tỷ giá" in text:
                    current_h3.click()
                    page.wait_for_timeout(1000)
                    exchange_rate_text = self._get_table_by_selector(page, "table#dataBusiness")
                    macro_data['exchange_rate'] = exchange_rate_text
                elif "Tiền mã hóa" in text:
                    current_h3.click()
                    page.wait_for_timeout(1000)
                    cryptocurrency_text = self._get_table_by_selector(page, "table#dataBusiness")
                    macro_data['cryptocurrency'] = cryptocurrency_text
        except Exception as e:
            logger.warning(f"Error while fetching macro data from Cafef: {e}")
        finally:
            page.context.close()

        return macro_data
