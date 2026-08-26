"""context/clean_child.py. Offline, no model call, no nested loop."""

import importlib.util
import inspect
import json
from pathlib import Path

from scratch_agent.actions import CallTool, Stop

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module():
    spec = importlib.util.spec_from_file_location(
        "clean_child", REPO_ROOT / "context" / "clean_child.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_make_brief_matches_isolation_md():
    module = load_module()
    brief = module.make_brief()
    assert list(brief) == ["job", "constraint that must hold", "artifact path"]
    assert brief["job"] == "What is 41 times 17?"
    assert brief["constraint that must hold"] == (
        "A child starts clean and gets a brief, not a trace."
    )
    assert brief["artifact path"] == "context/runs/clean_child.json"
    isolation = (REPO_ROOT / "context" / "isolation.md").read_text(encoding="utf-8")
    for key in brief:
        assert key in isolation


def test_brief_text_is_three_labeled_lines():
    module = load_module()
    brief = module.make_brief()
    assert module.brief_text(brief) == (
        "job: What is 41 times 17?\n"
        "constraint that must hold: A child starts clean and gets a brief, not a trace.\n"
        "artifact path: context/runs/clean_child.json"
    )


def test_run_child_takes_a_brief_only_and_starts_empty(monkeypatch):
    module = load_module()
    assert list(inspect.signature(module.run_child).parameters) == ["brief"]
    source = inspect.getsource(module.run_child)
    assert "messages = []" in source
    assert "trace" not in inspect.signature(module.run_child).parameters

    def fake_loop(question, max_steps=8):
        assert question == "What is 41 times 17?"
        hops = [
            CallTool(name="multiply", arguments={"a": 41, "b": 17}),
            697,
            Stop(answer="697"),
        ]
        return hops, "done"

    monkeypatch.setattr(module, "loop", fake_loop)
    brief = module.make_brief()
    child = module.run_child(brief)
    assert child["messages"] == [
        {"role": "user", "content": module.brief_text(brief)}
    ]
    assert child["parent_trace_in_child"] is False
    assert child["answer"] == "697"
    assert child["stop_reason"] == "done"
    window = json.dumps(child["messages"], ensure_ascii=False)
    for needle in module.NEEDLES:
        assert needle not in window


def test_hop_to_json_covers_the_three_shapes():
    module = load_module()
    call = CallTool(name="multiply", arguments={"a": 41, "b": 17})
    assert module.hop_to_json(call) == {
        "kind": "call_tool",
        "name": "multiply",
        "arguments": {"a": 41, "b": 17},
    }
    assert module.hop_to_json(Stop(answer="697")) == {"kind": "stop", "answer": "697"}
    err = {"kind": "error", "error": "unknown tool", "name": "nope"}
    assert module.hop_to_json(err) is err
    assert module.hop_to_json(697) == {"kind": "seen", "value": 697}


def test_parent_trace_holds_the_needles_the_child_must_not_see():
    module = load_module()
    parent = module.make_parent_trace()
    assert len(parent) == 6
    window = json.dumps(parent, ensure_ascii=False)
    assert all(needle in window for needle in module.NEEDLES)
    assert module.NEEDLES == (
        "What is 347 times 19?",
        "6593",
        "full writer trace",
        "seen: 6593",
        "That is not the current goal.",
    )
