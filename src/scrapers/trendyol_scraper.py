from scrapers.base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
import logging

class TrendyolScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "trendyol.com" in url

    def get_site_name(self) -> str:
        return "Trendyol"

    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        session = self._create_session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = session.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            price_element = soup.find('span', {'class': 'prc-dsc'})
            if not price_element:
                return None, url
                
            price_text = price_element.text.strip()
            price_text = price_text.replace('TL', '').replace('.', '').replace(',', '.').strip()
            
            price = float(price_text)
            product_id = url.split('-p-')[1].split('?')[0]
            return price, product_id
                
        except Exception as e:
            logging.error(f"Trendyol price extraction error: {str(e)}")
            return None, url

    def _create_session(self):
        return requests.Session()