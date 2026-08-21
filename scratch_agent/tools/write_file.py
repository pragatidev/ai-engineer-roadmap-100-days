"""Write text under the repo root. Default confirm is False. Refuse unless confirm is True."""

from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent


def write_file(path: str, content: str, confirm: bool = False):
    if ".." in Path(path).parts:
        return {"error": "path traversal"}
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        return {"error": "outside repo root"}
    if confirm is not True:
        return {"error": "confirm required"}
    resolved.write_text(content, encoding="utf-8")
    return {"wrote": path}


if __name__ == "__main__":
    target = "scratch_agent/README.md"
    print((repo_root / target).read_text(encoding="utf-8"))
    print(write_file(target, "ok"))
    print((repo_root / target).read_text(encoding="utf-8"))
