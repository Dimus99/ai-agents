from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


settings = get_settings()


class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "openai":
            return await self._openai_chat(system_prompt, user_prompt)
        return await self._ollama_chat(system_prompt, user_prompt)

    async def mutate_prompt(self, description: str, current_prompt: str) -> str:
        system_prompt = (
            "You are an expert quantitative trading strategist. Improve the agent's prompt to increase trading performance."
        )
        user_prompt = (
            "Agent description:\n" + description +
            "\n\nCurrent prompt:\n" + current_prompt + "\n\n"
            "Respond with an improved prompt only, concise, with concrete parameter values and rules."
        )
        return await self.chat(system_prompt, user_prompt)

    async def _openai_chat(self, system_prompt: str, user_prompt: str) -> str:
        base_url = settings.openai_base_url or "https://api.openai.com/v1"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        }
        async with httpx.AsyncClient(timeout=60, base_url=base_url) as client:
            r = await client.post("/chat/completions", json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

    async def _ollama_chat(self, system_prompt: str, user_prompt: str) -> str:
        base_url = settings.ollama_base_url.rstrip("/")
        payload = {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{base_url}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
            return data["message"]["content"].strip()
