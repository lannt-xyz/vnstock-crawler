import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    from app.database import get_db
    db = next(get_db())

    # from app.services.company_info_service import CompanyInfoService
    # service = CompanyInfoService(db)
    # profiles = service.fetch_and_save_company_profiles('FOX')
    # print(profiles)

    # from app.services.macro_service import MacroService
    # macro_service = MacroService(db)
    
    from app.crawler.cafef import CafefCrawler
    crawler = CafefCrawler()
    data = crawler.get_macro_data()
    print(data)
    
