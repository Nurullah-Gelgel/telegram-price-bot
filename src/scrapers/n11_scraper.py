from scrapers.base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Tuple
import logging
from config import SITE_TIMEOUTS

class N11Scraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "n11.com" in url

    def get_site_name(self) -> str:
        return "N11"

    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        driver = None
        try:
            driver = self._get_chrome_driver()
            driver.get(url)
            
            wait = WebDriverWait(driver, self._get_timeout(url))
            
            # Birden fazla fiyat seçiciyi dene
            selectors = [
                "div.newPrice ins[content]",
                "div.newPrice ins",
                "div.priceContainer div.newPrice ins"
            ]
            
            price_element = None
            for selector in selectors:
                try:
                    price_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if price_element:
                        break
                except:
                    continue
            
            if not price_element:
                raise Exception("Fiyat elementi bulunamadı")
            
            # Önce content attribute'u dene, yoksa text içeriğini al
            price_text = price_element.get_attribute('content')
            if not price_text:
                price_text = price_element.text.strip()
                price_text = price_text.replace('TL', '').replace('.', '').replace(',', '.').strip()
            
            price = float(price_text)
            
            # URL'den ürün ID'sini çıkar
            try:
                product_id = url.split('-p-')[1].split('?')[0]
            except IndexError:
                # URL'den ID çıkarılamazsa URL'i kendisini kullan
                product_id = url
                
            return price, product_id
                
        except Exception as e:
            logging.error(f"N11 price extraction error for URL {url}: {str(e)}")
            return None, url
        finally:
            if driver:
                driver.quit()