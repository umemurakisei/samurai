from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional

from .llm import LLMManager, ChatMessage
from .tools.registry import ToolRegistry
from .memory.memory import MemoryStore
from .utils.structured import validate_json_string


class ChatOrchestrator:
	"""Coordinates chat, tools, memory, and advanced modes."""

	def __init__(
		self,
		llm_manager: LLMManager,
		tool_registry: ToolRegistry,
		memory_store: MemoryStore,
	) -> None:
		self.llm_manager = llm_manager
		self.tool_registry = tool_registry
		self.memory_store = memory_store

	async def chat(self, session_id: str, message: str, options: Dict[str, Any]) -> Dict[str, Any]:
		messages: List[ChatMessage] = await self.memory_store.load_history(session_id)
		messages.append(ChatMessage(role="user", content=message))

		use_tool = options.get("tool")
		debate = bool(options.get("debate"))
		model_hint = options.get("model")
		structured_schema = options.get("schema")

		if use_tool:
			tool = self.tool_registry.get_tool(use_tool)
			if tool is None:
				return {"error": f"unknown tool: {use_tool}"}
			tool_result = await tool.invoke(message=message, session_id=session_id)
			messages.append(ChatMessage(role="tool", content=json.dumps(tool_result)))

		if debate:
			assistant_reply = await self._debate(messages, model_hint)
		else:
			resp = await self.llm_manager.complete(messages, model_hint=model_hint, stream=False)
			assistant_reply = resp.text if hasattr(resp, "text") else str(resp)

		# Optional structured validation
		if structured_schema:
			ok, err = validate_json_string(assistant_reply, structured_schema)
			if not ok:
				assistant_reply = (
					"The output did not match the requested schema. Errors:\n"
					+ err
				)

		messages.append(ChatMessage(role="assistant", content=assistant_reply))
		await self.memory_store.save_history(session_id, messages)
		return {"reply": assistant_reply}

	async def stream_chat(
		self, session_id: str, message: str, options: Dict[str, Any]
	) -> AsyncGenerator[str, None]:
		messages: List[ChatMessage] = await self.memory_store.load_history(session_id)
		messages.append(ChatMessage(role="user", content=message))

		use_tool = options.get("tool")
		model_hint = options.get("model")

		if use_tool:
			tool = self.tool_registry.get_tool(use_tool)
			if tool is None:
				yield "[tool-error] unknown tool"
			else:
				tool_result = await tool.invoke(message=message, session_id=session_id)
				messages.append(ChatMessage(role="tool", content=json.dumps(tool_result)))

		stream_resp = await self.llm_manager.complete(messages, model_hint=model_hint, stream=True)
		assistant_text = ""
		async for chunk in stream_resp:  # type: ignore
			assistant_text += chunk
			yield chunk

		messages.append(ChatMessage(role="assistant", content=assistant_text))
		await self.memory_store.save_history(session_id, messages)

	async def _debate(self, messages: List[ChatMessage], model_hint: Optional[str]) -> str:
		"""Simple two-expert debate followed by synthesis."""
		pro_messages = messages + [
			ChatMessage(
				role="system",
				content=(
					"You are Expert A. Propose a detailed solution with pros."
				),
			)
		]
		con_messages = messages + [
			ChatMessage(
				role="system",
				content=(
					"You are Expert B. Critique and find risks and alternatives."
				),
			)
		]
		resp_a = await self.llm_manager.complete(pro_messages, model_hint=model_hint)
		resp_b = await self.llm_manager.complete(con_messages, model_hint=model_hint)
		synthesis_messages = messages + [
			ChatMessage(
				role="system",
				content=(
					"Synthesize the best plan combining A and B, be concise and actionable."
				),
			),
			ChatMessage(role="assistant", content=getattr(resp_a, "text", str(resp_a))),
			ChatMessage(role="assistant", content=getattr(resp_b, "text", str(resp_b))),
		]
		resp_s = await self.llm_manager.complete(synthesis_messages, model_hint=model_hint)
		return getattr(resp_s, "text", str(resp_s))
