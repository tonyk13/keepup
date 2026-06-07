import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as dateparser
from typing import List, Dict, Any
from .base import BaseScraper

SENTINEL_DATE = datetime(1970, 1, 1)

class HTMLScraper(BaseScraper):
    def __init__(self, name: str, url: str, category: str, selectors: Dict[str, str]):
        self.name = name
        self.url = url
        self.category = category
        self.selectors = selectors

    def _resolve_url(self, href: str) -> str:
        if href.startswith("http"):
            return href
        domain = self.url.split("/")[2]
        return f"https://{domain}{href}"

    def _parse_date_from_text(self, text: str) -> datetime:
        """Try to parse dates from common text patterns."""
        if not text:
            return None
        # ISO format: 2024-01-15 or 2024-01-15T12:00:00Z
        iso_match = re.search(r'(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2}))?)', text)
        if iso_match:
            try:
                return datetime.fromisoformat(iso_match.group(1).replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                pass
        # Month Day, Year: Jan 15, 2024 or January 15, 2024
        month_year_match = re.search(
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}',
            text, re.IGNORECASE
        )
        if month_year_match:
            try:
                return dateparser.parse(month_year_match.group(0))
            except Exception:
                pass
        return None

    def _extract_date(self, article, soup) -> datetime:
        """Try multiple strategies to find a publication date."""
        # 1. <time datetime="...">
        date_el = article.select_one(self.selectors.get("date_selector", "time"))
        if date_el:
            dt_str = date_el.get("datetime") or date_el.get_text(strip=True)
            if dt_str:
                try:
                    return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).replace(tzinfo=None)
                except Exception:
                    parsed = self._parse_date_from_text(dt_str)
                    if parsed:
                        return parsed

        # 2. Meta tags in the full page
        for meta in soup.find_all("meta"):
            prop = meta.get("property", "").lower()
            name = meta.get("name", "").lower()
            if prop in ("article:published_time", "article:modified_time", "og:updated_time") or name in ("date", "publish-date"):
                content = meta.get("content", "")
                if content:
                    try:
                        return datetime.fromisoformat(content.replace("Z", "+00:00")).replace(tzinfo=None)
                    except Exception:
                        parsed = self._parse_date_from_text(content)
                        if parsed:
                            return parsed

        # 3. JSON-LD datePublished
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                data = json.loads(script.string or "{}")
                if isinstance(data, dict):
                    for key in ("datePublished", "dateModified", "dateCreated"):
                        val = data.get(key)
                        if val:
                            try:
                                return datetime.fromisoformat(val.replace("Z", "+00:00")).replace(tzinfo=None)
                            except Exception:
                                pass
                    # Sometimes it's nested under @graph
                    graph = data.get("@graph", [])
                    if isinstance(graph, list):
                        for item in graph:
                            for key in ("datePublished", "dateModified"):
                                val = item.get(key)
                                if val:
                                    try:
                                        return datetime.fromisoformat(val.replace("Z", "+00:00")).replace(tzinfo=None)
                                    except Exception:
                                        pass
            except Exception:
                pass

        # 4. Try to find date-like text in the article itself
        text = article.get_text(separator=" ", strip=True)
        parsed = self._parse_date_from_text(text)
        if parsed:
            return parsed

        return None

    async def scrape(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = await client.get(self.url, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        posts = []
        articles = soup.select(self.selectors.get("article_selector", "article"))
        for article in articles[:25]:
            title_el = article.select_one(self.selectors.get("title_selector", "h2"))
            link_el = article.select_one(self.selectors.get("link_selector", "a"))
            summary_el = article.select_one(self.selectors.get("summary_selector", "p"))

            title = title_el.get_text(strip=True) if title_el else "Untitled"
            link = ""
            if link_el:
                href = link_el.get("href", "")
                link = self._resolve_url(href)
            elif article.name == "a":
                href = article.get("href", "")
                link = self._resolve_url(href)

            published = self._extract_date(article, soup)
            summary = summary_el.get_text(separator=" ", strip=True) if summary_el else ""

            if title and link and not any(p["url"] == link for p in posts):
                posts.append({
                    "title": title,
                    "url": link,
                    "content": summary,
                    "published_at": published,
                    "author": None,
                    "hn_score": None,
                    "comment_count": None,
                })
        return posts
