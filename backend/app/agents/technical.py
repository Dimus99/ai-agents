from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

try:
    import pandas_ta as ta  # type: ignore
except Exception:  # pragma: no cover - optional in dev
    ta = None

from app.core.config import get_settings
from app.services.bybit import BybitService
from .base import AgentBase, Signal


settings = get_settings()


DEFAULT_TECH_PROMPT = (
    "You are a technical analysis agent. Use RSI(14), MACD(12,26,9), SMA(50,200).\n"
    "Rules: \n- If price above SMA200 and RSI<30 -> buy.\n- If price below SMA200 and RSI>70 -> sell.\n- If MACD crosses up -> buy bias; crosses down -> sell bias.\n"
    "Return one of: buy, sell, hold."
)


class TechnicalAgent(AgentBase):
    def __init__(self, name: str, prompt: str = DEFAULT_TECH_PROMPT):
        super().__init__(name=name, prompt=prompt)
        self.bybit = BybitService()

    async def run(self) -> tuple[Signal, dict[str, Any]]:
        candles = await self.bybit.get_klines(
            settings.bybit_symbol, settings.bybit_interval, settings.bybit_lookback_candles
        )
        df = pd.DataFrame(candles)
        df["close"] = df["close"].astype(float)

        if ta is not None:
            df["rsi"] = ta.rsi(df["close"], length=14)
            macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
            df["macd"] = macd["MACD_12_26_9"]
            df["macd_signal"] = macd["MACDs_12_26_9"]
            df["sma50"] = ta.sma(df["close"], length=50)
            df["sma200"] = ta.sma(df["close"], length=200)
        else:
            # Fallback crude indicators
            df["rsi"] = self._rsi(df["close"].values, 14)
            df["sma50"] = df["close"].rolling(50).mean()
            df["sma200"] = df["close"].rolling(200).mean()
            df["macd"] = df["close"].ewm(
                span=12).mean() - df["close"].ewm(span=26).mean()
            df["macd_signal"] = df["macd"].ewm(span=9).mean()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signal: Signal = "hold"
        reasoning: list[str] = []

        sma200 = float(latest.get("sma200", np.nan))
        rsi_val = float(latest.get("rsi", np.nan))
        close_val = float(latest.get("close", np.nan))
        if not np.isnan(sma200) and not np.isnan(rsi_val) and close_val > sma200 and rsi_val < 30:
            signal = "buy"
            reasoning.append("Above SMA200 and RSI<30")
        if not np.isnan(sma200) and not np.isnan(rsi_val) and close_val < sma200 and rsi_val > 70:
            signal = "sell"
            reasoning.append("Below SMA200 and RSI>70")

        macd_cross_up = prev["macd"] < prev["macd_signal"] and latest["macd"] > latest["macd_signal"]
        macd_cross_down = prev["macd"] > prev["macd_signal"] and latest["macd"] < latest["macd_signal"]
        if macd_cross_up and signal != "sell":
            signal = "buy"
            reasoning.append("MACD cross up")
        if macd_cross_down and signal != "buy":
            signal = "sell"
            reasoning.append("MACD cross down")

        return signal, {
            "close": close_val,
            "rsi": rsi_val,
            "sma50": float(latest.get("sma50", np.nan)),
            "sma200": sma200,
            "macd": float(latest.get("macd", np.nan)),
            "macd_signal": float(latest.get("macd_signal", np.nan)),
            "reasoning": "; ".join(reasoning),
        }

    @staticmethod
    def _rsi(prices: np.ndarray, period: int) -> pd.Series:
        delta = np.diff(prices, prepend=prices[0])
        gain = np.where(delta > 0, delta, 0.0)
        loss = np.where(delta < 0, -delta, 0.0)
        roll_up = pd.Series(gain).ewm(span=period).mean()
        roll_down = pd.Series(loss).ewm(span=period).mean()
        rs = roll_up / (roll_down + 1e-9)
        return 100.0 - (100.0 / (1.0 + rs))
