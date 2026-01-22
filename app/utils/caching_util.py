import glob
import json
import os
from datetime import datetime, timedelta

from app.config import config


class CachingUtil:
    def __init__(self, cache_dir=None, expiry_days=None):
        self.cache_dir = cache_dir or config.CACHE_DIR
        self.expiry_days = expiry_days or config.CACHE_EXPIRY_DAYS
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_file_path(self, key, extension, timestamp=None):
        ts = timestamp or datetime.now().strftime("%Y%m%d")
        return os.path.join(self.cache_dir, f"{key}_{ts}.{extension}")

    def get(self, key, extension="json"):
        """Lấy dữ liệu từ cache nếu còn hạn"""
        # Tìm tất cả các file có pattern: key_*.json
        search_pattern = os.path.join(self.cache_dir, f"{key}_*.{extension}")
        for file_path in glob.glob(search_pattern):
            filename = os.path.basename(file_path)
            # Trích xuất timestamp (giả định định dạng key_YYYYMMDD.json)
            date_str = filename.replace(f"{key}_", "").replace(f".{extension}", "")
            try:
                file_time = datetime.strptime(date_str, "%Y%m%d")
                if datetime.now() - file_time < timedelta(days=self.expiry_days):
                    with open(file_path, "r", encoding="utf-8") as f:
                        if extension == "json":
                            return json.load(f)
                        else:
                            return f.read()
                else:
                    # Xóa nếu hết hạn
                    os.remove(file_path)
            except ValueError:
                os.remove(file_path)
        return None

    def set(self, key, extension, data):
        """Lưu dữ liệu mới vào cache"""
        file_path = self._get_file_path(key, extension)
        with open(file_path, "w", encoding="utf-8") as f:
            if extension == "json":
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                f.write(data)
        return file_path
