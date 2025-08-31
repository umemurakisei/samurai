from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..config import Settings
from .base import ChatMessage, LLMProvider, LLMResponse
from .providers.mock import MockProvider


class LLMManager:
	"""Dispatches requests to configured providers with graceful fallbacks."""

	def __init__(self, settings: Settings) -> None:
		self.settings = settings
		self._providers: Dict[str, LLMProvider] = {
			"mock": MockProvider(),
		}
		# Lazy import heavy providers to avoid import errors if optional deps miss
		try:
			from .providers.openai import OpenAIProvider

			self._providers["openai"] = OpenAIProvider(api_key=settings.openai_api_key)
		except Exception:
			pass
		try:
			from .providers.openrouter import OpenRouterProvider

			self._providers["openrouter"] = OpenRouterProvider(
				api_key=settings.openrouter_api_key
			)
		except Exception:
			pass
		try:
			from .providers.ollama import OllamaProvider

			self._providers["ollama"] = OllamaProvider(base_url=settings.ollama_base_url)
		except Exception:
			pass
		try:
			from .providers.hf import HFProvider

			self._providers["hf"] = HFProvider(api_key=settings.hf_api_key)
		except Exception:
			pass

	def get_provider(self, name: str) -> Optional[LLMProvider]:
		return self._providers.get(name)

	async def complete(
		self,
		messages: List[ChatMessage],
		model_hint: Optional[str] = None,
		stream: bool = False,
		**kwargs: Any,
	) -> LLMResponse | AsyncGenerator[str, None]:
		"""Try providers by priority until one succeeds."""
		for provider_name in self.settings.providers_priority:
			provider = self.get_provider(provider_name)
			if provider is None:
				continue
			try:
				model = model_hint or self._default_model_for(provider_name)
				return await provider.complete(messages, model=model, stream=stream, **kwargs)
			except Exception:
				continue
		# Fallback to mock
		return await self._providers["mock"].complete(messages, model="mock", stream=stream)

	def _default_model_for(self, provider_name: str) -> str:
		if provider_name == "openai":
			return self.settings.default_model_openai
		if provider_name == "openrouter":
			return self.settings.default_model_openrouter
		if provider_name == "ollama":
			return self.settings.default_model_ollama
		if provider_name == "hf":
			return self.settings.default_model_hf
		return "mock"
