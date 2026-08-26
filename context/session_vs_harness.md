# Session versus harness

One question sorts every file in this repo.
If it disappeared right now, what command brings it back?

## A command brings it back

AGENTS.md
context/memory/write_note.py
context/memory/recover.py
context/memory/session_two.py
context/compaction.py

git checkout -- <path>. These are source, they are committed, and git holds a copy.
Losing one costs the seconds it takes to type the command.

## No command brings it back, and that is fine

context/runs/day18_session_one.json

The session one transcript. Git never saw it, so git cannot return it.
It did not matter: its one fact was written into context/memory/notes.md before the delete.

## No command brings it back, and that is the whole risk

the next line under ## Log in context/memory/notes.md

A fact you have observed and have not written down yet.
No checkout reaches it, because nothing is holding a copy.
The lines already in notes.md are safe only because write_note.py wrote them and a commit kept them.
That write step is the durable half. Everything above it is replaceable.
