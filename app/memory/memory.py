from __future__ import annotations

import json
import os
from typing import List

from ..llm.base import ChatMessage


class MemoryStore:
	async def load_history(self, session_id: str) -> List[ChatMessage]:
		raise NotImplementedError

	async def save_history(self, session_id: str, messages: List[ChatMessage]) -> None:
		raise NotImplementedError


class FileMemoryStore(MemoryStore):
	def __init__(self, base_path: str) -> None:
		self.base_path = base_path
		os.makedirs(self.base_path, exist_ok=True)

	def _path(self, session_id: str) -> str:
		return os.path.join(self.base_path, f"{session_id}.json")

	async def load_history(self, session_id: str) -> List[ChatMessage]:
		path = self._path(session_id)
		if not os.path.exists(path):
			return []
		with open(path, "r", encoding="utf-8") as f:
			data = json.load(f)
		return [ChatMessage(**m) for m in data]

	async def save_history(self, session_id: str, messages: List[ChatMessage]) -> None:
		path = self._path(session_id)
		with open(path, "w", encoding="utf-8") as f:
			json.dump([m.__dict__ for m in messages], f, ensure_ascii=False, indent=2)
