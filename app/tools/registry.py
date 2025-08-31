from __future__ import annotations

import asyncio
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


class Tool(Protocol):
	name: str
	description: str

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		...


@dataclass
class ToolInfo:
	name: str
	description: str


class ToolRegistry:
	"""Holds built-in tools and user-extendable registry."""

	def __init__(self) -> None:
		self._tools: Dict[str, Tool] = {}
		self._register_builtins()

	def register(self, tool: Tool) -> None:
		self._tools[tool.name] = tool

	def get_tool(self, name: str) -> Optional[Tool]:
		return self._tools.get(name)

	def list_tools_info(self) -> List[Dict[str, str]]:
		return [
			{"name": t.name, "description": t.description} for t in self._tools.values()
		]

	def _register_builtins(self) -> None:
		from .tools_builtin import (
			TimeTool,
			UUIDTool,
			SearchReplaceTool,
			ShellEchoTool,
			RandomNumberTool,
			MarkdownToHTMLTool,
			JSONValidatorTool,
			TextSummarizerTool,
			KeywordExtractorTool,
			CSVToJSONTool,
			QRCodeTool,
			PasswordGeneratorTool,
			SlugifyTool,
		)

		for tool_cls in [
			TimeTool,
			UUIDTool,
			SearchReplaceTool,
			ShellEchoTool,
			RandomNumberTool,
			MarkdownToHTMLTool,
			JSONValidatorTool,
			TextSummarizerTool,
			KeywordExtractorTool,
			CSVToJSONTool,
			QRCodeTool,
			PasswordGeneratorTool,
			SlugifyTool,
		]:
			self.register(tool_cls())
