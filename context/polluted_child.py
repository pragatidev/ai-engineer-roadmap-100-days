"""Show a polluted-context miss. Same child shape as clean_child.py, except the child inherits the parent messages. A review that can see the writer's spent tool result will stamp that result.

This file does not rewrite isolation.md. This file does not rewrite clean_child.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from context.clean_child import NEEDLES, make_parent_trace, brief_text

ARTIFACT = Path(__file__).resolve().parent / "runs" / "polluted_child.json"


def make_brief():
    return {
        "job": "What is 41 times 17?",
        "constraint that must hold": "A child starts clean and gets a brief, not a trace.",
        "artifact path": "context/runs/polluted_child.json",
    }


def find_spent_seen(messages):
    for message in messages:
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str) and content.startswith("seen:"):
            return content.split(":", 1)[1].strip()
    return None


def run_child(parent_messages, brief):
    messages = list(parent_messages)
    messages.append({"role": "user", "content": brief_text(brief)})
    window = json.dumps(messages, ensure_ascii=False)
    spent = find_spent_seen(messages)
    leaked = ("seen: " + spent) if spent is not None else None
    return {
        "messages": messages,
        "answer": spent,
        "leaked": leaked,
        "parent_trace_in_child": any(needle in window for needle in NEEDLES),
        "spent_tool_in_child": spent is not None,
    }


if __name__ == "__main__":
    parent_messages = make_parent_trace()
    brief = make_brief()
    child = run_child(parent_messages, brief)
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
        "spent_tool_in_child": child["spent_tool_in_child"],
        "leaked": child["leaked"],
        "answer": child["answer"],
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("The reviewer must not share the writer trace.")
    print("leaked")
    print(payload["leaked"])
    print(json.dumps(payload, indent=2, ensure_ascii=False))
