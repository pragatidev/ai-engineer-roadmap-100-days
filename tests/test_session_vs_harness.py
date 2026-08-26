"""context/session_vs_harness.md. The doc is a judgement call, so the shape is checked.

The file sorts every path in this repo with one question: if it disappeared right
now, what command brings it back? Three answers, so three sections, in this order.
The harness, which git checkout hands back. The transcript, which nothing hands
back and which cost nothing. The unwritten line, which nothing hands back and
which is the whole risk.

Every path listed under the first two headings is checked for real existence, with
one exception: the transcript, because the lab deletes it on purpose every run.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC = REPO_ROOT / "context" / "session_vs_harness.md"

TITLE = "# Session versus harness"
BODY_ONE = "One question sorts every file in this repo."
BODY_TWO = "If it disappeared right now, what command brings it back?"

RECOVERABLE = "A command brings it back"
FINE = "No command brings it back, and that is fine"
RISK = "No command brings it back, and that is the whole risk"

THROWN_AWAY = "context/runs/day18_session_one.json"
UNWRITTEN = "the next line under ## Log in context/memory/notes.md"

HARNESS = [
    "AGENTS.md",
    "context/memory/write_note.py",
    "context/memory/recover.py",
    "context/memory/session_two.py",
    "context/compaction.py",
]


def lines():
    """Every non empty line of the doc, stripped, in file order."""
    return [raw.strip() for raw in DOC.read_text(encoding="utf-8").splitlines() if raw.strip()]


def sections():
    """Map each '## Heading' to its non empty body lines, in file order.

    A body line may mention '## Log' mid sentence; only a line that starts with
    '## ' opens a section, so that mention stays body text where it belongs.
    """
    out = {}
    current = None
    for line in lines():
        if line.startswith("## "):
            current = line[3:]
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return out


def split(body):
    """Split a section body into its listed items and the reason prose under them.

    An item is a bare path or the one named thing that has no path. A reason is a
    sentence, so it ends in a full stop.
    """
    items = []
    for line in body:
        if line.endswith("."):
            break
        items.append(line)
    return items, body[len(items):]


def test_the_title_and_the_two_body_lines():
    assert lines()[:3] == [TITLE, BODY_ONE, BODY_TWO]


def test_the_three_sections_are_present_and_in_order():
    assert list(sections()) == [RECOVERABLE, FINE, RISK]


def test_the_harness_section_lists_five_files_then_gives_the_command():
    items, reasons = split(sections()[RECOVERABLE])
    assert items == HARNESS
    assert reasons == [
        "git checkout -- <path>. These are source, they are committed, and git holds a copy.",
        "Losing one costs the seconds it takes to type the command.",
    ]


def test_the_transcript_is_the_only_entry_that_did_not_matter():
    items, reasons = split(sections()[FINE])
    assert items == [THROWN_AWAY]
    assert len(reasons) == 2
    assert "git cannot return it" in reasons[0]
    assert "context/memory/notes.md before the delete" in reasons[1]


def test_the_risk_section_names_the_unwritten_line_and_the_write_step():
    items, reasons = split(sections()[RISK])
    assert items == [UNWRITTEN]
    assert len(reasons) == 4
    assert "have not written down yet" in reasons[0]
    assert "nothing is holding a copy" in reasons[1]
    assert "write_note.py wrote them" in reasons[2]
    assert reasons[3].startswith("That write step is the durable half.")


def test_every_reason_is_prose_and_not_a_bare_path():
    for heading in (RECOVERABLE, FINE, RISK):
        _, reasons = split(sections()[heading])
        for reason in reasons:
            assert " " in reason
            assert reason.endswith(".")
            assert not reason.split()[-1].endswith((".py", ".json"))


def test_every_listed_file_is_real_except_the_one_we_throw_away():
    for path in HARNESS:
        assert (REPO_ROOT / path).is_file(), path
    assert not (REPO_ROOT / THROWN_AWAY).exists()


def test_the_unwritten_line_points_at_a_notes_file_that_really_has_a_log():
    notes = (REPO_ROOT / "context" / "memory" / "notes.md").read_text(encoding="utf-8")
    assert "## Log" in notes
