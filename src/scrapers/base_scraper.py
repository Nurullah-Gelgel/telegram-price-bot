from abc import ABC, abstractmethod
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import SELENIUM_CONFIG, SITE_TIMEOUTS
import logging
import platform

class BaseScraper(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass

    @abstractmethod
    def get_site_name(self) -> str:
        pass

    @abstractmethod
    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        pass

    def _get_chrome_driver(self):
        """İşletim sistemine göre Chrome driver ayarlarını yapılandırır"""
        try:
            chrome_options = Options()
            
            # Ortak ayarlar
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # İşletim sistemine göre özel ayarlar
            if platform.system() == 'Linux':
                # Linux ayarları
                chrome_options.binary_location = '/usr/bin/google-chrome-stable'
                chrome_options.add_argument('--disable-software-rasterizer')
                chrome_options.add_argument('--disable-features=NetworkService')
                chrome_options.add_argument('--remote-debugging-port=9222')
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                # Linux için ChromeDriver service
                service = Service(executable_path='/usr/local/bin/chromedriver')
            else:
                # Windows ayarları
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                # Windows için ChromeDriver service
                service = Service(ChromeDriverManager().install())
            
            # Driver'ı oluştur ve döndür
            return webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            logging.error(f"Chrome driver initialization error: {str(e)}")
            logging.error(f"Error details: {str(e.__class__.__name__)}")
            logging.error(f"Operating System: {platform.system()}")
            return None

    def _get_timeout(self, url: str) -> int:
        """Site bazlı timeout değerini döndür"""
        for domain, timeout in SITE_TIMEOUTS.items():
            if domain in url:
                return timeout
        return SITE_TIMEOUTS['default']