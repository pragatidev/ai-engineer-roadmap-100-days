"""Just in time retrieval, written down as a rule before it is wired.

The rule:

    Read a file when the task names it, not before.

Preloading is not free insurance. Every token pushed in ahead of time
competes for attention with the token that actually matters, and you pay
that price on every turn of the loop, not once. context/token_counts.md
holds this repo's own receipt for it.

The map is the alternative. AGENTS.md carries identifiers, paths, names,
one line about what lives where. It does not carry bodies. The agent holds
the index and loads a body only when the task in front of it names that
body.

Preloading still wins when the set is small, fixed, and every turn needs
all of it. So the decision is two questions, and both must be answered
before you reach for either shape.

MAP below is that index. named_file decides. jit_read does the read, and
prints what it skipped, because restraint is invisible unless you print it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.registry import TOOLS

RULE = "Read a file when the task names it, not before."

# The two questions. decide() below is these lines in code.
THE_TEST = (
    "Does the task name this file?",
    "Will every turn need it?",
)

JIT_WINS = (
    "the set is large or open ended",
    "only some turns touch any one file",
    "the task names the file it needs",
)

PRELOAD_WINS = (
    "the set is small and fixed",
    "every single turn needs all of it",
    "a fetch per hop costs more than the tokens do",
)

# Honest about the price of the shape we are choosing.
JIT_COSTS = (
    "one round trip per read",
    "one decision the agent can get wrong",
)

JIT = "just in time"
PRELOAD = "preload"


def decide(task_names_file: bool, every_turn_needs_it: bool) -> str:
    """Answer THE_TEST and get the shape back.

    Small, fixed, and needed on every turn is the preload case. Everything
    else reads on demand, which includes the file the task never names:
    not naming it is the strongest signal there is not to load it.
    """
    if every_turn_needs_it:
        return PRELOAD
    if task_names_file:
        return JIT
    return JIT


def explain(task_names_file: bool, every_turn_needs_it: bool) -> str:
    """One spoken line for a decision, so a run reads like a sentence."""
    shape = decide(task_names_file, every_turn_needs_it)
    if shape == PRELOAD:
        return "preload: every turn needs it, so pay once"
    if task_names_file:
        return "just in time: the task names it, so read it now"
    return "just in time: the task does not name it, so do not read it"


def print_the_rule() -> None:
    """The day 16 printout. Still here; today's __main__ runs the read instead."""
    print("RULE")
    print(RULE)
    print("THE TEST")
    for question in THE_TEST:
        print(question)
    print("DECISIONS")
    for names, every in ((True, True), (True, False), (False, False)):
        print("names=%s every_turn=%s -> %s" % (names, every, explain(names, every)))


# The map. Identifiers and one line about what lives where. Never bodies.
MAP = {
    "AGENTS.md": "map of the workbench",
    "context/README.md": "the law of this section",
    "context/token_counts.md": "the counts from this section",
    "scratch_agent/README.md": "what the loop is",
    "context/compaction.py": "the compaction rule and step",
}


def named_file(task: str):
    """The decider. The first mapped path the task actually mentions, or None."""
    for path in MAP:
        if path in task:
            return path
    return None


def jit_read(task: str) -> dict:
    """Read the one file the task names. Report what was skipped either way."""
    path = named_file(task)
    if path is None:
        return {
            "task": task,
            "named": None,
            "read": None,
            "skipped": sorted(MAP),
            "chars": 0,
            "tokens_approx": 0,
        }
    body = TOOLS["read_file"](path)
    return {
        "task": task,
        "named": path,
        "read": path,
        "skipped": sorted(key for key in MAP if key != path),
        "chars": len(body),
        "tokens_approx": len(body) // 4,
    }


def preload_all() -> dict:
    """The other side of the argument. Every body in the map, all at once."""
    blob = "".join(TOOLS["read_file"](path) for path in MAP)
    return {"chars": len(blob), "tokens_approx": len(blob) // 4}


def compare(task: str) -> dict:
    """Both strategies on one task string, and the gap between them.

    Fairness is the whole experiment. Same task, same counting rule
    (characters divided by four), same five files in the map. The only
    thing that changes is when the bodies get loaded.
    """
    preloaded = preload_all()
    just_in_time = jit_read(task)
    return {
        "task": task,
        "preload_chars": preloaded["chars"],
        "preload_tokens": preloaded["tokens_approx"],
        "jit_named": just_in_time["named"],
        "jit_chars": just_in_time["chars"],
        "jit_tokens": just_in_time["tokens_approx"],
        "skipped": just_in_time["skipped"],
        "saved_tokens": preloaded["tokens_approx"] - just_in_time["tokens_approx"],
    }


def append_counts(payload: dict) -> None:
    """Write the two counts onto the end of context/token_counts.md.

    Append mode, not write mode. Every earlier count in that file stays
    exactly where it is.
    """
    page = REPO_ROOT / "context" / "token_counts.md"
    block = (
        "\n## Preloaded\n\n"
        "files: %s\n"
        "chars: %s\n"
        "tokens_approx: %s\n"
        "job: dump\n"
        "\n## Just in time\n\n"
        "named: %s\n"
        "chars: %s\n"
        "tokens_approx: %s\n"
        "skipped: %s\n"
        "job: read on demand\n"
        "\ntask: %s\n"
    ) % (
        len(MAP),
        payload["preload_chars"],
        payload["preload_tokens"],
        payload["jit_named"],
        payload["jit_chars"],
        payload["jit_tokens"],
        ", ".join(payload["skipped"]),
        payload["task"],
    )
    with open(page, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(block)


if __name__ == "__main__":
    TASK = "Read context/README.md and tell me what the attention budget is."
    payload = compare(TASK)
    print(json.dumps(payload, indent=2))
    append_counts(payload)
