# read_file

This page is the contract for one tool named `read_file`.
There is no Python function in this file.

This is not multiply, not HTTP, and not a function that returns the string `ok`.

## Argument

`path` is a string relative to the repo root.
The repo root is the folder that contains `scratch_agent`.
A legal path looks like `scratch_agent/README.md`.

## Success

Return the file text as a string.

## Failure

Return an error object with a reason.
Do not crash the process.
Refuse a missing file with that same error object.
Refuse path traversal, including `..`, with that same error object.

## Bounds

The tool may only read files under the repo root.
If the model can ask for any path on the machine, you gave it the disk, not a tool.
