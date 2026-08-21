"""One reason call returns a typed Action, not a chat reply. Plain Python. No LangChain."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engines.config import configured_engines, resolve_engine
from scratch_agent.actions import Action, CallTool, Stop

SCHEMA = (
    "Reply with one JSON object only. No markdown. No other text. "
    "Two objects are legal: "
    '{"kind": "call_tool", "name": "<tool name>", "arguments": {<name to value>}} '
    'or {"kind": "stop", "answer": "<the answer you would show a person>"}. '
    "The only tool is multiply. It takes numbers a and b. "
    "If the user asks to multiply, return call_tool, not the product."
)

NO_ENGINE = (
    "No engine is configured. Copy .env.example to .env and set one API key, "
    "or start Ollama, then run this again."
)


def action_from_model_text(text: str) -> Action:
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("model reply is not a JSON object")
    kind = payload.get("kind")
    if kind is None:
        raise ValueError("missing kind")
    if kind == "call_tool":
        return CallTool(name=payload["name"], arguments=payload["arguments"])
    if kind == "stop":
        return Stop(answer=payload["answer"])
    raise ValueError(f"unknown kind: {kind}")


def _chat(spec: dict, question: str) -> str:
    url = spec["base_url"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {spec['api_key']}",
        "Content-Type": "application/json",
    }
    headers.update(spec.get("headers") or {})
    body = {
        "model": spec["model"],
        "messages": [
            {"role": "system", "content": SCHEMA},
            {"role": "user", "content": question},
        ],
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
    content = data["choices"][0]["message"].get("content")
    return content if isinstance(content, str) else ""


def reason(question: str) -> Action:
    names = configured_engines()
    if not names:
        raise RuntimeError(NO_ENGINE)
    spec = resolve_engine(names[0])
    reply = _chat(spec, question)
    return action_from_model_text(reply)


if __name__ == "__main__":
    print(reason("What is 347 times 19?"))
