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
            
            # Sayfanın yüklenmesi için bekle
            wait = WebDriverWait(driver, self._get_timeout(url))
            
            # JavaScript'in çalışması için ekstra bekleme
            driver.execute_script("return document.readyState") == "complete"
            
            # Önce Watsons Club fiyatını kontrol et
            try:
                script = """
                    return document.querySelector('.price-badge--membership .formatted-price__decimal').textContent +
                           '.' +
                           document.querySelector('.price-badge--membership .formatted-price__fractional').textContent;
                """
                price_text = driver.execute_script(script)
                logging.info(f"Watsons Club fiyatı bulundu: {price_text}")
            except:
                # Normal fiyatı kontrol et
                try:
                    script = """
                        return document.querySelector('.price-badge__price .formatted-price__decimal').textContent +
                               '.' +
                               document.querySelector('.price-badge__price .formatted-price__fractional').textContent;
                    """
                    price_text = driver.execute_script(script)
                    logging.info(f"Normal fiyat bulundu: {price_text}")
                except:
                    logging.error("Fiyat elementi bulunamadı")
                    return None, url

            # HTML içindeki yorum işaretlerini ve boşlukları temizle
            price_text = price_text.replace('<!---->','').strip()
            
            try:
                price = float(price_text)
                if price <= 0:
                    return None, url
            except ValueError:
                return None, url
            
            # Ürün ID'sini URL'den çıkar
            product_id = url.split('/p/')[1].split('?')[0]
            return price, product_id
                
        except Exception as e:
            logging.error(f"Watsons price extraction error for URL {url}: {str(e)}")
            return None, url
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def _get_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')  # GPU hatalarını önlemek için
        chrome_options.add_argument('--window-size=1920,1080')
        
        # GPU ve WebGL ile ilgili ek ayarlar
        chrome_options.add_argument('--ignore-gpu-blocklist')
        chrome_options.add_argument('--disable-gpu-sandbox')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-accelerated-2d-canvas')
        chrome_options.add_argument('--disable-accelerated-jpeg-decoding')
        chrome_options.add_argument('--disable-accelerated-mjpeg-decode')
        chrome_options.add_argument('--disable-accelerated-video-decode')
        
        # Diğer performans ayarları
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-notifications')
        
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def _get_timeout(self, url: str) -> int:
        """Site bazlı timeout değerini döndür"""
        for domain, timeout in SITE_TIMEOUTS.items():
            if domain in url:
                return timeout
        return SITE_TIMEOUTS['default']