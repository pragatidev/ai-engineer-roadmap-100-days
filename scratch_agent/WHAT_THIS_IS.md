# What this is

An agent in this folder is reason plus tool plus loop. That is the whole agent.

Reason returns CallTool or Stop. The shelf in registry.py has two names only, read_file and multiply. Do not add divide.

loop.py runs those hops and asks named stop rules after every hop. retry.py exists. loop.py does not import it.

Keep the three run files.

- first_success.json: 347 times 19, product 6593, then Stop.
- failing_run.json: 347 divided by 19, unknown tool, nothing ran.
- max_steps_run.json: 347 times 19, two hops, the loop leaves on the step budget.
- day12_pass.json: 347 times 19, product 6593, Stop 6593, worker ran, stop reason done.

Do not delete them.

The failing run stays. Do not delete failing_run.json because the loop now passes.

This folder is plain Python. There is no LangChain in this folder. LangChain waits until Section 10. A team of agents is Section 11, called orchestration and orchestrator worker, not today. write_file stays off TOOLS. loop.py still does not import retry.py.

A demo with twelve agents is not this folder until this single loop is proven. This folder is one loop.
