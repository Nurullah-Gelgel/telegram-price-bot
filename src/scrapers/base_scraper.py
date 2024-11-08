from abc import ABC, abstractmethod
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import SELENIUM_CONFIG, SITE_TIMEOUTS
import logging

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
        """Ortak Chrome driver konfigürasyonu"""
        try:
            chrome_options = Options()
            
            # Chrome options'ları config'den al
            for option in SELENIUM_CONFIG['chrome_options']:
                chrome_options.add_argument(option)
                
            # Add these additional options for Linux servers
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.binary_location = '/usr/bin/google-chrome-stable'
            
            # Use system's ChromeDriver
            service = Service('/usr/local/bin/chromedriver')
            
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logging.error(f"Chrome driver initialization error: {str(e)}")
            logging.error(f"Error details: {str(e.__class__.__name__)}")
            raise

    def _get_timeout(self, url: str) -> int:
        """Site bazlı timeout değerini döndür"""
        for domain, timeout in SITE_TIMEOUTS.items():
            if domain in url:
                return timeout
        return SITE_TIMEOUTS['default']