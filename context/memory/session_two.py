"""The transcript is disposable. The note is not.

Session one runs, saves its whole transcript, and writes down the one fact that
mattered. Then the transcript is deleted on purpose. Session two starts with two
files off disk, AGENTS.md and the log block of notes.md, and answers a question
about session one anyway.

Two readers run side by side here. The old one takes the first path it finds and
never looks at the question. The new one takes the question's needle with it.
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
NEEDLE = "day 18"
TRANSCRIPT = Path("context/runs/day18_session_one.json")
KIND = "artifact path"
NOTE_LINE = "context/runs/day18_session_one.json holds the day 18 session one run"
WRITTEN_LINE = KIND + ": " + NOTE_LINE


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
    if WRITTEN_LINE in read_notes():
        return {"written": False, "reason": "already noted"}
    return write_note(KIND, NOTE_LINE, source="context/memory/session_two.py")


def throw_away():
    """Delete the transcript and report back whether it is really gone."""
    if TRANSCRIPT.exists():
        TRANSCRIPT.unlink()
    return TRANSCRIPT.exists()


def answer_about(scope, needle):
    """First line that names a run artifact AND carries the needle of the question."""
    for chunk in scope:
        for line in chunk.splitlines():
            if needle not in line:
                continue
            for word in line.split():
                if "context/runs/" in word and word.endswith(".json"):
                    return line.strip()
    return "unknown"


def session_two():
    """A fresh reader. Two chunks off disk. No transcript, no hops, no history."""
    scope = [
        (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"),
        read_notes(),
    ]
    return answer(scope), answer_about(scope, NEEDLE)


if __name__ == "__main__":
    note = session_one()
    transcript_exists = throw_away()
    first_path_line, recovered_line = session_two()
    print(
        json.dumps(
            {
                "question": QUESTION,
                "note": note,
                "transcript_path": str(TRANSCRIPT).replace("\\", "/"),
                "transcript_exists": transcript_exists,
                "sources": ["AGENTS.md", "context/memory/notes.md"],
                "first_path_line": first_path_line,
                "answer": recovered_line,
                "recovered": transcript_exists is False and recovered_line == WRITTEN_LINE,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
