from __future__ import annotations

import os
from typing import List


class Settings:
	"""Application settings loaded from environment variables.

	These are intentionally simple to avoid extra runtime dependencies. Provide
	API keys via environment variables if you want to use external providers.
	"""

	app_name: str
	providers_priority: List[str]
	default_model_openai: str
	default_model_openrouter: str
	default_model_ollama: str
	default_model_hf: str

	openai_api_key: str
	openrouter_api_key: str
	hf_api_key: str
	ollama_base_url: str
	# CORS
	cors_allow_origins: List[str]

	def __init__(self) -> None:
		self.app_name = os.getenv("SAMURAI_APP_NAME", "SAMURAI")
		providers = os.getenv(
			"SAMURAI_PROVIDERS",
			"openai,openrouter,ollama,hf,mock",
		)
		self.providers_priority = [p.strip() for p in providers.split(",") if p.strip()]

		self.default_model_openai = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
		self.default_model_openrouter = os.getenv(
			"OPENROUTER_MODEL",
			"openrouter/auto",
		)
		self.default_model_ollama = os.getenv("OLLAMA_MODEL", "llama3.1")
		self.default_model_hf = os.getenv("HF_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")

		self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
		self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
		self.hf_api_key = os.getenv("HF_API_KEY", "")
		self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

		cors = os.getenv(
			"CORS_ALLOW_ORIGINS",
			"http://localhost:8000,https://samurai.sui-tool.com",
		)
		self.cors_allow_origins = [o.strip() for o in cors.split(",") if o.strip()]


def load_settings() -> Settings:
	return Settings()
