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

Nothing here fetches a file yet. This is the contract the read tool obeys
in the next lecture.
"""

from __future__ import annotations

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


def main() -> None:
    print("RULE")
    print(RULE)
    print("THE TEST")
    for question in THE_TEST:
        print(question)
    print("DECISIONS")
    for names, every in ((True, True), (True, False), (False, False)):
        print("names=%s every_turn=%s -> %s" % (names, every, explain(names, every)))


if __name__ == "__main__":
    main()
