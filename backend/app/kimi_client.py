import os
import httpx
from typing import Optional

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")

SYSTEM_PROMPT = (
    "You are a technical news summarizer. Given a title and article excerpt, "
    "write a concise 1-2 sentence summary focusing on the key technical insight, "
    "announcement, or development. Be specific and avoid hype. Keep it under 200 characters."
)

async def summarize_post(title: str, content: str) -> Optional[str]:
    if not KIMI_API_KEY:
        return None

    # Truncate content to avoid burning tokens
    excerpt = (content or "")[:1200]
    user_prompt = f"Title: {title}\n\nExcerpt: {excerpt}\n\nSummarize:"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{KIMI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {KIMI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "kimi-k2.6",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 120,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            summary = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return summary if summary else None
    except Exception as e:
        print(f"[Kimi] Summary failed: {e}")
        return None
