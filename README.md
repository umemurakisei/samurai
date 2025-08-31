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

Deployment
----------

Docker (generic):

```bash
docker build -t samurai .
docker run -p 8000:8000 --env-file .env samurai
```

Render.com:

1) Push this repo to GitHub. 2) Import in Render using `render.yaml`. 3) Add custom domain `samurai.sui-tool.com` in Render dashboard and follow its DNS instructions (usually a CNAME to a Render hostname). 4) Set env vars.

Fly.io:

```bash
flyctl launch --no-deploy
flyctl deploy
flyctl certs add samurai.sui-tool.com
```

Star Domain / スターサーバー DNS 設定（samurai.sui-tool.com）
-----------------------------------------------

- ネームサーバー: NS1.STAR-DOMAIN.JP / NS2.STAR-DOMAIN.JP / NS3.STAR-DOMAIN.JP が設定済みであることを確認。
- サブドメイン追加（スターサーバー管理画面 → サブドメイン設定）で `samurai` を作成。
- API を Render/Fly など外部で動かす場合:
  - Render: カスタムドメインに `samurai.sui-tool.com` を追加 → 指定の CNAME をスタードメインDNSに登録（ホスト名: samurai, 種別: CNAME, 値: 指示のホスト名）。
  - Fly.io: `flyctl certs add samurai.sui-tool.com` 後の指示に従い、A/AAAA または CNAME を登録。
- スターサーバーで静的ファイルを配信し、API は外部に向ける場合:
  - `web/index.html` の `<meta name="api-base" content="https://<your-api-host>" />` を設定。
  - CORS は `CORS_ALLOW_ORIGINS` 環境変数で `https://samurai.sui-tool.com` を許可済み。
- 反映には最大 24 時間。確認: `https://samurai.sui-tool.com/app` と `/api/health`（API ホスト側）

スターサーバーでパス配信（sui-tool.com/samurai）
--------------------------------------------

- フロント（静的）: `web/` の中身をスターサーバーの公開ディレクトリにアップロードし、`/samurai` 配下で参照できるように配置。
  - 例: ドキュメントルート直下に `samurai/` ディレクトリを作成し、その中へ `web/` のファイルをそのまま配置。
- API は外部ホスト（Render/Fly等）を使用:
  - 何も設定しない場合、UI は現在のオリジンを API ベースとして使います（`index.html` で `api-base` 未設定時は `window.location.origin`）。
  - API が別ホストの場合は、`index.html` の `<meta name="api-base" content="https://<api-host>" />` を設定。
  - CORS は `CORS_ALLOW_ORIGINS` に `https://sui-tool.com` を含めてください（既定で追加済み）。
- 動作確認: `https://sui-tool.com/samurai` でUI、APIホストの `/api/health` が稼働していること。
# samurai