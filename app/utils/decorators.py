
import functools
import logging

from app.utils.cache_service import CacheService
from app.logger import logger

def try_catch_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return None
    return wrapper


logger = logging.getLogger(__name__)
cache_service = CacheService()

def cached_data(cache_key_prefix: str, expiry_days: int = None):
    """
    Decorator để tự động hóa việc get/set cache cho các hàm fetch dữ liệu.
    :param cache_key_prefix: Tiền tố cho key cache (ví dụ: 'company_list')
    :param expiry_days: Số ngày hết hạn (ghi đè config mặc định nếu cần)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Tạo cache key dựa trên prefix và các đối số truyền vào hàm (nếu có)
            # Ví dụ: nếu gọi get_profile("VNM"), key sẽ là "profile_VNM"
            suffix = "_".join([str(arg) for arg in args[1:]]) # Bỏ 'self' (args[0])
            cache_key = f"{cache_key_prefix}_{suffix}" if suffix else cache_key_prefix
            
            # 1. Thử lấy từ cache
            service = CacheService(expiry_days=expiry_days) if expiry_days else cache_service
            data = service.get(cache_key)
            
            if data is not None:
                logger.info(f"Cache hit: {cache_key}")
                return data
            
            # 2. Nếu không có cache, thực thi hàm gốc
            logger.info(f"Cache miss: {cache_key}. Fetching new data...")
            result = func(*args, **kwargs)
            
            # 3. Lưu kết quả vào cache nếu fetch thành công
            if result:
                service.set(cache_key, result)
                
            return result
        return wrapper
    return decorator