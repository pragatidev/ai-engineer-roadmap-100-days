"""context/session_vs_harness.md. The doc is a judgement call, so the shape is checked.

Two durable entries, four disposable, and a two line test. Every path that is
supposed to be on disk is on disk. The one path that is not checked for existence
is the transcript, because the lab deletes it on purpose every run.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC = REPO_ROOT / "context" / "session_vs_harness.md"

FIRST_LINE = "You can recreate the harness. You cannot recreate a lost fact."
THROWN_AWAY = "context/runs/day18_session_one.json"


def sections():
    """Map each '## Heading' to its non empty body lines, in file order."""
    out = {}
    current = None
    for raw in DOC.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            current = line[3:]
            out[current] = []
        elif line and current is not None:
            out[current].append(line)
    return out


def entries(body):
    """Body lines pair up as path then reason, so the paths are every other line."""
    return [body[i] for i in range(0, len(body), 2)]


def test_the_heading_and_the_first_line_of_body():
    lines = [line.strip() for line in DOC.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines[0] == "# Session versus harness"
    assert lines[1] == FIRST_LINE


def test_the_three_sections_are_present_and_in_order():
    assert list(sections()) == ["Durable", "Disposable", "Test"]


def test_durable_is_exactly_two_entries_each_with_a_reason():
    body = sections()["Durable"]
    assert len(body) == 4
    assert entries(body) == ["context/memory/notes.md", "AGENTS.md"]


def test_disposable_is_exactly_four_entries_each_with_a_reason():
    body = sections()["Disposable"]
    assert len(body) == 8
    assert entries(body) == [
        "context/memory/recover.py",
        "context/memory/write_note.py",
        "context/memory/session_two.py",
        THROWN_AWAY,
    ]


def test_every_reason_is_one_line_of_prose_not_a_path():
    body = sections()["Durable"] + sections()["Disposable"]
    reasons = [body[i] for i in range(1, len(body), 2)]
    assert len(reasons) == 6
    for reason in reasons:
        assert " " in reason
        assert not reason.endswith(".py")
        assert not reason.endswith(".md")
        assert not reason.endswith(".json")


def test_the_test_section_is_exactly_two_lines():
    assert sections()["Test"] == [
        "Delete it and ask what command brings it back.",
        "If a command brings it back it is disposable.",
    ]


def test_every_listed_path_is_real_except_the_one_we_throw_away():
    body = sections()["Durable"] + sections()["Disposable"]
    for path in entries(body):
        if path == THROWN_AWAY:
            continue
        assert (REPO_ROOT / path).is_file(), path
