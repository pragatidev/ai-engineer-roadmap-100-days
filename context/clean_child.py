"""A child starts clean and gets a brief, not a trace.

The parent holds the writer trace. The child is a nested call with a fresh message list. The child never receives the trace.

This file does not rewrite isolation.md. Isolation already named the rule.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.actions import CallTool, Stop
from scratch_agent.loop import loop

ARTIFACT = Path(__file__).resolve().parent / "runs" / "clean_child.json"

NEEDLES = (
    "What is 347 times 19?",
    "6593",
    "full writer trace",
    "seen: 6593",
    "That is not the current goal.",
)


def make_brief():
    return {
        "job": "What is 41 times 17?",
        "constraint that must hold": "A child starts clean and gets a brief, not a trace.",
        "artifact path": "context/runs/clean_child.json",
    }


def make_parent_trace():
    return [
        {
            "role": "system",
            "content": "You are the writer. The tools are multiply and read_file.",
        },
        {
            "role": "user",
            "content": "What is 347 times 19?",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "kind": "call_tool",
                    "name": "multiply",
                    "arguments": {"a": 347, "b": 19},
                },
                ensure_ascii=False,
            ),
        },
        {
            "role": "user",
            "content": "seen: 6593",
        },
        {
            "role": "assistant",
            "content": "6593. The quiet question was 41 times 17. That is not the current goal.",
        },
        {
            "role": "user",
            "content": "Review this. Here is the full writer trace so you do not miss anything.",
        },
    ]


def brief_text(brief):
    return "\n".join(
        [
            "job: " + brief["job"],
            "constraint that must hold: " + brief["constraint that must hold"],
            "artifact path: " + brief["artifact path"],
        ]
    )


def hop_to_json(hop):
    if isinstance(hop, CallTool):
        return {"kind": "call_tool", "name": hop.name, "arguments": hop.arguments}
    if isinstance(hop, Stop):
        return {"kind": "stop", "answer": hop.answer}
    if isinstance(hop, dict) and hop.get("kind") == "error":
        return hop
    return {"kind": "seen", "value": hop}


def run_child(brief):
    """Nested call. Fresh message list. Brief only. No trace parameter."""
    messages = []
    messages.append({"role": "user", "content": brief_text(brief)})
    hops, coded = loop(brief["job"])
    last = hops[-1]
    answer = last.answer if isinstance(last, Stop) else None
    window = json.dumps(messages, ensure_ascii=False)
    return {
        "messages": messages,
        "hops": [hop_to_json(hop) for hop in hops],
        "stop_reason": coded,
        "answer": answer,
        "parent_trace_in_child": any(needle in window for needle in NEEDLES),
    }


if __name__ == "__main__":
    parent_messages = make_parent_trace()
    brief = make_brief()
    child = run_child(brief)
    parent_window = json.dumps(parent_messages, ensure_ascii=False)
    payload = {
        "job": brief["job"],
        "constraint that must hold": brief["constraint that must hold"],
        "artifact path": brief["artifact path"],
        "parent_messages": len(parent_messages),
        "child_messages": len(child["messages"]),
        "child_user_content": brief_text(brief),
        "parent_has_trace": all(needle in parent_window for needle in NEEDLES),
        "parent_trace_in_child": child["parent_trace_in_child"],
        "spent_tool_in_child": "6593"
        in json.dumps(child["messages"], ensure_ascii=False),
        "hops": child["hops"],
        "stop_reason": child["stop_reason"],
        "answer": child["answer"],
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("A child starts clean and gets a brief, not a trace.")
    print("parent_trace_in_child")
    print(payload["parent_trace_in_child"])
    print(json.dumps(payload, indent=2, ensure_ascii=False))
