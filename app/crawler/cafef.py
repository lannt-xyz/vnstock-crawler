import re

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from tenacity import retry, stop_after_attempt, wait_random

from app.logger import logger
from app.utils.caching_util import CachingUtil
from app.utils.decorators import cached_data, log_execution_time
from app.utils.playwright_manager import PlaywrightManager


class CafefCrawler:
    BASE_URL = "https://cafef.vn"

    def __init__(self):
        self.cache = CachingUtil()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=1, max=3),
    )
    @cached_data(cache_key_prefix="cafef_companies", extension="json")
    def get_all_companies(self):
        # Nếu không có file cache hợp lệ, lấy dữ liệu mới từ endpoint
        endpoint_url = "https://cafef1.mediacdn.vn/Search/company.json"
        response = requests.get(endpoint_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from {endpoint_url}")

        # Parse dữ liệu từ response
        return response.json()

    def _get_company_url(self, ticker: str):
        companies = self.get_all_companies()
        for company in companies:
            if company["Symbol"] == ticker:
                return f"{self.BASE_URL}{company['RedirectUrl']}"
        return None

    def _get_page_content(self, page: Page):
        # Lấy content từ page
        page_text = page.content()
        soup = BeautifulSoup(page_text, "html.parser")

        # Thử tìm các vùng chứa nội dung chính (thứ tự ưu tiên từ hẹp đến rộng)
        # CafeF thường dùng 'content' hoặc 'left_col' cho phần thông tin doanh nghiệp
        main_content = (
            soup.find("div", class_="content")
            or soup.find("div", id="content")
            or soup.find("div", class_="pagewrap")
            or soup.find("div", id="pagewrap")
            or soup.find("div", id="cf_ContainerBox")
        )

        if main_content:
            return main_content.get_text(separator=" ", strip=True)

        return soup.get_text(separator=" ", strip=True)

    def _get_selector_content(self, page: Page, selector: str):
        try:
            element = page.query_selector(selector)
            if element:
                html_content = element.inner_html()
                soup = BeautifulSoup(html_content, "html.parser")
                return soup.get_text(separator=" ", strip=True)
        except Exception as e:
            logger.warning(f"Error while fetching content for selector {selector}: {e}")
        return ""

    def _get_table_by_selector(self, page: Page, selector: str):
        try:
            element = page.query_selector(selector)
            if element:
                html_content = element.inner_html()
                soup = BeautifulSoup(html_content, "html.parser")
                rows = soup.find_all("tr")
                table_text = []
                for row in rows:
                    cols = row.find_all(["td", "th"])
                    cols_text = [col.get_text(strip=True) for col in cols]
                    table_text.append(",".join(cols_text))
                return "\n".join(table_text)
        except Exception as e:
            logger.warning(f"Error while fetching table for selector {selector}: {e}")
        return ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=1, max=3),
    )
    @log_execution_time
    def get_company_profile(self, symbol: str):
        company_url = self._get_company_url(symbol)
        if not company_url:
            raise Exception(f"Company with symbol {symbol} not found on Cafef")

        profile_data = []
        page = PlaywrightManager.get_page()
        try:
            page.goto(company_url, timeout=15000)
            page_text = page.content()
            soup = BeautifulSoup(page_text, "html.parser")

            # Tổng quan
            profile_data.append(
                "[Tên công ty, Mã chứng khoán, Lĩnh vực hoạt động, Mô tả hoạt động kinh doanh, Thông tin liên hệ, Các thông tin cơ bản liên quan đến transaction (Giá tham chiếu ~ KLCP lưu hành), ...]"
            )
            profile_data.append(self._get_page_content(page))

            # Lấy thêm thông tin từ tab "Thông tin cơ bản" từ thẻ a có chứa text tương ứng
            basic_info_tab = soup.find("a", string=re.compile("Thông tin cơ bản"))
            if basic_info_tab and "href" in basic_info_tab.attrs:
                basic_info_url = f"{self.BASE_URL}{basic_info_tab['href']}"
                page.goto(basic_info_url, timeout=15000)
                profile_data.append(
                    "[Thông tin cơ bản, lịch sử hình thành, ngành nghề kinh doanh ...]"
                )
                profile_data.append(self._get_page_content(page))

            # Lấy thêm thông tin từ tab "Ban lãnh đạo & Sở hữu" từ thẻ a có text tương ứng
            leadership_tab = soup.find("a", string=re.compile("Ban lãnh đạo & Sở hữu"))
            if leadership_tab and "href" in leadership_tab.attrs:
                leadership_url = f"{self.BASE_URL}{leadership_tab['href']}"
                page.goto(leadership_url, timeout=15000)
                profile_data.append("[Ban lãnh đạo & Sở hữu]")
                profile_data.append(self._get_page_content(page))

            # Lấy thêm thông tin từ tab "Danh sách cổ đông" từ thẻ h2 có text tương ứng
            # Định nghĩa bộ lọc
            h2_locators = page.locator("h2.owner-tab")

            # Lặp qua số lượng phần tử
            for i in range(h2_locators.count()):
                current_h2 = h2_locators.nth(i)
                text = current_h2.inner_text()
                if any(
                    keyword in text
                    for keyword in [
                        "Danh sách cổ đông",
                        "Đang sở hữu",
                        "GD CĐ nội bộ & CĐ lớn",
                    ]
                ):
                    current_h2.click()
                    page.wait_for_timeout(1000)
                    profile_data.append(f"[{text.strip()}]")
                    profile_data.append(self._get_page_content(page))

                    # Trong trường hợp, tồn tại thẻ a có class là `info-menu-item` và text chứa `Khối ngoại`, lấy href rồi truy cập
                    foreign_investors_tab = page.locator(
                        "a.info-menu-item", has_text=re.compile("Khối ngoại")
                    )
                    if foreign_investors_tab.count() > 0:
                        foreign_investors_tab.click()
                        page.wait_for_timeout(1000)
                        profile_data.append("[Khối ngoại]")
                        profile_data.append(self._get_page_content(page))

            # Back về trang công ty chính
            page.goto(company_url, timeout=15000)
            # Lấy kết quả kinh doanh
            page.wait_for_timeout(1000)

            # Lấy thêm thông tin từ tab "Kết quả kinh doanh" từ thẻ h2 có text tương ứng
            business_tab = page.locator("h2", has_text=re.compile("Kết quả kinh doanh"))
            if business_tab:
                business_tab.click()
                page.wait_for_timeout(1000)
                profile_data.append("[Kết quả kinh doanh]")
                profile_data.append(self._get_page_content(page))

                # Nếu tồn tại thẻ a có href chứa `incsta`, text chứa `Chi tiết` hoặc `Xem tất cả`
                detailed_business_tab = page.locator(
                    "a", has_text=re.compile(r"Chi tiết|Xem tất cả")
                )
                for i in range(detailed_business_tab.count()):
                    current_a = detailed_business_tab.nth(i)
                    href = current_a.get_attribute("href") or ""
                    if "incsta" in href:
                        current_a.click()
                        page.wait_for_timeout(1000)
                        profile_data.append("[Kết quả kinh doanh chi tiết]")
                        profile_data.append(self._get_page_content(page))

                        # Back về trang công ty chính
                        page.goto(company_url, timeout=15000)
                        # Lấy kết quả kinh doanh
                        page.wait_for_timeout(1000)
                        break

            # Lấy thêm thông tin từ tab "Tài nguyên - Nguồn vốn" từ thẻ h2 có text tương ứng
            resource_tab = page.locator(
                "h2", has_text=re.compile("Tài nguyên - Nguồn vốn")
            )
            if resource_tab:
                resource_tab.click()
                page.wait_for_timeout(1000)
                profile_data.append("[Tài nguyên - Nguồn vốn]")
                profile_data.append(self._get_page_content(page))

                # Nếu tồn tại thẻ a có href chứa `bsheet`
                detailed_resource_tab = page.locator(
                    "a", has_text=re.compile(r"Chi tiết|Xem tất cả")
                )
                for i in range(detailed_resource_tab.count()):
                    current_a = detailed_resource_tab.nth(i)
                    href = current_a.get_attribute("href") or ""
                    if "bsheet" in href:
                        current_a.click()
                        page.wait_for_timeout(1000)
                        profile_data.append("[Tài nguyên - Nguồn vốn chi tiết]")
                        profile_data.append(self._get_page_content(page))

                        # Back về trang công ty chính
                        page.goto(company_url, timeout=15000)
                        # Lấy kết quả kinh doanh
                        page.wait_for_timeout(1000)
                        break

            # Lấy thêm thông tin từ tab "Chỉ số tài chính" từ thẻ h2 có text tương ứng
            financial_tab = page.locator("h2", has_text=re.compile("Chỉ số tài chính"))
            if financial_tab:
                financial_tab.click()
                page.wait_for_timeout(1000)
                profile_data.append("[Chỉ số tài chính]")
                profile_data.append(self._get_page_content(page))

            # Lấy thêm thông tin từ tab "Công ty con & liên kết" từ thẻ h2 có text tương ứng
            subsidiaries_tab = page.locator(
                "h2", has_text=re.compile("Công ty con & liên kết")
            )
            if subsidiaries_tab:
                subsidiaries_tab.click()
                page.wait_for_timeout(1000)
                profile_data.append("[Công ty con & liên kết]")
                profile_data.append(self._get_page_content(page))

        except Exception as e:
            logger.warning(f"Error while fetching profile for {symbol} from Cafef: {e}")
        finally:
            page.context.close()

        return "\n".join(profile_data)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=1, max=3),
    )
    @log_execution_time
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
                    commodity_text = self._get_table_by_selector(
                        page, "table#dataBusiness"
                    )
                    macro_data["commodity"] = commodity_text
                elif "Tỷ giá" in text:
                    current_h3.click()
                    page.wait_for_timeout(1000)
                    exchange_rate_text = self._get_table_by_selector(
                        page, "table#dataBusiness"
                    )
                    macro_data["exchange_rate"] = exchange_rate_text
                elif "Tiền mã hóa" in text:
                    current_h3.click()
                    page.wait_for_timeout(1000)
                    cryptocurrency_text = self._get_table_by_selector(
                        page, "table#dataBusiness"
                    )
                    macro_data["cryptocurrency"] = cryptocurrency_text
        except Exception as e:
            logger.warning(f"Error while fetching macro data from Cafef: {e}")
        finally:
            page.context.close()

        return macro_data
