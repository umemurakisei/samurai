from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..base import ChatMessage, LLMResponse


class MockProvider:
	name = "mock"

	async def complete(
		self,
		messages: List[ChatMessage],
		model: Optional[str] = None,
		stream: bool = False,
		**kwargs: Any,
	) -> LLMResponse | AsyncGenerator[str, None]:
		last = messages[-1].content if messages else ""
		reply = f"[SAMURAI-MOCK] You said: {last}"
		if stream:
			async def generator() -> AsyncGenerator[str, None]:
				for i in range(0, len(reply), 8):
					await asyncio.sleep(0.01)
					yield reply[i : i + 8]

			return generator()
		return LLMResponse(text=reply, provider=self.name, model=model or "mock")
