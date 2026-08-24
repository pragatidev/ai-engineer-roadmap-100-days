"""The gate in context/memory/write_note.py. Offline, no model call, no real notes.md."""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module():
    spec = importlib.util.spec_from_file_location(
        "write_note", REPO_ROOT / "context" / "memory" / "write_note.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_kinds_match_the_may_write_list():
    module = load_module()
    notes = (REPO_ROOT / "context" / "memory" / "notes.md").read_text(encoding="utf-8")
    listed = notes.split("## May write", 1)[1].split("##", 1)[0]
    listed = [line.strip() for line in listed.splitlines() if line.strip()]
    assert listed == list(module.KINDS)


def test_check_refuses_and_allows():
    module = load_module()
    assert module.check("tool output", "hi", None) == "unknown kind"
    assert module.check("artifact path", "x" * 201, None) == "too long, that is a log"
    assert module.check("artifact path", "a\nb", None) == "multiple lines, that is a log"
    assert module.check("discovered fact that cost work", "httpx retries once", None) == "no source"
    assert module.check("discovered fact that cost work", "httpx retries once", "reason.py") is None
    assert module.check("artifact path", "context/runs/x.json holds the run", None) is None


def test_write_note_refuses_without_touching_the_file(tmp_path):
    module = load_module()
    target = tmp_path / "notes.md"
    target.write_text("# Notes\n", encoding="utf-8")
    module.NOTES = target
    assert module.write_note("tool output", "6593") == {
        "written": False,
        "reason": "unknown kind",
    }
    assert target.read_text(encoding="utf-8") == "# Notes\n"


def test_write_note_appends_once_under_one_log_heading(tmp_path):
    module = load_module()
    target = tmp_path / "notes.md"
    target.write_text("# Notes\n", encoding="utf-8")
    module.NOTES = target
    first = module.write_note("artifact path", "context/runs/a.json holds it", source="w.py")
    second = module.write_note("current goal and state", "gate is wired")
    written = target.read_text(encoding="utf-8")
    assert first["written"] is True
    assert second["written"] is True
    assert written.count("## Log") == 1
    assert "artifact path: context/runs/a.json holds it" in written
    assert "source: w.py" in written
    assert "current goal and state: gate is wired" in written
