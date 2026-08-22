"""Bounded retries. The budget is a number you wrote, not a hope.

loop.py does not import this module yet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.registry import TOOLS


def stop_on_retry_budget(attempts, max_tries):
    """Reason 'retry budget' when the attempt count met the max."""
    if attempts >= max_tries:
        return "retry budget"
    return None


def flaky_multiply(attempt, succeed_on, a=347, b=19):
    """Miss until attempt reaches succeed_on, then call the real multiply."""
    if attempt < succeed_on:
        return {"kind": "error", "error": "transient error", "name": "multiply"}
    return TOOLS["multiply"](a, b)


def run_with_retry(succeed_on, max_tries=3):
    """Call the wrapper until a product lands, or until the budget fires."""
    hops = []
    for attempt in range(1, max_tries + 1):
        seen = flaky_multiply(attempt, succeed_on)
        if isinstance(seen, dict) and seen.get("kind") == "error":
            hops.append(seen)
            coded = stop_on_retry_budget(attempt, max_tries)
            if coded is not None:
                return hops, coded
            continue
        hops.append({"kind": "seen", "value": seen})
        return hops, None
    return hops, None


if __name__ == "__main__":
    hops, coded = run_with_retry(succeed_on=3, max_tries=3)
    print(
        json.dumps(
            {"hops": hops, "stop_reason": coded},
            indent=2,
            ensure_ascii=False,
        )
    )
    hops, coded = run_with_retry(succeed_on=4, max_tries=3)
    print(
        json.dumps(
            {"hops": hops, "stop_reason": coded},
            indent=2,
            ensure_ascii=False,
        )
    )
