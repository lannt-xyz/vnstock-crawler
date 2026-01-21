import requests
import feedparser
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class RSSParser:
    """Parse RSS feeds to get article metadata"""

    def __init__(self, rss_url: str):
        self.rss_url = rss_url

    def fetch(self, limit: Optional[int] = None) -> List[Dict]:
        """Fetch RSS items"""
        try:
            feed = feedparser.parse(self.rss_url)
            items = []

            for entry in feed.entries[:limit] if limit else feed.entries:
                item = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'published_at': entry.get('published_parsed'),
                    'description': entry.get('description', '')
                }
                items.append(item)

            return items
        except Exception as e:
            logger.error(f"Error parsing RSS {self.rss_url}: {e}")
            return []

class SitemapParser:
    """Parse XML sitemaps to get URLs"""

    def __init__(self, sitemap_url: str):
        self.sitemap_url = sitemap_url

    def fetch(self, limit: Optional[int] = None) -> List[Dict]:
        """Fetch sitemap URLs"""
        try:
            response = requests.get(self.sitemap_url, timeout=30)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            urls = []

            # Handle standard sitemap format
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')[:limit] if limit else root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')

                if loc is not None:
                    item = {
                        'url': loc.text,
                        'lastmod': lastmod.text if lastmod is not None else None
                    }
                    urls.append(item)

            return urls
        except Exception as e:
            logger.error(f"Error parsing sitemap {self.sitemap_url}: {e}")
            return []

class ArticleExtractor:
    """Extract article details from HTML using CSS selectors"""

    def __init__(self, config: Dict):
        self.config = config

    def extract(self, url: str) -> Optional[Dict]:
        """Extract article details from URL"""
        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract using selectors
            title = self._extract_text(soup, self.config.get('title_selector'))
            content = self._extract_content(soup, self.config.get('content_selector'))
            short_desc = self._extract_text(soup, self.config.get('short_desc_selector'))
            publish_time = self._extract_text(soup, self.config.get('publish_time_selector'))
            author = self._extract_text(soup, self.config.get('author_selector'))

            if title and content:
                return {
                    'title': title,
                    'short_description': short_desc,
                    'content': content,
                    'markdown_content': content,  # Keep as HTML for now
                    'publish_time': publish_time,
                    'author': author,
                    'url': url
                }
            return None

        except Exception as e:
            logger.error(f"Error extracting article {url}: {e}")
            return None

    def _extract_text(self, soup: BeautifulSoup, selector: Optional[Dict]) -> Optional[str]:
        """Extract text using CSS selector"""
        if not selector:
            return None

        try:
            if 'class' in selector:
                element = soup.find(selector.get('tag', 'div'), class_=selector['class'])
            elif 'id' in selector:
                element = soup.find(selector.get('tag', 'div'), id=selector['id'])
            else:
                element = soup.find(selector.get('tag', 'div'))

            return element.get_text(strip=True) if element else None
        except:
            return None

    def _extract_content(self, soup: BeautifulSoup, selector: Optional[Dict]) -> Optional[str]:
        """Extract content, may need special handling"""
        if not selector:
            return None

        try:
            if 'class' in selector:
                element = soup.find(selector.get('tag', 'div'), class_=selector['class'])
            elif 'id' in selector:
                element = soup.find(selector.get('tag', 'div'), id=selector['id'])
            else:
                element = soup.find(selector.get('tag', 'div'))

            if element:
                # Remove unwanted elements
                for unwanted in element.find_all(['script', 'style', 'advertisement']):
                    unwanted.decompose()

                return element.get_text(separator='\n', strip=True)
            return None
        except:
            return None

class NewsCrawler:
    """Main crawler class combining RSS/Sitemap and article extraction"""

    # Pre-configured sites (similar to vnstock_news)
    SITE_CONFIGS = {
        'cafef': {
            'rss_url': 'https://cafebiz.vn/rss/home.rss',
            'sitemap_url': 'https://cafef.vn/sitemap.xml',
            'selectors': {
                'title_selector': {'tag': 'h1', 'class': 'title'},
                'content_selector': {'tag': 'div', 'class': 'content'},
                'short_desc_selector': {'tag': 'div', 'class': 'sapo'},
                'publish_time_selector': {'tag': 'time', 'class': 'time'},
                'author_selector': {'tag': 'span', 'class': 'author'}
            }
        },
        'vnexpress': {
            'rss_url': 'https://vnexpress.net/rss/tin-moi-nhat.rss',
            'sitemap_url': 'https://vnexpress.net/sitemap.xml',
            'selectors': {
                'title_selector': {'tag': 'h1', 'class': 'title-detail'},
                'content_selector': {'tag': 'article', 'class': 'content_detail'},
                'short_desc_selector': {'tag': 'p', 'class': 'description'},
                'publish_time_selector': {'tag': 'span', 'class': 'date'},
                'author_selector': {'tag': 'p', 'class': 'author'}
            }
        }
    }

    def __init__(self, site_name: Optional[str] = None, custom_config: Optional[Dict] = None, debug: bool = False):
        if custom_config:
            self.config = custom_config
        elif site_name and site_name in self.SITE_CONFIGS:
            self.config = self.SITE_CONFIGS[site_name]
        else:
            raise ValueError(f"Unsupported site: {site_name}")

        self.debug = debug
        self.extractor = ArticleExtractor(self.config['selectors'])

    def get_articles(self, limit: int = 10, sitemap_url: Optional[str] = None, rss_url: Optional[str] = None) -> List[Dict]:
        """Get article metadata from RSS or Sitemap"""
        articles = []

        # Try RSS first
        rss_url = rss_url or self.config.get('rss_url')
        if rss_url:
            rss_parser = RSSParser(rss_url)
            articles = rss_parser.fetch(limit)
            if articles:
                if self.debug:
                    logger.info(f"Fetched {len(articles)} articles from RSS")
                return articles

        # Fallback to sitemap
        sitemap_url = sitemap_url or self.config.get('sitemap_url')
        if sitemap_url:
            sitemap_parser = SitemapParser(sitemap_url)
            sitemap_data = sitemap_parser.fetch(limit)
            articles = [{'url': item['url'], 'title': '', 'published_at': item['lastmod']} for item in sitemap_data]
            if self.debug:
                logger.info(f"Fetched {len(articles)} articles from sitemap")

        return articles

    def get_article_details(self, url: str) -> Optional[Dict]:
        """Get detailed article content"""
        return self.extractor.extract(url)

class BatchNewsCrawler:
    """Batch crawler for multiple URLs"""

    def __init__(self, site_name: Optional[str] = None, custom_config: Optional[Dict] = None, request_delay: float = 1.0):
        self.crawler = NewsCrawler(site_name, custom_config)
        self.request_delay = request_delay

    def fetch_details_for_urls(self, urls: List[str]) -> List[Dict]:
        """Fetch details for multiple URLs with delay"""
        results = []

        for i, url in enumerate(urls):
            if self.request_delay > 0 and i > 0:
                time.sleep(self.request_delay)

            details = self.crawler.get_article_details(url)
            if details:
                results.append(details)

        return results