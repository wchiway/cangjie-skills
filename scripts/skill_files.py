"""Select the portable skill payload, excluding local caches and build output."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "cangjie"
DIRECTORIES = {"agents", "assets", "references", "scripts"}
ROOT_FILES = {"SKILL.md", "LICENSE", "NOTICE.md"}
SUFFIXES = {".md", ".jsonl", ".yaml", ".py", ".cj", ".svg"}


def payload_files(source=SKILL):
    files = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        selected = (
            relative.as_posix() in ROOT_FILES
            or (relative.parts[0] in DIRECTORIES and path.suffix in SUFFIXES)
        )
        if path.is_symlink():
            raise ValueError(f"Skill payload must not contain symbolic links: {relative}")
        if path.is_file() and selected:
            files.append((path, relative))
    missing = ROOT_FILES - {relative.as_posix() for _, relative in files}
    if missing:
        raise ValueError(f"Missing required skill files: {', '.join(sorted(missing))}")
    return files
