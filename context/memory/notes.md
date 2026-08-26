# Notes

This file holds the facts that survive a compaction cut.

## May write

decision plus reason
discovered fact that cost work
current goal and state
artifact path
constraint that must hold

## May not write

raw tool output bodies (they live under context/runs)
secrets
a guess with no source
a rule that lives in the file that owns it
anything cheap to recompute

## Log

artifact path: context/runs/day16_note_run.json holds the day 16 run
source: context/memory/write_note.py
artifact path: context/runs/day18_session_one.json holds the day 18 session one run
source: context/memory/session_two.py
current goal and state: quiet question What is 41 times 17? still in the window after the cut
discovered fact that cost work: AGENTS.md points at context/README.md and does not paste the law
source: AGENTS.md
constraint that must hold: one control is not a set; isolation is not the third name on this list
decision plus reason: write notes before maybe_compact so dropped results do not take the facts with them
artifact path: context/runs/alive.json holds the alive run
source: context/alive.py
