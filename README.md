SAMURAI
=====

Ultra-fast, modular chat AI with multi-provider LLM adapters, built-in tools, memory, streaming, and a minimal web UI.

Quickstart
---------

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. (Optional) Set API keys:

```bash
export OPENAI_API_KEY=sk-...
export OPENROUTER_API_KEY=or-...
export HF_API_KEY=hf_...
export OLLAMA_BASE_URL=http://localhost:11434
```

3. Run the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the web UI at http://localhost:8000

API
---

- GET /api/health
- GET /api/tools
- POST /api/chat { session_id, message, options: { tool, debate, model } }
- POST /api/chat/stream (same payload) -> SSE

Notes
-----

- Providers in `app/llm/providers`.
- Tools in `app/tools`.
- Memory in `app/memory`.
# samurai