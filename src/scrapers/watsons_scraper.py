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

class WatsonsScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "watsons.com.tr" in url

    def get_site_name(self) -> str:
        return "Watsons"

    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        driver = None
        try:
            driver = self._get_chrome_driver()
            driver.get(url)
            
            wait = WebDriverWait(driver, 15)
            
            try:
                # Ana fiyat alanını bul
                price_wrapper = wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "div.price-badge__wrapper"
                    ))
                )
                
                price_text = None
                
                # Önce Watsons Club fiyatını kontrol et
                try:
                    # Watsons Club fiyat alanını bul
                    membership_wrapper = price_wrapper.find_element(
                        By.CSS_SELECTOR,
                        "div.price-badge__wrapper--membership"
                    )
                    
                    if membership_wrapper:
                        club_price = membership_wrapper.find_element(
                            By.CSS_SELECTOR,
                            "div.price-badge--membership e2-price-badge"
                        )
                        
                        if club_price:
                            decimal = club_price.find_element(
                                By.CSS_SELECTOR,
                                "span.formatted-price__decimal"
                            ).get_attribute('textContent').replace('<!---->','').strip()
                            
                            fractional = club_price.find_element(
                                By.CSS_SELECTOR,
                                "span.formatted-price__fractional"
                            ).get_attribute('textContent').replace('<!---->','').strip()
                            
                            if decimal and fractional:
                                price_text = f"{decimal}.{fractional}"
                                logging.info(f"Watsons Club fiyatı bulundu: {price_text}")
                except Exception as e:
                    logging.info(f"Watsons Club fiyatı bulunamadı: {str(e)}")
                
                # Eğer Watsons Club fiyatı bulunamadıysa normal fiyatı al
                if not price_text:
                    try:
                        normal_price = price_wrapper.find_element(
                            By.CSS_SELECTOR,
                            "e2-price-badge.price-badge__price"
                        )
                        
                        decimal = normal_price.find_element(
                            By.CSS_SELECTOR,
                            "span.formatted-price__decimal"
                        ).get_attribute('textContent').replace('<!---->','').strip()
                        
                        fractional = normal_price.find_element(
                            By.CSS_SELECTOR,
                            "span.formatted-price__fractional"
                        ).get_attribute('textContent').replace('<!---->','').strip()
                        
                        if decimal and fractional:
                            price_text = f"{decimal}.{fractional}"
                            logging.info(f"Normal fiyat bulundu: {price_text}")
                    except Exception as e:
                        logging.error(f"Normal fiyat alınamadı: {str(e)}")
                
                if not price_text:
                    logging.error("Hiçbir fiyat bulunamadı")
                    return None, url
                    
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
                    product_id = url.split('/p/')[1].split('?')[0]
                except IndexError:
                    product_id = url
                    
                return price, product_id
                
            except Exception as e:
                logging.error(f"Fiyat elementi bulunamadı: {str(e)}")
                return None, url
            
        except Exception as e:
            logging.error(f"Watsons price extraction error for URL {url}: {str(e)}")
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
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--enable-unsafe-swiftshader')  # WebGL hatasını çözmek için
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)