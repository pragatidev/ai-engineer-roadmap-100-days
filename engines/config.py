"""The only place model IDs live."""

from __future__ import annotations

from pathlib import Path

import httpx
from dotenv import dotenv_values

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"

# Keys come only from course_repo/.env. Parent folders are never walked.
DEFAULT_OLLAMA_HOST = "http://localhost:11434"

ENGINES = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
        "model": "gpt-5.6-terra",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "env_key": "ANTHROPIC_API_KEY",
        "model": "claude-sonnet-5",
        "headers": {"anthropic-version": "2023-06-01"},
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "env_key": "GEMINI_API_KEY",
        "model": "gemini-3.6-flash",
    },
    "xai": {
        "base_url": "https://api.x.ai/v1",
        "env_key": "XAI_API_KEY",
        "model": "grok-4.6",
    },
    "kimi": {
        "base_url": "https://api.moonshot.ai/v1",
        "env_key": "KIMI_API_KEY",
        "model": "kimi-k2.5",
    },
    "qwen": {
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "env_key": "QWEN_API_KEY",
        "model": "qwen-plus",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "env_key": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "env_key": None,
        "model": "llama3.2",
    },
}


def read_env() -> dict[str, str]:
    if not ENV_PATH.is_file():
        return {}
    raw = dotenv_values(ENV_PATH)
    out: dict[str, str] = {}
    for key, value in raw.items():
        if key and value and value.strip():
            out[key] = value.strip()
    return out


def ollama_host(env: dict[str, str] | None = None) -> str:
    env = read_env() if env is None else env
    return env.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).rstrip("/")


def ollama_responds(host: str | None = None) -> bool:
    url = (host or ollama_host()) + "/api/tags"
    try:
        with httpx.Client(timeout=1.0) as client:
            response = client.get(url)
        return response.status_code < 500
    except Exception:
        return False


def pick_ollama_model(env: dict[str, str] | None = None) -> str:
    default = str(ENGINES["ollama"]["model"])
    try:
        with httpx.Client(timeout=1.0) as client:
            data = client.get(ollama_host(env) + "/api/tags").json()
    except Exception:
        return default
    names = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    if default in names:
        return default
    prefixed = [name for name in names if name.startswith(default + ":")]
    if prefixed:
        return prefixed[0]
    return default


def configured_engines() -> list[str]:
    env = read_env()
    found: list[str] = []
    for name, spec in ENGINES.items():
        if name == "ollama":
            if ollama_responds(ollama_host(env)):
                found.append(name)
            continue
        env_key = spec["env_key"]
        if env_key and env.get(env_key):
            found.append(name)
    return found


def resolve_engine(name: str) -> dict:
    spec = dict(ENGINES[name])
    env = read_env()
    if name == "ollama":
        spec["base_url"] = ollama_host(env) + "/v1"
        spec["api_key"] = "ollama"
        spec["model"] = pick_ollama_model(env)
    else:
        spec["api_key"] = env.get(spec["env_key"] or "", "")
    return spec
