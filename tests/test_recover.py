"""The recovery proof in context/memory/recover.py. Offline, no model call, no network."""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module():
    spec = importlib.util.spec_from_file_location(
        "recover", REPO_ROOT / "context" / "memory" / "recover.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_answer_finds_an_artifact_path_and_otherwise_says_unknown():
    module = load_module()
    found = module.answer(["nothing here\nwrote it to context/runs/day16_note_run.json\ndone"])
    assert found == "wrote it to context/runs/day16_note_run.json"
    assert module.answer(["the goal is 347 times 19", "no path in this chunk"]) == "unknown"
    assert module.answer(["see context/runs/ for the copies"]) == "unknown"


def test_read_notes_returns_the_log_block_and_not_the_contract(tmp_path):
    module = load_module()
    target = tmp_path / "notes.md"
    target.write_text(
        "# Notes\n\n## May not write\n\nsecrets\n\n## Log\n\nartifact path: context/runs/a.json\n",
        encoding="utf-8",
    )
    module.NOTES = target
    log = module.read_notes()
    assert log == "artifact path: context/runs/a.json"
    assert "secrets" not in log


def test_read_notes_is_empty_when_there_is_no_log_heading(tmp_path):
    module = load_module()
    target = tmp_path / "notes.md"
    target.write_text("# Notes\n\n## May write\n\nartifact path\n", encoding="utf-8")
    module.NOTES = target
    assert module.read_notes() == ""


def test_the_cut_loses_the_path_and_the_log_block_gives_it_back(tmp_path):
    module = load_module()
    target = tmp_path / "notes.md"
    target.write_text(
        "# Notes\n\n## Log\n\nartifact path: context/runs/day16_note_run.json holds the day 16 run\n",
        encoding="utf-8",
    )
    module.NOTES = target
    thread = module.thread_with_artifact("What is 347 times 19?")
    assert module.tokens_approx(module.thread_blob(thread)) > module.LINE
    kept, did_cut = module.maybe_compact(thread)
    assert did_cut is True
    assert module.answer(module.chunks(thread)) != "unknown"
    assert module.answer(module.chunks(kept)) == "unknown"
    assert module.answer(module.chunks(kept) + [module.read_notes()]) != "unknown"


def test_the_kept_slots_are_the_keep_list_plus_lives():
    module = load_module()
    kept, _ = module.maybe_compact(module.thread_with_artifact("What is 347 times 19?"))
    assert "used tool results" not in kept
    assert "duplicate file bodies" not in kept
    assert kept["current goal"] == "What is 347 times 19?"
