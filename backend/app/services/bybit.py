from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

import httpx

from app.core.config import get_settings


settings = get_settings()


class BybitService:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.bybit_base_url
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30)

    async def close(self):
        await self._client.aclose()

    async def get_klines(self, symbol: str, interval: str, limit: int) -> list[dict[str, Any]]:
        # Bybit v5: GET /v5/market/kline
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": str(limit),
        }
        r = await self._client.get("/v5/market/kline", params=params)
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
        list_data = result.get("list", [])
        candles: list[dict[str, Any]] = []
        for row in reversed(list_data):
            # [ start, open, high, low, close, volume, turnover ]
            candles.append(
                {
                    "timestamp": int(row[0]),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                }
            )
        return candles
