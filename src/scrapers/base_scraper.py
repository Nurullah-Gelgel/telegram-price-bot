from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class ProductInfo:
    price: float
    product_id: str
    title: Optional[str] = None
    brand: Optional[str] = None

class BaseScraper(ABC):
    @abstractmethod
    def extract_price(self, url: str) -> Tuple[Optional[float], str]:
        """Extract price and product ID from the given URL"""
        pass

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this scraper can handle the given URL"""
        pass

    @abstractmethod
    def get_site_name(self) -> str:
        """Return the name of the e-commerce site"""
        pass