# AI Engineer Roadmap: 100 Days of Code

One living system. One checkable artifact per day for 100 days.

This repo is the course workbench. You clone it once, then commit each day's
work here so a hiring manager can clone it and run the smoke check.

## Setup

```bash
git clone https://github.com/pragatidev/ai-engineer-roadmap-100-days
cd ai-engineer-roadmap-100-days
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

On macOS or Linux, the first command is `python3 -m venv .venv`, and every command
after it uses `.venv/bin/python` in place of `.venv\Scripts\python`.

Copy the example env file and set at most one provider key. Or leave the keys
empty and start Ollama on the host below.

```bash
copy .env.example .env
.venv\Scripts\python scripts/smoke.py
```

## If a setup command fails

Windows: install Python from python.org and tick "Add Python to PATH", then open a new
terminal. Use `.venv\Scripts\python` for every command after the venv.

macOS: use `python3`, not `python`. Install Git and Python from git-scm.com and python.org,
or let the Xcode Command Line Tools prompt install them. The Ollama app must be opened once
from Applications before the `ollama` command exists.

Linux: install Git and Python with your package manager, not from those sites. If
`python3 -m venv .venv` reports that ensurepip is not available, install the venv package
first (`sudo apt install python3-venv` on Debian or Ubuntu), then run it again. Start the
local model service with `ollama serve` in its own terminal.

Any system: a terminal reads its program list when it opens, so open a new terminal after
installing anything.

Day 1 live call (needs one key in `.env`, or a running Ollama):

```bash
.venv\Scripts\python engines/hello_models.py
```
