from __future__ import annotations

import os
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from ..base import ChatMessage, LLMResponse


class OpenAIProvider:
	name = "openai"

	def __init__(self, api_key: str) -> None:
		self.api_key = api_key
		self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

	async def complete(
		self,
		messages: List[ChatMessage],
		model: Optional[str] = None,
		stream: bool = False,
		**kwargs: Any,
	) -> LLMResponse | AsyncGenerator[str, None]:
		headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
		payload = {
			"model": model or "gpt-4o-mini",
			"messages": [m.__dict__ for m in messages],
			"stream": bool(stream),
		}
		async with httpx.AsyncClient(timeout=60.0) as client:
			if stream:
				resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
				resp.raise_for_status()
				async def gen():
					async for line in resp.aiter_lines():
						if not line or not line.startswith("data: "):
							continue
						data = line[6:]
						if data.strip() == "[DONE]":
							break
						yield data
				return gen()
			else:
				resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
				resp.raise_for_status()
				data = resp.json()
				text = data["choices"][0]["message"]["content"]
				finish = data["choices"][0].get("finish_reason", "stop")
				usage = data.get("usage")
				return LLMResponse(text=text, provider=self.name, model=payload["model"], finish_reason=finish, usage=usage)
