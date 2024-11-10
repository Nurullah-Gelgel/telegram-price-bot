from scrapers.base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Tuple
import logging
from config import SITE_TIMEOUTS

class HepsiburadaScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "hepsiburada.com" in url

    def get_site_name(self) -> str:
        return "Hepsiburada"

    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        driver = None
        try:
            driver = self._get_chrome_driver()
            if not driver:
                logging.error("Failed to initialize Chrome driver")
                return None, url
            
            driver.get(url)
            
            wait = WebDriverWait(driver, self._get_timeout(url))
            
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
            return None, url.split('/')[-1] if '/' in url else url
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass