from __future__ import annotations

import argparse
import asyncio

from .config import load_settings
from .llm import LLMManager, ChatMessage


async def main() -> None:
	parser = argparse.ArgumentParser(description="SAMURAI CLI")
	parser.add_argument("message", type=str, help="Prompt to send")
	parser.add_argument("--model", type=str, default=None)
	args = parser.parse_args()

	settings = load_settings()
	llm = LLMManager(settings)
	resp = await llm.complete([ChatMessage(role="user", content=args.message)], model_hint=args.model)
	print(getattr(resp, "text", str(resp)))


if __name__ == "__main__":
	asyncio.run(main())
