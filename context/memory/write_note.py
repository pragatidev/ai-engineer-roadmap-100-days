"""The write path for context/memory/notes.md.

Nothing else in this repo appends to that file. A line gets in only if it
qualifies, and when it does not, the gate says why and the caller keeps going.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.loop import _hop_to_json, loop

NOTES = Path("context/memory/notes.md")

KINDS = (
    "decision plus reason",
    "discovered fact that cost work",
    "current goal and state",
    "artifact path",
    "constraint that must hold",
)

LIMIT = 200


def check(kind, text, source=None):
    """Return None when the line qualifies, otherwise a short reason to refuse."""
    if kind not in KINDS:
        return "unknown kind"
    if len(text) > LIMIT:
        return "too long, that is a log"
    if "\n" in text:
        return "multiple lines, that is a log"
    if kind == "discovered fact that cost work" and not source:
        return "no source"
    return None


def write_note(kind, text, source=None):
    """Append one qualifying line to NOTES. A refusal is a return value, not a crash."""
    reason = check(kind, text, source)
    if reason is not None:
        return {"written": False, "reason": reason}
    existing = NOTES.read_text(encoding="utf-8") if NOTES.exists() else ""
    block = "" if "## Log" in existing else "\n## Log\n\n"
    line = kind + ": " + text
    block += line + "\n"
    if source:
        block += "source: " + source + "\n"
    with NOTES.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(block)
    return {"written": True, "line": line}


if __name__ == "__main__":
    question = "What is 347 times 19?"
    hops, coded = loop(question)
    serialized = [_hop_to_json(hop) for hop in hops]
    stops = [hop["answer"] for hop in serialized if hop["kind"] == "stop"]
    payload = {
        "question": question,
        "hops": serialized,
        "tool_ran": any(hop["kind"] == "seen" for hop in serialized),
        "stop_reason": coded,
        "answer": stops[-1] if stops else "",
    }
    run_path = Path("context/runs/day16_note_run.json")
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(write_note("tool output", payload["answer"]))
    print(write_note(
        "discovered fact that cost work",
        json.dumps(payload, indent=2, ensure_ascii=False),
    ))
    print(write_note(
        "artifact path",
        "context/runs/day16_note_run.json holds the day 16 run",
        source="context/memory/write_note.py",
    ))
