from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional, Protocol


@dataclass
class ChatMessage:
	role: str
	content: str
	name: Optional[str] = None


@dataclass
class LLMResponse:
	text: str
	provider: str
	model: str
	finish_reason: str = "stop"
	usage: Optional[Dict[str, Any]] = None
	tool_calls: Optional[List[Dict[str, Any]]] = None


class LLMProvider(Protocol):
	name: str

	async def complete(
		self,
		messages: List[ChatMessage],
		model: Optional[str] = None,
		stream: bool = False,
		**kwargs: Any,
	) -> LLMResponse | AsyncGenerator[str, None]:
		...
