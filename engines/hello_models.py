"""One schema for every engine. Walk every configured engine and print one row each."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engines.config import configured_engines, resolve_engine

PROMPT = "Reply with the single word pong."
NO_ENGINE = (
    "No engine is configured. Copy .env.example to .env and set one API key, "
    "or start Ollama, then run this again."
)


# MODEL CALL. You ask. It writes. Then this function stops.
def chat(spec: dict, prompt: str) -> str:
    url = spec["base_url"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {spec['api_key']}",
        "Content-Type": "application/json",
    }
    headers.update(spec.get("headers") or {})
    body = {
        "model": spec["model"],
        "messages": [{"role": "user", "content": prompt}],
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
    return data["choices"][0]["message"]["content"]


def format_row(engine: str, model: str, latency_ms: int | str, reply: str) -> str:
    return f"{engine} | {model} | {latency_ms} | {reply}"


# HARNESS. The harness walks every configured engine, times each call, prints one row per engine, then stops. No tool. No second decide. No check.
def main() -> int:
    names = configured_engines()
    if not names:
        print(NO_ENGINE)
        return 0

    for name in names:
        spec = resolve_engine(name)
        started = time.perf_counter()
        reply = chat(spec, PROMPT)
        latency_ms = int((time.perf_counter() - started) * 1000)
        snippet = " ".join(reply.split())[:80]
        print(format_row(name, spec["model"], latency_ms, snippet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
