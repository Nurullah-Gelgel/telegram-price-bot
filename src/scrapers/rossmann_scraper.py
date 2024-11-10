from scrapers.base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Tuple
import logging
from config import SITE_TIMEOUTS

class RossmannScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "rossmann.com.tr" in url

    def get_site_name(self) -> str:
        return "Rossmann"

    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        driver = None
        try:
            driver = self._get_chrome_driver()
            driver.get(url)
            
            wait = WebDriverWait(driver, self._get_timeout(url))
            
            try:
                # Tüm fiyat alanını bul
                price_area = wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "div.price-area.desktopPrice"
                    ))
                )
                
                # Önce Rossmann Card fiyatını kontrol et
                try:
                    card_price = price_area.find_element(
                        By.CSS_SELECTOR, 
                        "div.special-price div.price-area"
                    )
                    if card_price and card_price.text and "TL" in card_price.text:
                        price_text = card_price.text.strip()
                        logging.info(f"Rossmann Card fiyatı bulundu: {price_text}")
                    else:
                        raise Exception("Rossmann Card fiyatı bulunamadı")
                except:
                    # Rossmann Card fiyatı yoksa normal fiyatı al
                    normal_price = price_area.find_element(
                        By.CSS_SELECTOR, 
                        "div.final-price"
                    )
                    if normal_price and normal_price.text:
                        price_text = normal_price.text.strip()
                        logging.info(f"Normal fiyat bulundu: {price_text}")
                    else:
                        raise Exception("Normal fiyat bulunamadı")
                
                # Fiyat metnini temizle
                if not price_text:
                    return None, url
                    
                # TL ve boşlukları kaldır, sadece sayıları ve virgülü al
                price_text = ''.join(filter(lambda x: x.isdigit() or x == ',', price_text))
                if not price_text:
                    return None, url
                    
                # Virgülü noktaya çevir
                price_text = price_text.replace(',', '.')
                
                try:
                    price = float(price_text)
                    if price <= 0:
                        logging.error(f"Geçersiz fiyat değeri: {price}")
                        return None, url
                    logging.info(f"Fiyat başarıyla çekildi: {price}")
                except ValueError:
                    logging.error(f"Geçersiz fiyat formatı: {price_text}")
                    return None, url
                
                # Ürün ID'sini URL'den çıkar
                try:
                    product_id = url.split('/')[-1].split('-')[-1].split('.')[0]
                except IndexError:
                    product_id = url
                    
                return price, product_id
                    
            except Exception as e:
                logging.error(f"Fiyat elementi bulunamadı: {str(e)}")
                return None, url
                
        except Exception as e:
            logging.error(f"Rossmann price extraction error for URL {url}: {str(e)}")
            return None, url
        finally:
            if driver:
                driver.quit()