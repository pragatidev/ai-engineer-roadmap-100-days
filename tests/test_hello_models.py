from __future__ import annotations

from engines.hello_models import format_row


def test_format_row_has_four_parts() -> None:
    line = format_row("ollama", "dummy-model", 12, "pong")
    parts = line.split(" | ")
    assert parts == ["ollama", "dummy-model", "12", "pong"]


def test_format_row_latency_is_digits() -> None:
    line = format_row("openai", "dummy-model", 3909, "pong")
    parts = line.split(" | ")
    assert parts[2].isdigit()
