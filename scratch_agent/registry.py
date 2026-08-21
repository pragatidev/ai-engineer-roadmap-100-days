"""Name to callable. The loop looks up a string. It does not hard-code one tool."""

from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent


def read_file(path: str):
    if ".." in Path(path).parts:
        return {"error": "path traversal"}
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        return {"error": "outside repo root"}
    try:
        return resolved.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"error": "missing file"}


TOOLS = {
    "read_file": read_file,
}


if __name__ == "__main__":
    print(TOOLS["read_file"]("scratch_agent/README.md"))
    print(TOOLS["read_file"]("scratch_agent/../README.md"))
    print(TOOLS["read_file"]("scratch_agent/no_such_file.md"))
