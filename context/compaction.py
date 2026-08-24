"""Compaction is a designed cut, not a hand summary in chat.

The model can write the sentences. The rule is yours.
When tokens cross a line, compact.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.actions import Stop
from scratch_agent.loop import loop
from scratch_agent.registry import TOOLS

# KEEP: survives the cut because the next hop still needs it.
KEEP = [
    "instructions",
    "tool names",
    "current goal",
    "recent working set",
]

# DROP: spent tokens that crowd the attention budget.
DROP = [
    "used tool results",
    "superseded reasoning",
    "duplicate file bodies",
]

# LIVES: the dense copy after the cut.
LIVES = (
    "one conversation message in the slot of the dropped turns; "
    "optional copy under context/runs"
)

LINE = 500


def tokens_approx(text):
    return len(text) // 4


def thread_blob(thread):
    return json.dumps(thread, ensure_ascii=False)


def mid_task_thread(question):
    readme = TOOLS["read_file"]("scratch_agent/README.md")
    loop_body = (REPO_ROOT / "scratch_agent" / "loop.py").read_text(encoding="utf-8")
    reason_body = (REPO_ROOT / "scratch_agent" / "reason.py").read_text(encoding="utf-8")
    return {
        "instructions": (
            "Reply with one JSON object only. No markdown. No other text. "
            "The tools are multiply and read_file."
        ),
        "tool names": sorted(TOOLS.keys()),
        "current goal": question,
        "recent working set": [
            {
                "kind": "call_tool",
                "name": "read_file",
                "arguments": {"path": "scratch_agent/README.md"},
            }
        ],
        "used tool results": readme,
        "superseded reasoning": (
            "The quiet question was 41 times 17. That is not the current goal."
        ),
        "duplicate file bodies": (
            loop_body + "\n" + loop_body + "\n" + reason_body + "\n" + reason_body
        ),
    }


def compact(thread):
    compacted = {name: thread[name] for name in KEEP}
    compacted["lives"] = LIVES
    runs = Path(__file__).resolve().parent / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "lives.json").write_text(
        json.dumps({"lives": LIVES}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return compacted


def maybe_compact(thread):
    if tokens_approx(thread_blob(thread)) <= LINE:
        return thread, False
    return compact(thread), True


def strip_compare(text):
    marker = "## Uncompacted"
    idx = text.find(marker)
    if idx < 0:
        return text
    kept = text[:idx].rstrip() + "\n"
    return kept


def append_counts(chars_before, tokens_before, chars_after, tokens_after, goal):
    page = REPO_ROOT / "context" / "token_counts.md"
    existing = strip_compare(page.read_text(encoding="utf-8"))
    if not existing.endswith("\n"):
        existing += "\n"
    block = (
        "\n## Uncompacted\n\n"
        "chars: %s\n"
        "tokens_approx: %s\n"
        "\n## Compacted\n\n"
        "chars: %s\n"
        "tokens_approx: %s\n"
        "line: %s\n"
        "goal: %s\n"
    ) % (
        chars_before,
        tokens_before,
        chars_after,
        tokens_after,
        LINE,
        goal,
    )
    page.write_text(existing + block, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    print("KEEP")
    for item in KEEP:
        print(item)
    print("DROP")
    for item in DROP:
        print(item)
    print("LIVES")
    print(LIVES)
    question = "What is 347 times 19?"
    thread = mid_task_thread(question)
    blob_before = thread_blob(thread)
    chars_before = len(blob_before)
    before = tokens_approx(blob_before)
    thread, did_cut = maybe_compact(thread)
    blob_after = thread_blob(thread)
    chars_after = len(blob_after)
    after = tokens_approx(blob_after)
    print(
        json.dumps(
            {
                "line": LINE,
                "chars_before": chars_before,
                "tokens_before": before,
                "chars_after": chars_after,
                "tokens_after": after,
                "compacted": did_cut,
                "keep_present": [name for name in KEEP if name in thread],
                "drop_present": [name for name in DROP if name in thread],
                "lives_in_slot": "lives" in thread,
                "current goal": thread.get("current goal"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    hops, coded = loop(thread["current goal"])
    last = hops[-1]
    continued = {"stop_reason": coded}
    if isinstance(last, Stop):
        continued["answer"] = last.answer
    print(json.dumps(continued, indent=2, ensure_ascii=False))
    append_counts(chars_before, before, chars_after, after, question)

