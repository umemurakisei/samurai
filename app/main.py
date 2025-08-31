from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import orjson
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import load_settings
from .llm import LLMManager
from .orchestrator import ChatOrchestrator
from .tools.registry import ToolRegistry
from .memory.memory import FileMemoryStore


settings = load_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_allow_origins,
	allow_methods=["*"],
	allow_headers=["*"],
	allow_credentials=True,
)


# Static web UI under /app to avoid colliding with /api
app.mount("/app", StaticFiles(directory="/workspace/web", html=True), name="web")


# Core services
llm_manager = LLMManager(settings)
memory_store = FileMemoryStore(base_path="/workspace/samurai_data/memory")
tool_registry = ToolRegistry()


@app.get("/api/health")
async def health() -> Dict[str, Any]:
	return {
		"status": "ok",
		"app": settings.app_name,
		"version": __version__,
	}


@app.get("/api/tools")
async def list_tools() -> Dict[str, Any]:
	return {"tools": tool_registry.list_tools_info()}


@app.post("/api/chat")
async def chat(
	payload: Dict[str, Any] = Body(..., embed=False),
) -> JSONResponse:
	"""Synchronous chat completion with optional tool use and features.

	Payload example:
	{
		"session_id": "abc",
		"message": "Hello",
		"options": {"debate": false, "tool": null}
	}
	"""
	session_id = str(payload.get("session_id") or "default")
	message = str(payload.get("message") or "").strip()
	options = payload.get("options") or {}
	if not message:
		raise HTTPException(status_code=400, detail="message is required")

	orchestrator = ChatOrchestrator(
		llm_manager=llm_manager,
		tool_registry=tool_registry,
		memory_store=memory_store,
	)
	result = await orchestrator.chat(session_id=session_id, message=message, options=options)
	return JSONResponse(content=result)


@app.post("/api/chat/stream")
async def chat_stream(
	payload: Dict[str, Any] = Body(..., embed=False),
) -> StreamingResponse:
	"""Streaming chat endpoint (SSE-formatted)."""
	session_id = str(payload.get("session_id") or "default")
	message = str(payload.get("message") or "").strip()
	options = payload.get("options") or {}
	if not message:
		raise HTTPException(status_code=400, detail="message is required")

	orchestrator = ChatOrchestrator(
		llm_manager=llm_manager,
		tool_registry=tool_registry,
		memory_store=memory_store,
	)

	async def event_generator() -> AsyncGenerator[bytes, None]:
		async for chunk in orchestrator.stream_chat(
			session_id=session_id, message=message, options=options
		):
			yield f"data: {json.dumps({'chunk': chunk})}\n\n".encode("utf-8")
		yield b"data: {\"event\": \"end\"}\n\n"

	return StreamingResponse(
		event_generator(),
		media_type="text/event-stream",
		headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
	)
