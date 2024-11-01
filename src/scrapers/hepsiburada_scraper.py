from scrapers.base_scraper import BaseScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Tuple
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class HepsiburadaScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "hepsiburada.com" in url

    def get_site_name(self) -> str:
        return "Hepsiburada"

    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        driver = None
        try:
            driver = self._get_chrome_driver()
            driver.get(url)
            
            wait = WebDriverWait(driver, 10)
            
            # Önce sepetteki fiyatı kontrol et
            try:
                checkout_price_element = wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "div[data-test-id='checkout-price'] span.eWD5fCQxbBy4Pnsc5a_I"
                    ))
                )
                price_text = checkout_price_element.text.strip()
            except:
                # Sepette fiyat yoksa normal fiyatı al
                price_element = wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "div[data-test-id='price-current-price']"
                    ))
                )
                price_text = price_element.text.strip()
            
            # Fiyat temizleme
            price_text = price_text.replace('TL', '').strip()
            price_text = ''.join(filter(lambda x: x.isdigit() or x == ',', price_text))
            price_text = price_text.replace(',', '.')
            
            price = float(price_text)
            product_id = url.split('/')[-1].split('-')[-1].split('?')[0]
            return price, product_id
                
        except Exception as e:
            logging.error(f"Hepsiburada price extraction error for URL {url}: {str(e)}")
            return None, url
        finally:
            if driver:
                driver.quit()

    def _get_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Tarayıcıyı görünmez modda çalıştır
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)