"""The notes are only worth writing if a later step can still answer from them."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from context.compaction import LINE, maybe_compact, thread_blob, tokens_approx
from context.memory.write_note import NOTES

QUESTION = "Where did the day 16 run write its artifact?"


def read_notes():
    """Hand back the log block of NOTES. No log yet is a normal state, not a crash."""
    path = NOTES if NOTES.is_absolute() else REPO_ROOT / NOTES
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if "## Log" not in text:
        return ""
    return text.split("## Log", 1)[1].strip()


def answer(scope):
    """First line in scope that names a path under context/runs ending in .json."""
    for chunk in scope:
        for line in chunk.splitlines():
            for word in line.split():
                if "context/runs/" in word and word.endswith(".json"):
                    return line.strip()
    return "unknown"


def chunks(thread):
    """The text a reader can actually see right now, one chunk per slot."""
    return [str(value) for value in thread.values()]


def thread_with_artifact(goal):
    """An ordinary mid task thread whose artifact path rides in a dropped slot."""
    loop_body = (REPO_ROOT / "scratch_agent" / "loop.py").read_text(encoding="utf-8")
    return {
        "instructions": (
            "Reply with one JSON object only. No markdown. No other text. "
            "The tools are multiply and read_file."
        ),
        "tool names": "multiply, read_file",
        "current goal": goal,
        "recent working set": "call_tool read_file scratch_agent/README.md",
        "used tool results": (
            "read_file scratch_agent/README.md returned the loop notes\n"
            "wrote the run payload to context/runs/day16_note_run.json\n"
            "exit ok"
        ),
        "superseded reasoning": (
            "The quiet question was 41 times 17. That is not the current goal."
        ),
        "duplicate file bodies": loop_body + "\n" + loop_body,
    }


if __name__ == "__main__":
    thread = thread_with_artifact("What is 347 times 19?")
    tokens_before = tokens_approx(thread_blob(thread))
    before = answer(chunks(thread))
    kept, _ = maybe_compact(thread)
    tokens_after = tokens_approx(thread_blob(kept))
    after = answer(chunks(kept))
    after_with_notes = answer(chunks(kept) + [read_notes()])
    print(
        json.dumps(
            {
                "question": QUESTION,
                "line": LINE,
                "tokens_before": tokens_before,
                "tokens_after": tokens_after,
                "before": before,
                "after": after,
                "after_with_notes": after_with_notes,
                "recovered": after == "unknown" and after_with_notes != "unknown",
            },
            indent=2,
            ensure_ascii=False,
        )
    )
