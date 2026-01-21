from sqlalchemy.orm import Session
from app.models.news import CompanyNews, MacroNews
from app.news_crawler import NewsCrawler, BatchNewsCrawler
from app.logger import logger

class NewsService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_save_company_news(self, symbol: str):
        try:
            # Use cafef crawler for company news (can be customized per symbol)
            crawler = NewsCrawler(site_name='cafef')
            articles = crawler.get_articles(limit=5)  # Get recent articles

            batch_crawler = BatchNewsCrawler(site_name='cafef', request_delay=1.0)

            # Filter articles that might be related to the symbol (basic filtering)
            relevant_urls = [article['url'] for article in articles if symbol.lower() in article.get('title', '').lower()]

            if relevant_urls:
                detailed_articles = batch_crawler.fetch_details_for_urls(relevant_urls[:3])  # Limit to 3

                for article in detailed_articles:
                    news = CompanyNews(
                        symbol=symbol,
                        title=article.get('title', '')[:255],
                        content=article.get('content'),
                        url=article.get('url'),
                        published_at=article.get('publish_time')
                    )
                    self.db.add(news)
                self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching company news for {symbol}: {e}")
            self.db.rollback()

    def fetch_and_save_macro_news(self):
        try:
            # Use vnexpress for macro news
            crawler = NewsCrawler(site_name='vnexpress')
            articles = crawler.get_articles(limit=10)

            batch_crawler = BatchNewsCrawler(site_name='vnexpress', request_delay=1.0)
            urls = [article['url'] for article in articles[:5]]  # Get first 5

            detailed_articles = batch_crawler.fetch_details_for_urls(urls)

            for article in detailed_articles:
                news = MacroNews(
                    title=article.get('title', '')[:255],
                    content=article.get('content'),
                    url=article.get('url'),
                    published_at=article.get('publish_time')
                )
                self.db.add(news)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error fetching macro news: {e}")
            self.db.rollback()