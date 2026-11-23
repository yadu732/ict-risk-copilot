"""Small HTTP client for a LOCAL Ollama model, with schema-constrained output."""

from __future__ import annotations

import json
from urllib.parse import urlparse

import requests
from pydantic import BaseModel


class OllamaError(RuntimeError):
    pass


def local_url(base_url: str) -> str:
    """Prohibit remote servers; synthetic-only data stays on the local machine."""
    parsed = urlparse(base_url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"localhost", "127.0.0.1"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or parsed.port is None
    ):
        raise OllamaError("Ollama must use a local http://localhost:PORT URL")
    return f"http://{parsed.hostname}:{parsed.port}"


def generate_structured(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    schema: type[BaseModel],
    base_url: str = "http://127.0.0.1:11434",
    timeout: int = 120,
) -> dict:
    base = local_url(base_url)
    if not model or len(model) > 100:
        raise OllamaError("Invalid Ollama model name")
    payload = {
        "model": model,
        "stream": False,
        "format": schema.model_json_schema(),
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    try:
        response = requests.post(f"{base}/api/chat", json=payload, timeout=timeout)
        response.raise_for_status()
        body = response.json()
        content = body["message"]["content"]
        parsed = json.loads(content)
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        raise OllamaError(
            "Ollama could not generate valid structured output. "
            "Check that Ollama is running and your model is installed."
        ) from exc
    if not isinstance(parsed, dict):
        raise OllamaError("Model returned a non-object JSON value")
    return parsed
