# Token counts

## Before

chars: 20
tokens_approx: 5
question: What is 41 times 17?

## After

chars: 81064
tokens_approx: 20266
warehouse:
scratch_agent/README.md
scratch_agent/loop.py
scratch_agent/reason.py
scratch_agent/registry.py
scratch_agent/actions.py
repeat_count: 8
expected: 697
answer: 6593

Characters are prompt_chars. Tokens are characters divided by four. This folder has no extra tokenizer package.

## Map

path: AGENTS.md
chars: 1289
tokens_approx: 322
job: point

## Fat

path: context/fat_agents.md
chars: 4500
tokens_approx: 1125
job: paste

## Uncompacted

chars: 16978
tokens_approx: 4244

## Compacted

chars: 422
tokens_approx: 105
line: 500
goal: What is 347 times 19?

## Preloaded

files: 5
chars: 7734
tokens_approx: 1933
job: dump

## Just in time

named: context/README.md
chars: 282
tokens_approx: 70
skipped: AGENTS.md, context/compaction.py, context/token_counts.md, scratch_agent/README.md
job: read on demand

task: Read context/README.md and tell me what the attention budget is.

## Alive before

chars: 16949
tokens_approx: 4237
question: What is 41 times 17?

## Alive after

chars: 398
tokens_approx: 99
line: 500
expected: 697
answer: 697
compacted: true
notes_written: true
map: AGENTS.md
map_job: point
controls: compact, notes, a map
short_demo: false
death_rerun: false
isolation_on_list: false
artifact path: context/runs/alive.json
