import pkgutil
import importlib
import inspect
from app.database import Base # Hoặc nơi bạn định nghĩa Base

# Lấy đường dẫn của thư mục hiện tại (app/models)
__all__ = []

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    # Import module động
    full_module_name = f"{__name__}.{module_name}"
    module = importlib.import_module(full_module_name)
    
    # Duyệt qua các thành viên trong module
    for name, obj in inspect.getmembers(module):
        # Kiểm tra nếu là class và kế thừa từ Base
        if inspect.isclass(obj) and issubclass(obj, Base) and obj is not Base:
            # Export class này ra namespace của package models
            globals()[name] = obj
            if name not in __all__:
                __all__.append(name)
