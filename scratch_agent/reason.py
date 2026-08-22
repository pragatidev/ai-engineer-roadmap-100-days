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
    "The tools are multiply and divide. Each takes numbers a and b. "
    "If the user asks to multiply or divide, return call_tool, not the result."
)

DECIDE_SCHEMA = (
    "Reply with one JSON object only. No markdown. No other text. "
    "Two objects are legal: "
    '{"kind": "call_tool", "name": "<tool name>", "arguments": {<name to value>}} '
    'or {"kind": "stop", "answer": "<the answer you would show a person>"}. '
    "The user message includes seen: the tool result. "
    "If seen answers the question, return stop with that answer. "
    "Do not call the same tool again for a result you already have."
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


def _chat(spec: dict, question: str, seen=None) -> str:
    url = spec["base_url"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {spec['api_key']}",
        "Content-Type": "application/json",
    }
    headers.update(spec.get("headers") or {})
    if seen is None:
        user_content = question
    else:
        user_content = (
            question + "\n" + "seen: " + json.dumps(seen, ensure_ascii=False)
        )
    system_content = SCHEMA if seen is None else DECIDE_SCHEMA
    body = {
        "model": spec["model"],
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
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


def decide(question, seen):
    names = configured_engines()
    if not names:
        raise RuntimeError(NO_ENGINE)
    spec = resolve_engine(names[0])
    reply = _chat(spec, question, seen)
    return action_from_model_text(reply)


if __name__ == "__main__":
    question = "What is 347 times 19?"
    action = reason(question)
    print(action)
    if isinstance(action, CallTool):
        logged = {
            "kind": "call_tool",
            "name": action.name,
            "arguments": action.arguments,
        }
    elif isinstance(action, Stop):
        logged = {"kind": "stop", "answer": action.answer}
    else:
        raise TypeError(f"unexpected action type: {type(action)!r}")
    payload = {
        "question": question,
        "action": logged,
        "tool_ran": False,
        "note": "no tool ran because this folder has no tool yet",
    }
    runs_dir = Path(__file__).resolve().parent / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out = runs_dir / "reason_only_fail.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

