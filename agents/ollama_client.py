"""Small Ollama client shared by the command-line agents.

The client deliberately uses the Ollama HTTP API directly so the agents do not
need a provider-specific SDK. If Ollama is stopped or a model is missing, the
caller receives an empty string and can use its deterministic fallback.
"""

import json
import os
from urllib import error, request


class OllamaClient:
    def __init__(self, model_env: str, default_model: str):
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv(model_env, os.getenv("OLLAMA_MODEL", default_model))
        self.last_error: str | None = None

    @property
    def configured(self) -> bool:
        return bool(self.host and self.model)

    def status(self) -> dict[str, str | bool | None]:
        return {
            "provider": "ollama",
            "host": self.host,
            "model": self.model,
            "configured": self.configured,
            "last_error": self.last_error,
        }

    def complete(self, prompt: str, system: str, *, max_tokens: int, timeout: float) -> str:
        self.last_error = None
        payload = json.dumps({
            "model": self.model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.7},
        }).encode("utf-8")
        req = request.Request(
            f"{self.host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            return str(body.get("response") or "").strip()
        except error.HTTPError as exc:
            self.last_error = f"HTTP {exc.code}"
        except (error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            self.last_error = type(exc).__name__
        return ""
