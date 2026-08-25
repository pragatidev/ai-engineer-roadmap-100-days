"""context/memory/session_two.py. Offline, no model call, no real notes.md, no real transcript."""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module():
    spec = importlib.util.spec_from_file_location(
        "session_two", REPO_ROOT / "context" / "memory" / "session_two.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_throw_away_deletes_and_reports_it_is_gone(tmp_path):
    module = load_module()
    target = tmp_path / "day18_session_one.json"
    target.write_text("{}\n", encoding="utf-8")
    module.TRANSCRIPT = target
    assert module.throw_away() is False
    assert target.exists() is False


def test_throw_away_is_safe_when_there_is_nothing_to_delete(tmp_path):
    module = load_module()
    module.TRANSCRIPT = tmp_path / "never_written.json"
    assert module.throw_away() is False


def scripted_loop(module):
    """A session one that never leaves the machine. Same shape the real loop returns."""
    from scratch_agent.actions import CallTool, Stop

    def fake(question, max_steps=8):
        hops = [
            CallTool(name="multiply", arguments={"a": 347, "b": 19}),
            6593,
            Stop(answer="6593"),
        ]
        return hops, "done"

    module.loop = fake


def test_session_one_writes_the_transcript_then_the_one_line(tmp_path):
    module = load_module()
    scripted_loop(module)
    module.TRANSCRIPT = tmp_path / "day18_session_one.json"
    module.read_notes = lambda: ""
    written = []
    module.write_note = lambda kind, text, source=None: written.append(
        (kind, text, source)
    ) or {"written": True, "line": kind + ": " + text}
    result = module.session_one()
    payload = module.TRANSCRIPT.read_text(encoding="utf-8")
    assert '"answer": "6593"' in payload
    assert '"hops"' in payload
    assert result["written"] is True
    assert written == [
        ("artifact path", module.NOTE_LINE, "context/memory/session_two.py")
    ]


def test_session_one_does_not_write_the_same_line_twice(tmp_path):
    module = load_module()
    scripted_loop(module)
    module.TRANSCRIPT = tmp_path / "day18_session_one.json"
    module.read_notes = lambda: module.WRITTEN_LINE
    module.write_note = lambda *a, **k: pytest.fail("the guard let a duplicate through")
    assert module.session_one() == {"written": False, "reason": "already noted"}
    assert module.TRANSCRIPT.exists() is True


def test_session_two_sees_exactly_two_chunks_and_no_transcript(tmp_path):
    module = load_module()
    seen = []

    def spy(scope):
        seen.append(list(scope))
        return "unknown"

    module.answer = spy
    module.read_notes = lambda: "artifact path: context/runs/day18_session_one.json holds it"
    module.session_two()
    assert len(seen[0]) == 2
    assert seen[0][0] == (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "context/runs/day18_session_one.json" in seen[0][1]
    assert "hops" not in seen[0][1]


def test_session_two_reads_the_line_back_out_of_the_log(tmp_path):
    module = load_module()
    module.read_notes = lambda: module.WRITTEN_LINE
    assert module.session_two() == (module.WRITTEN_LINE, module.WRITTEN_LINE)


DAY_16 = "artifact path: context/runs/day16_note_run.json holds the day 16 run"


def test_the_old_reader_answers_with_the_wrong_day_once_the_log_has_two(tmp_path):
    module = load_module()
    module.read_notes = lambda: DAY_16 + "\n" + module.WRITTEN_LINE
    first_path_line, recovered = module.session_two()
    assert first_path_line == DAY_16
    assert recovered == module.WRITTEN_LINE


def test_answer_about_refuses_a_path_line_that_does_not_carry_the_needle():
    module = load_module()
    assert module.answer_about([DAY_16], module.NEEDLE) == "unknown"


def test_answer_about_ignores_a_needle_line_with_no_run_artifact():
    module = load_module()
    assert module.answer_about(["the day 18 session went fine"], module.NEEDLE) == "unknown"
