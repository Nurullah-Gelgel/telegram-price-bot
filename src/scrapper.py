from typing import Tuple, Optional
import logging
from scrapers.scraper_factory import ScraperFactory

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PriceScraper:
    def __init__(self):
        self.factory = ScraperFactory()

    def get_price(self, url: str) -> Tuple[Optional[float], str]:
        scraper = self.factory.get_scraper(url)
        if not scraper:
            supported_sites = ", ".join(self.factory.get_supported_sites())
            logger.error(f"Unsupported site. Supported sites are: {supported_sites}")
            return None, url
            
        return scraper.extract_price(url)

    def get_supported_sites(self) -> list[str]:
        return self.factory.get_supported_sites()

# Global instance for backwards compatibility
_scraper = PriceScraper()
fiyat_cek = _scraper.get_price