from __future__ import annotations

from typing import Any

from app.services.news import NewsService
from app.services.llm import LLMService
from .base import AgentBase, Signal


DEFAULT_NEWS_PROMPT = (
    "You are a crypto news sentiment analyst. Aggregate latest headlines.\n"
    "Rules: classify sentiment as positive/negative/neutral and map to buy/sell/hold."
)


class NewsAgent(AgentBase):
    def __init__(self, name: str, prompt: str = DEFAULT_NEWS_PROMPT):
        super().__init__(name=name, prompt=prompt)
        self.news = NewsService()
        self.llm = LLMService()

    async def run(self) -> tuple[Signal, dict[str, Any]]:
        headlines = await self.news.fetch_headlines(limit=20)
        text = "\n".join(
            f"- {h['title']}" for h in headlines if h.get("title"))
        instruction = (
            self.prompt
            + "\nReturn JSON with fields sentiment in {positive,negative,neutral} and action in {buy,sell,hold}.\n"
            + text
        )
        # Use LLM to interpret sentiment according to prompt
        analysis = await self.llm._ollama_chat("System: news sentiment", instruction)
        # naive parse
        sentiment = "neutral"
        action: Signal = "hold"
        lower = analysis.lower()
        if "buy" in lower:
            action = "buy"
        if "sell" in lower:
            action = "sell"
        if "positive" in lower:
            sentiment = "positive"
        elif "negative" in lower:
            sentiment = "negative"
        return action, {"sentiment": sentiment, "raw": analysis[:2000]}
