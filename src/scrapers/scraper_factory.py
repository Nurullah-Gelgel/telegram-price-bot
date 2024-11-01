from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from scrapers.trendyol_scraper import TrendyolScraper
from scrapers.hepsiburada_scraper import HepsiburadaScraper
from scrapers.n11_scraper import N11Scraper

class ScraperFactory:
    def __init__(self):
        self.scrapers: List[BaseScraper] = [
            TrendyolScraper(),
            HepsiburadaScraper(),
            N11Scraper(),
            # Yeni scraperlar buraya eklenebilir
        ]

    def get_scraper(self, url: str) -> Optional[BaseScraper]:
        for scraper in self.scrapers:
            if scraper.can_handle(url):
                return scraper
        return None

    def get_supported_sites(self) -> List[str]:
        return [scraper.get_site_name() for scraper in self.scrapers]