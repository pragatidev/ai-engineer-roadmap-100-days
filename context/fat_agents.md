Fat AGENTS.md (comparison copy, not the live map)

## Setup

```bash
git clone https://github.com/pragatidev/ai-engineer-roadmap-100-days
cd ai-engineer-roadmap-100-days
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

On macOS or Linux, the first command is `python3 -m venv .venv`, and every command
after it uses `.venv/bin/python` in place of `.venv\Scripts\python`.

Copy the example env file and set at most one provider key. Or leave the keys
empty and start Ollama on the host below.

```bash
copy .env.example .env
.venv\Scripts\python scripts/smoke.py
```

# Scratch agent

Section 2 builds the reason, the tool, and the loop in plain Python. There is no LangChain in this folder.
LangChain waits until Section 10, a LangGraph tutorial of this same agent on a hireable stack.

The loop is done. The fail then pass pair is failing_run.json next to runs/day12_pass.json. Keep first_success.json and max_steps_run.json. TOOLS still has read_file and multiply. Do not add divide. write_file stays off TOOLS. loop.py does not import retry.py.

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
from scratch_agent.stop_rules import (
    stop_on_done,
    stop_on_max_steps,
    stop_on_repeated_tool_error,
)


def pending(action):
    """Hop 2. Look the name up in TOOLS and call that worker."""
    if action.name not in TOOLS:
        return {"kind": "error", "error": "unknown tool", "name": action.name}
    worker = TOOLS[action.name]
    return worker(**action.arguments)


def why_stop(hops, max_steps):
    """Ask the named rules. First string wins. None means keep going."""
    return (
        stop_on_done(hops)
        or stop_on_repeated_tool_error(hops)
        or stop_on_max_steps(hops, max_steps)
    )


def loop(question, max_steps=8):
    """Run reason, pending, then decide, and consult stop rules after every hop."""
    # Control flow to keep:
    # reason returns the next action.
    # If that action names a tool, look the name up in TOOLS and call the worker.
    # Pass what the worker returned into decide as seen.
    # If the action is stop, return the answer.
    # After every hop, ask why_stop. Leave with that string when it fires.
    action = reason(question)
    hops = [action]
    coded = why_stop(hops, max_steps)
    while coded is None and isinstance(action, CallTool):
        seen = pending(action)
        hops.append(seen)
        coded = why_stop(hops, max_steps)
        if coded is not None:
            break
        if isinstance(seen, dict) and seen.get("kind") == "error":
            break
        action = decide(question, seen=seen)
        hops.append(action)
        coded = why_stop(hops, max_steps)
    return hops, coded


def _hop_to_json(hop):
    if isinstance(hop, CallTool):
        return {"kind": "call_tool", "name": hop.name, "arguments": hop.arguments}
    if isinstance(hop, Stop):
        return {"kind": "stop", "answer": hop.answer}
    if isinstance(hop, dict) and hop.get("kind") == "error":
        return hop
    return {"kind": "seen", "value": hop}


if __name__ == "__main__":
    question = "What is 347 times 19?"
    hops, coded = loop(question)
    serialized = [_hop_to_json(hop) for hop in hops]
    payload = {
        "question": question,
        "hops": serialized,
        "tool_ran": any(item["kind"] == "seen" for item in serialized),
        "stop_reason": coded,
    }
    last = hops[-1]
    if isinstance(last, Stop):
        payload["answer"] = last.answer
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    runs_dir = Path(__file__).resolve().parent / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out = runs_dir / "day12_pass.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

# Context engineering

Context is a finite attention budget.

Every token in the window competes for attention. Bigger windows did not retire this job. They made stuffing more expensive.

This folder is section 3. Still plain Python. The stuffed context death run is not this file.
