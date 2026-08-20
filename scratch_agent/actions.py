"""Typed action the reason step returns. Plain Python. No model call."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CallTool:
    """Run a tool. Name plus the arguments that tool needs."""

    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Stop:
    """We're done. The answer you'd show a person."""

    answer: str


Action = CallTool | Stop


if __name__ == "__main__":
    call = CallTool(name="multiply", arguments={"a": 347, "b": 19})
    stop = Stop(answer="6593")
    print(call)
    print(stop)
