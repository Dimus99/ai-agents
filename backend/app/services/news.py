from __future__ import annotations

from typing import Any

import httpx


class NewsService:
    def __init__(self, rss_url: str = "https://cryptopanic.com/api/v1/posts/?auth_token=demo&kind=news"):
        self._client = httpx.AsyncClient(timeout=30)
        self._rss_url = rss_url

    async def close(self):
        await self._client.aclose()

    async def fetch_headlines(self, limit: int = 20) -> list[dict[str, Any]]:
        r = await self._client.get(self._rss_url)
        r.raise_for_status()
        data = r.json()
        items = data.get("results", [])[:limit]
        headlines = [
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "source": item.get("domain"),
                "published_at": item.get("published_at"),
            }
            for item in items
        ]
        return headlines
