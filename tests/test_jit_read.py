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


def test_the_rule_file_wires_no_tool_yet():
    source = (REPO_ROOT / "context" / "jit_read.py").read_text(encoding="utf-8")
    for wiring in ("open(", "read_text(", "TOOLS", "import requests"):
        assert wiring not in source
