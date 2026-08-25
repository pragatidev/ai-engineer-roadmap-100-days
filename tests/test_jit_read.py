"""The rule file in context/jit_read.py. Offline, no model call, no file read."""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module():
    spec = importlib.util.spec_from_file_location(
        "jit_read", REPO_ROOT / "context" / "jit_read.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_rule_is_stated_once_and_plainly():
    module = load_module()
    assert module.RULE == "Read a file when the task names it, not before."
    assert module.RULE in module.__doc__
    assert len(module.THE_TEST) == 2


def test_decide_answers_both_questions():
    module = load_module()
    # Small, fixed, needed every turn: pay once.
    assert module.decide(True, True) == module.PRELOAD
    assert module.decide(False, True) == module.PRELOAD
    # The task names it, this turn: read it now.
    assert module.decide(True, False) == module.JIT
    # The task does not name it: the strongest signal not to load it.
    assert module.decide(False, False) == module.JIT


def test_explain_says_why_not_just_what():
    module = load_module()
    assert module.explain(True, True) == "preload: every turn needs it, so pay once"
    assert module.explain(True, False) == (
        "just in time: the task names it, so read it now"
    )
    assert module.explain(False, False) == (
        "just in time: the task does not name it, so do not read it"
    )


def test_the_map_carries_identifiers_never_bodies():
    module = load_module()
    assert len(module.MAP) == 5
    for path, line in module.MAP.items():
        assert (REPO_ROOT / path).is_file()
        # A one line pointer, not a pasted body.
        assert "\n" not in line
        assert len(line) < 60


def test_named_file_finds_the_path_the_task_mentions():
    module = load_module()
    task = "Read context/README.md and tell me what the attention budget is."
    assert module.named_file(task) == "context/README.md"
    assert module.named_file("What is 41 times 17?") is None


def test_jit_read_reads_only_the_named_file():
    module = load_module()
    result = module.jit_read(
        "Read context/README.md and tell me what the attention budget is."
    )
    assert result["named"] == "context/README.md"
    assert result["read"] == "context/README.md"
    assert result["chars"] > 0
    assert result["tokens_approx"] == result["chars"] // 4
    assert "context/README.md" not in result["skipped"]
    assert len(result["skipped"]) == 4


def test_no_file_named_means_no_disk_touched():
    module = load_module()
    result = module.jit_read("What is 41 times 17?")
    assert result["named"] is None
    assert result["read"] is None
    assert result["chars"] == 0
    assert result["tokens_approx"] == 0
    assert result["skipped"] == sorted(module.MAP)


def test_preload_all_costs_more_than_any_single_read():
    module = load_module()
    whole = module.preload_all()
    one = module.jit_read(
        "Read context/README.md and tell me what the attention budget is."
    )
    assert whole["chars"] > one["chars"]
    assert whole["tokens_approx"] == whole["chars"] // 4


TASK = "Read context/README.md and tell me what the attention budget is."


def test_compare_measures_both_sides_of_the_same_task():
    module = load_module()
    payload = module.compare(TASK)
    assert payload["task"] == TASK
    assert payload["jit_named"] == "context/README.md"
    # Same counting rule on both sides: characters divided by four.
    assert payload["preload_tokens"] == payload["preload_chars"] // 4
    assert payload["jit_tokens"] == payload["jit_chars"] // 4
    # Same five files in play; the just in time side skipped the other four.
    assert len(payload["skipped"]) == len(module.MAP) - 1
    assert "context/README.md" not in payload["skipped"]
    # The gap is a subtraction, not a claim.
    assert payload["saved_tokens"] == (
        payload["preload_tokens"] - payload["jit_tokens"]
    )
    assert payload["saved_tokens"] > 0


def test_append_counts_adds_two_sections_and_keeps_what_was_there(tmp_path, monkeypatch):
    module = load_module()
    page = tmp_path / "context" / "token_counts.md"
    page.parent.mkdir(parents=True)
    page.write_text("# Token counts\n\n## Before\n\nchars: 20\n", encoding="utf-8")
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

    module.append_counts(module.compare(TASK))
    written = page.read_text(encoding="utf-8")

    # Append mode: the earlier count is still there.
    assert written.startswith("# Token counts\n\n## Before\n\nchars: 20\n")
    assert "## Preloaded" in written
    assert "job: dump" in written
    assert "## Just in time" in written
    assert "job: read on demand" in written
    assert "named: context/README.md" in written
    assert "task: " + TASK in written
