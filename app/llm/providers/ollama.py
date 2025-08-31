from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from ..base import ChatMessage, LLMResponse


class OllamaProvider:
	name = "ollama"

	def __init__(self, base_url: str = "http://localhost:11434") -> None:
		self.base_url = base_url.rstrip("/")

	async def complete(
		self,
		messages: List[ChatMessage],
		model: Optional[str] = None,
		stream: bool = False,
		**kwargs: Any,
	) -> LLMResponse | AsyncGenerator[str, None]:
		payload = {
			"model": model or "llama3.1",
			"messages": [m.__dict__ for m in messages],
			"stream": bool(stream),
		}
		async with httpx.AsyncClient(timeout=None) as client:
			if stream:
				resp = await client.post(f"{self.base_url}/api/chat", json=payload)
				resp.raise_for_status()
				async def gen():
					async for line in resp.aiter_lines():
						if not line:
							continue
						yield line
				return gen()
			else:
				resp = await client.post(f"{self.base_url}/api/chat", json=payload)
				resp.raise_for_status()
				data = resp.json()
				# Ollama non-stream returns message.content
				text = data.get("message", {}).get("content", "")
				return LLMResponse(text=text, provider=self.name, model=payload["model"]) 
