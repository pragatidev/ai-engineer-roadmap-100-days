"""Alive run. A long task with compact, notes, and a map. Not a short demo. Not a rerun of the stuffed death driver. Isolation is not a control on this receipt."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from context.compaction import KEEP, DROP, LINE, maybe_compact, thread_blob, tokens_approx
from context.memory.write_note import write_note
from scratch_agent.actions import CallTool, Stop
from scratch_agent.loop import loop
from scratch_agent.registry import TOOLS

QUESTION = "What is 41 times 17?"
EXPECTED = 697
MAP_PATH = "AGENTS.md"
ARTIFACT = Path("context/runs/alive.json")
CONTROLS = ["compact", "notes", "a map"]


def hop_to_json(hop):
    if isinstance(hop, CallTool):
        return {"kind": "call_tool", "name": hop.name, "arguments": hop.arguments}
    if isinstance(hop, Stop):
        return {"kind": "stop", "answer": hop.answer}
    if isinstance(hop, dict) and hop.get("kind") == "error":
        return hop
    return {"kind": "seen", "value": hop}


def long_thread(question):
    map_text = TOOLS["read_file"](MAP_PATH)
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
                "kind": "point",
                "path": MAP_PATH,
                "job": "point",
                "chars": len(map_text),
            }
        ],
        "used tool results": readme,
        "superseded reasoning": (
            "The old demo was 347 times 19. That is not the current goal."
        ),
        "duplicate file bodies": (
            loop_body + "\n" + loop_body + "\n" + reason_body + "\n" + reason_body
        ),
    }


def write_surviving_notes():
    return [
        write_note(
            "current goal and state",
            "quiet question What is 41 times 17? still in the window after the cut",
        ),
        write_note(
            "discovered fact that cost work",
            "AGENTS.md points at context/README.md and does not paste the law",
            source="AGENTS.md",
        ),
        write_note(
            "constraint that must hold",
            "one control is not a set; isolation is not the third name on this list",
        ),
        write_note(
            "decision plus reason",
            "write notes before maybe_compact so dropped results do not take the facts with them",
        ),
        write_note(
            "artifact path",
            "context/runs/alive.json holds the alive run",
            source="context/alive.py",
        ),
    ]


def main() -> None:
    thread = long_thread(QUESTION)
    blob_before = thread_blob(thread)
    chars_before = len(blob_before)
    tokens_before = tokens_approx(blob_before)
    note_rows = write_surviving_notes()
    notes_written = all(row.get("written") is True for row in note_rows)
    thread, did_cut = maybe_compact(thread)
    compacted = did_cut
    blob_after = thread_blob(thread)
    chars_after = len(blob_after)
    tokens_after = tokens_approx(blob_after)
    keep_present = [name for name in KEEP if name in thread]
    drop_present = [name for name in DROP if name in thread]
    lives_in_slot = "lives" in thread
    hops, coded = loop(thread["current goal"])
    serialized = [hop_to_json(hop) for hop in hops]
    last = hops[-1] if hops else None
    answer = last.answer if isinstance(last, Stop) else ""
    payload = {
        "question": QUESTION,
        "expected": EXPECTED,
        "answer": answer,
        "stop_reason": coded,
        "hops": serialized,
        "line": LINE,
        "chars_before": chars_before,
        "tokens_before": tokens_before,
        "chars_after": chars_after,
        "tokens_after": tokens_after,
        "compacted": compacted,
        "keep_present": keep_present,
        "drop_present": drop_present,
        "lives_in_slot": lives_in_slot,
        "notes_written": notes_written,
        "note_rows": note_rows,
        "map": MAP_PATH,
        "map_job": "point",
        "short_demo": False,
        "death_rerun": False,
        "controls": CONTROLS,
        "isolation_on_list": "isolation" in CONTROLS,
        "artifact path": ARTIFACT.as_posix(),
        "tool names": sorted(TOOLS.keys()),
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()
