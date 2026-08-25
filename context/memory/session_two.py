"""The transcript is gone. The note is not.

Session one runs, writes down the one fact that mattered, and saves its whole
transcript. Then the transcript is deleted on purpose. Session two starts with
two files off disk, AGENTS.md and the log block of notes.md, and answers a
question about session one anyway.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.loop import _hop_to_json, loop
from context.memory.recover import answer, read_notes
from context.memory.write_note import NOTES, write_note

QUESTION = "Where did the day 18 run write its artifact?"
TRANSCRIPT = Path("context/runs/day18_session_one.json")
NOTE_LINE = "context/runs/day18_session_one.json holds the day 18 session one run"


def session_one():
    """Run the loop, save the whole transcript, then write the one durable line."""
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
    TRANSCRIPT.parent.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if NOTE_LINE in read_notes():
        return {"written": False, "reason": "already noted"}
    return write_note(
        "artifact path",
        NOTE_LINE,
        source="context/memory/session_two.py",
    )


def throw_away():
    """Delete the transcript and report back whether it is really gone."""
    if TRANSCRIPT.exists():
        TRANSCRIPT.unlink()
    return TRANSCRIPT.exists()


def session_two():
    """A fresh reader. Two chunks off disk. No transcript, no hops, no history."""
    scope = [
        (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"),
        read_notes(),
    ]
    return answer(scope)


if __name__ == "__main__":
    note = session_one()
    transcript_exists = throw_away()
    recovered_line = session_two()
    print(
        json.dumps(
            {
                "question": QUESTION,
                "note": note,
                "transcript_path": str(TRANSCRIPT).replace("\\", "/"),
                "transcript_exists": transcript_exists,
                "sources": ["AGENTS.md", "context/memory/notes.md"],
                "answer": recovered_line,
                "recovered": transcript_exists is False and recovered_line != "unknown",
            },
            indent=2,
            ensure_ascii=False,
        )
    )
