"""context/polluted_child.py. Offline, no model call, no nested loop."""

import importlib.util
import inspect
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module():
    spec = importlib.util.spec_from_file_location(
        "polluted_child", REPO_ROOT / "context" / "polluted_child.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_child_copies_the_parent_list():
    module = load_module()
    source = inspect.getsource(module.run_child)
    assert "messages = list(parent_messages)" in source
    assert "scratch_agent.loop" not in inspect.getsource(module)
    parent = module.make_parent_trace()
    brief = module.make_brief()
    child = module.run_child(parent, brief)
    assert child["messages"] is not parent
    assert child["messages"][: len(parent)] == parent
    assert len(child["messages"]) == len(parent) + 1
    assert child["messages"][-1] == {
        "role": "user",
        "content": module.brief_text(brief),
    }


def test_find_spent_seen_returns_the_copied_seen_turn():
    module = load_module()
    parent = module.make_parent_trace()
    brief = module.make_brief()
    child = module.run_child(parent, brief)
    found = module.find_spent_seen(child["messages"])
    assert found == "6593"
    assert child["answer"] == found
    assert child["leaked"] == "seen: 6593"
    assert child["spent_tool_in_child"] is True
    assert child["parent_trace_in_child"] is True
