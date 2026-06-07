from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class BaseScraper(ABC):
    name: str = ""
    url: str = ""
    category: str = ""

    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """Return list of post dicts with keys: title, url, content, published_at, author, hn_score, comment_count"""
        pass

    def __repr__(self):
        return f"<Scraper {self.name}>"
