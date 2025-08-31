from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from ..base import ChatMessage, LLMResponse


class HFProvider:
	name = "hf"

	def __init__(self, api_key: str) -> None:
		self.api_key = api_key

	async def complete(
		self,
		messages: List[ChatMessage],
		model: Optional[str] = None,
		stream: bool = False,
		**kwargs: Any,
	) -> LLMResponse | AsyncGenerator[str, None]:
		# Use text-generation-inference compatible endpoints if available; for simplicity we just return last user message reversed as placeholder
		text = " ".join(m.content for m in messages if m.role == "user")[::-1]
		return LLMResponse(text=f"[HF-PLACEHOLDER] {text}", provider=self.name, model=model or "hf")
