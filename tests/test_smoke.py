from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ENV_KEYS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "XAI_API_KEY",
    "KIMI_API_KEY",
    "QWEN_API_KEY",
    "DEEPSEEK_API_KEY",
    "OLLAMA_HOST",
]


def test_config_imports() -> None:
    import engines.config as config

    assert callable(config.configured_engines)
    assert "openai" in config.ENGINES
    assert "ollama" in config.ENGINES


def test_env_example_lists_providers() -> None:
    from dotenv import dotenv_values

    parsed = dotenv_values(REPO_ROOT / ".env.example")
    for key in REQUIRED_ENV_KEYS:
        assert key in parsed, key


def test_hello_models_has_main_guard() -> None:
    text = (REPO_ROOT / "engines" / "hello_models.py").read_text(encoding="utf-8")
    assert 'if __name__ == "__main__"' in text


def test_smoke_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "smoke.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
