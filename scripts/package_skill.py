#!/usr/bin/env python3
"""Build a deterministic standalone skill ZIP with license and checksum."""

import argparse
import hashlib
from pathlib import Path
import zipfile

from skill_files import payload_files


def package(output):
    files = payload_files()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "cangjie-skill.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as stream:
        for source, relative in files:
            entry = zipfile.ZipInfo(f"cangjie/{relative.as_posix()}", date_time=(2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            stream.writestr(entry, source.read_bytes())
    checksum = output / "SHA256SUMS"
    checksum.write_text(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n", encoding="utf-8")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist"), help="Generated artifact directory (default: dist)")
    args = parser.parse_args()
    print(package(args.output))


if __name__ == "__main__":
    main()
