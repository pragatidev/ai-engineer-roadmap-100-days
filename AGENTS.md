# AGENTS.md

This file is a map of the workbench, not a pasted encyclopedia.
Rules live in the files that own them. Do not copy those rules here.

## Now

README.md
Setup for a human clone. Point here. Do not paste the clone steps.

engines/config.py
The only place model IDs live. Point here. Do not paste model strings.

engines/hello_models.py
One model call, then the program stops.

engines/one_tool_call.py
One structured tool request, then the program stops. Not a loop.

scripts/smoke.py
Offline green check. A hiring manager can clone and run this.

tests/test_smoke.py
Four tests. Green with no key and no network.

.env.example
Provider key names. Set at most one, or use the local Ollama host. Never commit a filled .env.

scratch_agent/README.md
The loop is done. Point here. Do not paste the loop.

context/README.md
The law of this section. Point here. Do not paste the law.

## Later rooms

These rooms do not exist yet. Do not create them today. Empty rooms stay empty until those days.

harness with guides and sensors
Agent Skills that compose
MCP server
measured RAG workbench with a scoreboard
evals gating CI
traces and guardrails
same agent rebuilt on LangGraph
orchestrator-worker multi-agent
one HTTP service in Docker
career folder
capstone that imports the rest
