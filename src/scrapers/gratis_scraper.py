from scrapers.base_scraper import BaseScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Tuple
import logging
from config import SITE_TIMEOUTS, SELENIUM_CONFIG

class GratisScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "gratis.com" in url

    def get_site_name(self) -> str:
        return "Gratis"

    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        driver = None
        try:
            driver = self._get_chrome_driver()
            driver.get(url)
            
            wait = WebDriverWait(driver, self._get_timeout(url))
            
            # Önce Gratis Kart fiyatını kontrol et
            try:
                gratis_card_price = wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "div.via-card .card-price"
                    ))
                )
                price_text = gratis_card_price.text.strip()
            except:
                # Gratis Kart fiyatı yoksa normal fiyatı al
                price_element = wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "span.price-content span.discounted"
                    ))
                )
                price_text = price_element.text.strip()
            
            # Fiyat metnini temizle
            price_text = ''.join(filter(lambda x: x.isdigit() or x == ',', price_text))
            price_text = price_text.replace(',', '.')
            price = float(price_text)
            
            # Ürün ID'sini URL'den çıkar
            try:
                product_id = url.split('-')[-1].split('?')[0]
            except IndexError:
                product_id = url
                
            return price, product_id
                
        except Exception as e:
            logging.error(f"Gratis price extraction error for URL {url}: {str(e)}")
            return None, url
        finally:
            if driver:
                driver.quit()

    def _get_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)