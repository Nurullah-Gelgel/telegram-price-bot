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
            
            # Add required options
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--disable-web-security')
            
            # Set binary location
            chrome_options.binary_location = '/usr/bin/google-chrome-stable'
            
            # Add user agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Create service with specific executable path
            service = Service(executable_path='/usr/local/bin/chromedriver')
            
            # Initialize and return the driver
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
            
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