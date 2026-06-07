import httpx
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseScraper

class HNScraper(BaseScraper):
    def __init__(self, query: str = "", tag: str = ""):
        self.name = "hackernews"
        self.url = "https://news.ycombinator.com"
        self.category = "community"
        self.query = query
        self.tag = tag
        # Algolia HN search API: https://hn.algolia.com/api
        if tag:
            self.feed_url = f"https://hn.algolia.com/api/v1/search_by_date?tags={tag}&hitsPerPage=30"
        else:
            self.feed_url = "https://hn.algolia.com/api/v1/search_by_date?tags=front_page&hitsPerPage=30"

    async def scrape(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(self.feed_url)
            resp.raise_for_status()
            data = resp.json()

        posts = []
        for hit in data.get("hits", []):
            created = datetime.utcfromtimestamp(hit.get("created_at_i", 0))
            url = hit.get("url")
            if not url:
                url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            posts.append({
                "title": hit.get("title", "Untitled"),
                "url": url,
                "content": hit.get("story_text", "") or "",
                "published_at": created,
                "author": hit.get("author", None),
                "hn_score": hit.get("points", 0),
                "comment_count": hit.get("num_comments", 0),
            })
        return posts
