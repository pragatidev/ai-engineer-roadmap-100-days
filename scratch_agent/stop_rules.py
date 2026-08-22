"""Named hard-stop checks. Each returns a reason string or None.

Do not import this module from loop.py yet. The loop still exits by
type change and by the unknown-tool break. These functions name why.
"""

from __future__ import annotations

from scratch_agent.actions import Stop


def stop_on_done(hops):
    """Reason 'done' when the latest hop is already a Stop with an answer."""
    if not hops:
        return None
    last = hops[-1]
    if isinstance(last, Stop):
        return "done"
    if isinstance(last, dict) and last.get("kind") == "stop":
        return "done"
    return None


def stop_on_max_steps(hops, max_steps):
    """Reason 'max steps' when the hop list met the budget."""
    if len(hops) >= max_steps:
        return "max steps"
    return None


def stop_on_repeated_tool_error(hops):
    """Reason 'repeated tool error' when two error hops share a tool name."""
    seen_fail = {}
    for hop in hops:
        if not isinstance(hop, dict) or hop.get("kind") != "error":
            continue
        name = hop.get("name")
        seen_fail[name] = seen_fail.get(name, 0) + 1
        if seen_fail[name] > 1:
            return "repeated tool error"
    return None


if __name__ == "__main__":
    print(stop_on_done.__name__)
    print(stop_on_max_steps.__name__)
    print(stop_on_repeated_tool_error.__name__)
