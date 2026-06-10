#!/usr/bin/env python3
"""Backfill LLM summaries for posts from the past week."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from datetime import datetime, timedelta
from app.db import SessionLocal, Post
from app.kimi_client import summarize_post

async def main():
    db = SessionLocal()
    try:
        # Find posts from the past week without summaries
        cutoff = datetime.utcnow() - timedelta(days=7)
        posts = db.query(Post).filter(
            Post.published_at >= cutoff,
            Post.llm_summary == None
        ).order_by(Post.published_at.desc()).all()

        if not posts:
            print("No posts from the past week need summarization.")
            return

        print(f"Found {len(posts)} posts from the past week without summaries.")
        print(f"Estimated cost: ${len(posts) * 0.001:.2f} (assuming ~$0.001 per summary)")
        print()

        for i, p in enumerate(posts, 1):
            summary = await summarize_post(p.title, p.content)
            if summary:
                p.llm_summary = summary
                db.add(p)
                db.commit()
                print(f"[{i}/{len(posts)}] ✓ {p.title[:60]}...")
                print(f"         → {summary[:120]}")
            else:
                print(f"[{i}/{len(posts)}] ✗ Failed: {p.title[:60]}...")
            print()

        print(f"Done! Updated {len(posts)} posts.")
    finally:
        db.close()

if __name__ == "__main__":
    if not os.getenv("KIMI_API_KEY"):
        print("ERROR: KIMI_API_KEY environment variable is not set.")
        print("Set it with: export KIMI_API_KEY='your-key-here'")
        sys.exit(1)
    asyncio.run(main())
