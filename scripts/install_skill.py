#!/usr/bin/env python3
"""Copy the complete skill to an assistant directory without replacing existing files."""

import argparse
from pathlib import Path
import shutil
import sys

from skill_files import payload_files


LOCATIONS = {"codex": ".agents/skills", "cursor": ".cursor/skills", "claude": ".claude/skills"}


def install(destination):
    files = payload_files()
    # mkdir is exclusive, including for dangling symlinks; never merge installations.
    destination.mkdir(parents=True, exist_ok=False)
    for source, relative in files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return len(files)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--assistant", choices=LOCATIONS, help="Use the assistant's documented skills directory")
    target.add_argument("--destination", type=Path, help="Exact new skill directory, including the cangjie folder")
    parser.add_argument("--project", type=Path, help="Existing project root; default is a user-level installation")
    parser.add_argument("--dry-run", action="store_true", help="Print the destination without writing anything")
    args = parser.parse_args(argv)
    if args.project and not args.assistant:
        parser.error("--project requires --assistant")
    base = args.project.expanduser().absolute() if args.project else Path.home()
    if args.project and not base.is_dir():
        parser.error("--project must be an existing directory")
    destination = args.destination.expanduser().absolute() if args.destination else base / LOCATIONS[args.assistant] / "cangjie"
    try:
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"Destination exists; inspect it before updating: {destination}")
        if args.dry_run:
            print(f"Would install {len(payload_files())} files to {destination}")
            return 0
        count = install(destination)
    except (OSError, ValueError) as error:
        print(f"Error: {error}. Existing installations are never overwritten; inspect any partial destination before retrying.", file=sys.stderr)
        return 1
    print(f"Installed {count} files to {destination}")
    print("Reload the assistant if needed. LICENSE and NOTICE.md are included.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
