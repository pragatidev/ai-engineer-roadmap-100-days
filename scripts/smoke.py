"""Offline green checks. No network calls."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXPECTED_FILES = [
    "README.md",
    ".env.example",
    "requirements.txt",
    "engines/config.py",
    "engines/hello_models.py",
    "scripts/smoke.py",
    "tests/test_smoke.py",
    ".github/workflows/smoke.yml",
]

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


def check_python() -> tuple[bool, str]:
    ok = sys.version_info >= (3, 10)
    ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return ok, f"python {ver} (need >= 3.10)"


def check_tree() -> tuple[bool, str]:
    missing = [rel for rel in EXPECTED_FILES if not (REPO_ROOT / rel).is_file()]
    if missing:
        return False, "missing: " + ", ".join(missing)
    return True, "expected files present"


def check_env_example() -> tuple[bool, str]:
    from dotenv import dotenv_values

    parsed = dotenv_values(REPO_ROOT / ".env.example")
    missing = [key for key in REQUIRED_ENV_KEYS if key not in parsed]
    if missing:
        return False, "missing " + ", ".join(missing)
    return True, "seven providers plus OLLAMA_HOST"


def check_config_import() -> tuple[bool, str]:
    try:
        import engines.config  # noqa: F401
    except Exception as exc:
        return False, f"import failed: {exc}"
    return True, "import ok"


def check_pytest_collect() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        tail = (result.stdout + result.stderr).strip().splitlines()[-3:]
        return False, " | ".join(tail) or "collect failed"
    return True, "collect ok"


def run_checks() -> list[tuple[str, bool, str]]:
    return [
        ("python>=3.10", *check_python()),
        ("repo tree", *check_tree()),
        (".env.example", *check_env_example()),
        ("engines.config", *check_config_import()),
        ("pytest collect", *check_pytest_collect()),
    ]


def main() -> int:
    rows = run_checks()
    width = max(len(name) for name, _, _ in rows)
    all_ok = True
    for name, ok, detail in rows:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"{name.ljust(width)}  {status}  {detail}")
    print()
    print("ALL PASS" if all_ok else "SMOKE FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
