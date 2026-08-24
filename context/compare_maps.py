"""Count the live map and the fat comparison file with the same door."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scratch_agent.registry import TOOLS

LAW = "Context is a finite attention budget"
CLONE = "git clone"
LOOP_SIG = "def loop"


def classify(text: str) -> str:
    if (
        "context/README.md" in text
        and "scratch_agent/README.md" in text
        and LAW not in text
        and CLONE not in text
        and LOOP_SIG not in text
    ):
        return "point"
    return "paste"


def report(rel: str) -> tuple[str, int, int, str]:
    reader = TOOLS["read_file"]
    text = reader(rel)
    if isinstance(text, dict):
        raise SystemExit("read failed: %s %s" % (rel, text))
    chars = len(text)
    tokens = chars // 4
    job = classify(text)
    print(rel)
    print(chars)
    print(tokens)
    print(job)
    return rel, chars, tokens, job


def append_counts(rows: list[tuple[str, int, int, str]]) -> None:
    page = REPO_ROOT / "context" / "token_counts.md"
    existing = page.read_text(encoding="utf-8")
    if "## Map" in existing:
        return
    if not existing.endswith("\n"):
        existing += "\n"
    map_rel, map_chars, map_tokens, map_job = rows[0]
    fat_rel, fat_chars, fat_tokens, fat_job = rows[1]
    block = (
        "\n## Map\n\n"
        "path: %s\n"
        "chars: %s\n"
        "tokens_approx: %s\n"
        "job: %s\n"
        "\n## Fat\n\n"
        "path: %s\n"
        "chars: %s\n"
        "tokens_approx: %s\n"
        "job: %s\n"
    ) % (
        map_rel,
        map_chars,
        map_tokens,
        map_job,
        fat_rel,
        fat_chars,
        fat_tokens,
        fat_job,
    )
    page.write_text(existing + block, encoding="utf-8", newline="\n")


def main() -> None:
    rows = [
        report("AGENTS.md"),
        report("context/fat_agents.md"),
    ]
    append_counts(rows)


if __name__ == "__main__":
    main()
