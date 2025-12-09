import logging
from typing import List

from fastapi import HTTPException, status
from openai import AsyncOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMClient:
    def __init__(self, api_key: str | None = settings.openai_api_key, model: str | None = settings.openai_model):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def generate(self, messages: List[dict]) -> str:
        if not self.client:
            logger.info("OPENAI_API_KEY not set; returning placeholder draft.")
            return "# Draft unavailable\n\nProvide OPENAI_API_KEY to enable Markdown generation."

        try:
            response = await self.client.chat.completions.create(model=self.model, messages=messages)
        except Exception as exc:
            logger.exception("LLM generation failed: %s", exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="LLM generation failed.") from exc

        if not response.choices:
            return ""
        return response.choices[0].message.content or ""
