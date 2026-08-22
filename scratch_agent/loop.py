"""Three hops and the loop that holds them. Plain Python. No LangChain."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.actions import CallTool, Stop
from scratch_agent.reason import decide, reason
from scratch_agent.registry import TOOLS


def pending(action):
    """Hop 2. Look the name up in TOOLS and call that worker."""
    worker = TOOLS[action.name]
    return worker(**action.arguments)


def loop(question):
    """Run reason, pending, then decide, in that order."""
    # Control flow to keep:
    # reason returns the next action.
    # If that action names a tool, look the name up in TOOLS and call the worker.
    # Pass what the worker returned into decide as seen.
    # If the action is stop, return the answer.
    action = reason(question)
    hops = [action]
    while isinstance(action, CallTool):
        seen = pending(action)
        hops.append(seen)
        action = decide(question, seen=seen)
        hops.append(action)
    return hops


def _hop_to_json(hop):
    if isinstance(hop, CallTool):
        return {"kind": "call_tool", "name": hop.name, "arguments": hop.arguments}
    if isinstance(hop, Stop):
        return {"kind": "stop", "answer": hop.answer}
    return {"kind": "seen", "value": hop}


if __name__ == "__main__":
    question = "What is 347 times 19?"
    hops = loop(question)
    serialized = [_hop_to_json(hop) for hop in hops]
    last = hops[-1]
    payload = {
        "question": question,
        "hops": serialized,
        "tool_ran": any(item["kind"] == "seen" for item in serialized),
        "answer": last.answer,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    runs_dir = Path(__file__).resolve().parent / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out = runs_dir / "first_success.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
