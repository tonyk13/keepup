import httpx
import json
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseScraper

class RedditScraper(BaseScraper):
    def __init__(self, subreddit: str):
        self.name = f"reddit_{subreddit}"
        self.url = f"https://www.reddit.com/r/{subreddit}/"
        self.feed_url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
        self.category = "community"

    async def scrape(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = await client.get(self.feed_url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child["data"]
            # Skip ads and stickied posts sometimes
            if post.get("stickied"):
                continue
            created = datetime.utcfromtimestamp(post.get("created_utc", 0))
            posts.append({
                "title": post.get("title", "Untitled"),
                "url": f"https://www.reddit.com{post.get('permalink', '')}",
                "content": post.get("selftext", "")[:2000],  # Truncate long selftext
                "published_at": created,
                "author": post.get("author", None),
                "hn_score": post.get("ups", 0),
                "comment_count": post.get("num_comments", 0),
            })
        return posts
