"""Death driver. Stuff the scratch agent until a quiet question drowns."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CONTEXT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CONTEXT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.actions import CallTool, Stop
from scratch_agent.loop import loop

REPEAT_COUNT = 8
SHOUT_COUNT = 80
QUIET_QUESTION = "What is 41 times 17?"
EXPECTED = "697"
OLD_QUESTION = "What is 347 times 19?"
WAREHOUSE = [
    "scratch_agent/README.md",
    "scratch_agent/loop.py",
    "scratch_agent/reason.py",
    "scratch_agent/registry.py",
    "scratch_agent/actions.py",
]


def hop_to_json(hop):
    if isinstance(hop, CallTool):
        return {"kind": "call_tool", "name": hop.name, "arguments": hop.arguments}
    if isinstance(hop, Stop):
        return {"kind": "stop", "answer": hop.answer}
    if isinstance(hop, dict) and hop.get("kind") == "error":
        return hop
    return {"kind": "seen", "value": hop}


def load_warehouse() -> str:
    parts = []
    for rel in WAREHOUSE:
        body = (REPO_ROOT / rel).read_text(encoding="utf-8")
        parts.append("===== " + rel + " =====\n" + body)
    return "\n\n".join(parts)


def build_stuffed_question() -> str:
    bundle = load_warehouse()
    repeated = "\n\n".join([bundle] * REPEAT_COUNT)
    shout = (OLD_QUESTION + "\n") * SHOUT_COUNT
    hay = shout + "\n" + repeated + "\n" + shout
    mid = len(hay) // 2
    return hay[:mid] + "\n\n" + QUIET_QUESTION + "\n\n" + hay[mid:]


def main() -> None:
    stuffed = build_stuffed_question()
    hops, coded = loop(stuffed)
    serialized = [hop_to_json(hop) for hop in hops]
    payload = {
        "question": QUIET_QUESTION,
        "expected": EXPECTED,
        "hops": serialized,
        "stop_reason": coded,
        "warehouse": list(WAREHOUSE),
        "repeat_count": REPEAT_COUNT,
        "prompt_chars": len(stuffed),
    }
    last = hops[-1] if hops else None
    if isinstance(last, Stop):
        payload["answer"] = last.answer
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    print(text, end="")
    runs_dir = CONTEXT_DIR / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out = runs_dir / "rot_fail.json"
    out.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
