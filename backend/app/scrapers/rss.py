import httpx
import feedparser
from datetime import datetime
from dateutil import parser as dateparser
from typing import List, Dict, Any
from .base import BaseScraper

class RSSScraper(BaseScraper):
    def __init__(self, name: str, feed_url: str, category: str, site_url: str):
        self.name = name
        self.url = site_url
        self.feed_url = feed_url
        self.category = category

    def _extract_link(self, entry) -> str:
        link = entry.get("link", "")
        if isinstance(link, dict):
            return link.get("href", "")
        if not link:
            for l in entry.get("links", []):
                if l.get("rel") in ("alternate", ""):
                    return l.get("href", "")
        return str(link) if link else ""

    def _parse_date(self, entry) -> datetime:
        # Try structured parsed dates first
        for key in ("published_parsed", "updated_parsed", "created_parsed"):
            val = entry.get(key)
            if val:
                return datetime(*val[:6])

        # Try raw date strings
        for key in ("published", "updated", "created", "pubDate"):
            val = entry.get(key)
            if val:
                try:
                    return dateparser.parse(val)
                except Exception:
                    pass

        return None

    async def scrape(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "KeepUp/1.0 (Content Aggregator; https://github.com)"
            }
            resp = await client.get(self.feed_url, headers=headers)
            resp.raise_for_status()

        parsed = feedparser.parse(resp.text)
        posts = []
        for entry in parsed.entries:
            published_dt = self._parse_date(entry)

            content = entry.get("summary", "") or entry.get("description", "")
            if entry.get("content"):
                content = entry.content[0].value
            from bs4 import BeautifulSoup
            content = BeautifulSoup(content, "lxml").get_text(separator=" ", strip=True) if content else ""

            url = self._extract_link(entry)
            if not url:
                continue

            posts.append({
                "title": entry.get("title", "Untitled"),
                "url": url,
                "content": content,
                "published_at": published_dt,
                "author": entry.get("author", None),
                "hn_score": None,
                "comment_count": None,
            })
        return posts
