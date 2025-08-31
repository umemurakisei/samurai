from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import random
import re
import string
import time
from dataclasses import dataclass
from typing import Any, Dict, List


class BaseTool:
	name: str = "base"
	description: str = ""

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		raise NotImplementedError


class TimeTool(BaseTool):
	name = "time.now"
	description = "Get current UNIX time and ISO timestamp"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		now = time.time()
		return {"unix": int(now), "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}


class UUIDTool(BaseTool):
	name = "uuid.generate"
	description = "Generate a random UUID v4"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		h = hashlib.sha256(f"{time.time()}-{random.random()}".encode()).hexdigest()
		return {"uuid": f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"}


class SearchReplaceTool(BaseTool):
	name = "text.search_replace"
	description = "Find and replace pattern in text. Input JSON: {text, pattern, replace}"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		try:
			obj = json.loads(message)
		except Exception:
			return {"error": "Invalid JSON"}
		text = obj.get("text", "")
		pattern = obj.get("pattern", "")
		repl = obj.get("replace", "")
		try:
			compiled = re.compile(pattern)
		except Exception as e:
			return {"error": f"bad pattern: {e}"}
		result = compiled.sub(repl, text)
		return {"result": result}


class ShellEchoTool(BaseTool):
	name = "shell.echo"
	description = "Echo back the input message (safe shell placeholder)"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		return {"echo": message}


class RandomNumberTool(BaseTool):
	name = "random.number"
	description = "Generate random integer. Input JSON: {min, max}"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		try:
			obj = json.loads(message)
		except Exception:
			obj = {}
		lo = int(obj.get("min", 0))
		hi = int(obj.get("max", 100))
		return {"number": random.randint(lo, hi)}


class MarkdownToHTMLTool(BaseTool):
	name = "convert.md_to_html"
	description = "Very small markdown-to-HTML converter for headings and code blocks"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		text = message
		# extremely minimal conversion
		html = text
		html = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
		html = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
		html = re.sub(r"```([\s\S]*?)```", r"<pre><code>\1</code></pre>", html)
		html = html.replace("\n", "<br>")
		return {"html": html}


class JSONValidatorTool(BaseTool):
	name = "json.validate"
	description = "Validate JSON string and return parsed object or error"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		try:
			parsed = json.loads(message)
			return {"valid": True, "object": parsed}
		except Exception as e:
			return {"valid": False, "error": str(e)}


class TextSummarizerTool(BaseTool):
	name = "text.summarize"
	description = "Naive summarizer: returns the first N sentences. Input JSON: {text, sentences}"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		try:
			obj = json.loads(message)
		except Exception:
			return {"error": "Invalid JSON"}
		text = obj.get("text", "")
		num = int(obj.get("sentences", 3))
		sentences = re.split(r"(?<=[.!?])\s+", text)
		return {"summary": " ".join(sentences[:num]).strip()}


class KeywordExtractorTool(BaseTool):
	name = "text.keywords"
	description = "Extract frequent keywords (naive). Input JSON: {text, topN}"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		try:
			obj = json.loads(message)
		except Exception:
			return {"error": "Invalid JSON"}
		text = obj.get("text", "")
		topn = int(obj.get("topN", 10))
		words = re.findall(r"[A-Za-z0-9_]+", text.lower())
		freq: Dict[str, int] = {}
		for w in words:
			if len(w) <= 2:
				continue
			freq[w] = freq.get(w, 0) + 1
		items = sorted(freq.items(), key=lambda x: -x[1])[:topn]
		return {"keywords": [{"word": w, "count": c} for w, c in items]}


class CSVToJSONTool(BaseTool):
	name = "convert.csv_to_json"
	description = "Convert CSV text to JSON array"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		reader = csv.DictReader(io.StringIO(message))
		return {"rows": list(reader)}


class QRCodeTool(BaseTool):
	name = "encode.qr_base64"
	description = "Return base64 placeholder for QR encoding (no external deps)"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		# Not a real QR encoder, but placeholder to keep deps minimal
		encoded = base64.b64encode(message.encode()).decode()
		return {"qr_base64": encoded}


class PasswordGeneratorTool(BaseTool):
	name = "security.password"
	description = "Generate a random password. Input JSON: {length}"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		try:
			obj = json.loads(message)
		except Exception:
			obj = {}
		length = int(obj.get("length", 16))
		alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+"
		pwd = "".join(random.choice(alphabet) for _ in range(length))
		return {"password": pwd}


class SlugifyTool(BaseTool):
	name = "text.slugify"
	description = "Slugify a string into URL-safe format"

	async def invoke(self, message: str, session_id: str) -> Dict[str, Any]:
		slug = re.sub(r"[^a-zA-Z0-9]+", "-", message).strip("-").lower()
		return {"slug": slug}

