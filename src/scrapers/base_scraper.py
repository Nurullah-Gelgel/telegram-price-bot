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
        chrome_options = Options()
        
        # Chrome options'ları config'den al
        for option in SELENIUM_CONFIG['chrome_options']:
            chrome_options.add_argument(option)
            
        # User agent'ı config'den al
        chrome_options.add_argument(f'--user-agent={SELENIUM_CONFIG["user_agent"]}')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def _get_timeout(self, url: str) -> int:
        """Site bazlı timeout değerini döndür"""
        for domain, timeout in SITE_TIMEOUTS.items():
            if domain in url:
                return timeout
        return SITE_TIMEOUTS['default']