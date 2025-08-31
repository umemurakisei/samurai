from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from jsonschema import Draft202012Validator


def validate_json_string(text: str, schema: Dict[str, Any]) -> Tuple[bool, str]:
	"""Validate a JSON string against a JSON Schema. Returns (ok, error_string)."""
	try:
		obj = json.loads(text)
	except Exception as e:
		return False, f"JSON parse error: {e}"
	validator = Draft202012Validator(schema)
	errors = sorted(validator.iter_errors(obj), key=lambda e: e.path)
	if errors:
		lines = []
		for err in errors:
			loc = "/".join(str(x) for x in err.path)
			lines.append(f"{loc}: {err.message}")
		return False, "\n".join(lines)
	return True, ""
