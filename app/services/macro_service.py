from sqlalchemy.orm import Session

from app.crawler.cafef import CafefCrawler
from app.models.macro import MacroData
from app.utils.decorators import cached_data, try_catch_decorator
from app.utils.gemini_api import extract_data

class MacroService:
    def __init__(self, db: Session):
        self.db = db
        self.cafef_crawler = CafefCrawler()

    @try_catch_decorator
    def fetch_and_save_macro_data(self):
        macro_data = self._fetch_macro_data()
        # first delete existing
        self.db.query(MacroData).delete()
        self.db.flush()

        for item in macro_data:
            macro = MacroData(
                **item
            )
            self.db.add(macro)
        self.db.commit()

    @cached_data(cache_key_prefix="macro_data", extension="json")
    @try_catch_decorator
    def _fetch_macro_data(self):
        macro_data = self.cafef_crawler.get_macro_data()
        prompt = f"""
Bạn là một chuyên gia trích xuất dữ liệu (Data Extraction Specialist). Nhiệm vụ của bạn là đọc một văn bản thô, lộn xộn được crawl từ web và chuyển đổi nó thành cấu trúc JSON chính xác theo các bảng cơ sở dữ liệu sau.
Các Models đích:
    MacroData: indicator, price, changed_percent

Quy tắc trích xuất:
    Lọc nhiễu: Loại bỏ quảng cáo, các câu văn không liên quan, hoặc các ký tự đặc biệt do lỗi crawl.
    Đồng nhất hóa: Đảm bảo symbol (Mã chứng khoán) nhất quán trên tất cả các bảng.
    Định dạng số: ownership_percent và shares_owned phải là kiểu Float (số thực).
    Trường JSON: Đối với cột data trong Financials và Ratios, hãy nhóm tất cả các chỉ số tài chính tìm thấy vào một object JSON duy nhất.
    Dữ liệu trống: Nếu không tìm thấy thông tin cho một trường, hãy để null.

Định dạng đầu ra mong muốn (JSON duy nhất):
[
    {{
        "indicator": "...",
        "price": ...,
        "changed_percent": "..."
    }},
    ...
]

Dữ liệu thô cần trích xuất:

{macro_data}
"""
        return extract_data(prompt)
