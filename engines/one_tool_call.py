"""One structured function call. The model may request multiply. Python runs it once, or refuses. No loop."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engines.config import configured_engines, resolve_engine

PROMPT = "What is 347 times 19? Use the multiply tool."
NO_ENGINE = (
    "No engine is configured. Copy .env.example to .env and set one API key, "
    "or start Ollama, then run this again."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        },
    }
]


def multiply(a: float, b: float) -> float:
    return a * b


FUNCTIONS = {
    "multiply": multiply,
}


# MODEL CALL. You ask. You send a tools list. The model may reply with a function request.
def chat_with_tools(spec: dict, prompt: str) -> dict:
    url = spec["base_url"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {spec['api_key']}",
        "Content-Type": "application/json",
    }
    headers.update(spec.get("headers") or {})
    body = {
        "model": spec["model"],
        "messages": [{"role": "user", "content": prompt}],
        "tools": TOOLS,
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
    return data["choices"][0]["message"]


# RUN ONCE. Look up the function. Run it, or refuse. Do not send the product back.
def run_once(message: dict) -> str:
    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        return "refused: no tool request"
    call = tool_calls[0]
    name = call["function"]["name"]
    fn = FUNCTIONS.get(name)
    if fn is None:
        return f"refused: unknown function {name}"
    args = json.loads(call["function"]["arguments"])
    return str(fn(args["a"], args["b"]))


# HARNESS. Pick an engine, print the tool request and the tool result, stop. No second decide.
def main() -> int:
    names = configured_engines()
    if not names:
        print(NO_ENGINE)
        return 0

    name = names[0]
    spec = resolve_engine(name)
    message = chat_with_tools(spec, PROMPT)
    tool_calls = message.get("tool_calls") or []
    if tool_calls:
        call = tool_calls[0]["function"]
        request_text = f"{call['name']} {call['arguments']}"
    else:
        request_text = "none"
    result = run_once(message)
    print(f"{name} | {spec['model']} | {request_text} | {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
