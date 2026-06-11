import os
import httpx
from typing import Optional

KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")

SYSTEM_PROMPT = (
    "You are a technical news summarizer. Given a title and article excerpt, "
    "write a concise 1-2 sentence summary focusing on the key technical insight, "
    "announcement, or development. Be specific and avoid hype. Keep it under 200 characters."
)

async def summarize_post(title: str, content: str) -> Optional[str]:
    api_key = os.getenv("KIMI_API_KEY", "")
    if not api_key:
        print("[Kimi] KIMI_API_KEY not set, skipping summary generation")
        return None

    # Truncate content to avoid burning tokens
    excerpt = (content or "")[:1200]
    user_prompt = f"Title: {title}\n\nExcerpt: {excerpt}\n\nSummarize:"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{KIMI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "kimi-k2.6",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 1,
                    "max_tokens": 120,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            print(f"[Kimi] Raw response: {data}")
            summary = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return summary if summary else None
    except httpx.HTTPStatusError as e:
        error_msg = f"[Kimi] HTTP error {e.response.status_code}: {e.response.text}"
        print(error_msg)
        return None
    except Exception as e:
        error_msg = f"[Kimi] Summary failed: {type(e).__name__}: {e}"
        print(error_msg)
        return None
