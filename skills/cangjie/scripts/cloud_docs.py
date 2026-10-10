#!/usr/bin/env python3
"""Search a bundled chapter catalog and fetch individual public Cangjie documents."""

import argparse
import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


SKILL_DIR = Path(__file__).resolve().parents[1]
INVENTORY = SKILL_DIR / "references" / "docs-inventory.jsonl"
SNAPSHOT = "169f052c0517299bdab66723eab870552883b0e9"
SOURCES = {
    "gitcode": (
        "https://raw.gitcode.com/Cangjie/cangjie_docs/raw",
        "https://gitcode.com/Cangjie/cangjie_docs/blob",
    ),
    "github": (
        "https://raw.githubusercontent.com/cangjielanguage/cangjie_docs",
        "https://github.com/cangjielanguage/cangjie_docs/blob",
    ),
}
MAX_BYTES = 3 * 1024 * 1024
BRANCH_CACHE_SECONDS = 300


def validate_redirect(original, target):
    before, after = urlsplit(original), urlsplit(target)
    if (
        after.scheme != "https"
        or after.hostname != before.hostname
        or after.port not in (None, 443)
        or after.username is not None
        or after.password is not None
    ):
        raise ValueError("Unexpected redirect away from the public raw-document host.")


class DocumentRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Validate every hop before urllib can send a request to its target.
        try:
            validate_redirect(req.full_url, newurl)
        except ValueError:
            fp.close()
            raise
        return super().redirect_request(req, fp, code, msg, headers, newurl)


urlopen = build_opener(DocumentRedirectHandler()).open


def load_catalog():
    return [json.loads(line) for line in INVENTORY.read_text(encoding="utf-8").splitlines()]


def validate_path(path):
    parts = PurePosixPath(path).parts
    if (
        not path.startswith("docs/")
        or not path.endswith(".md")
        or any(part in (".", "..") for part in path.split("/"))
        or any(ord(char) < 32 for char in path)
        or "\\" in path
        or PurePosixPath(path).as_posix() != path
        or len(parts) < 3
    ):
        raise ValueError("Use a normalized docs/... Markdown path, not a URL or local path.")
    return path


def validate_ref(ref):
    if not re.fullmatch(r"[A-Za-z0-9_./-]+", ref) or any(
        part in ("", ".", "..") for part in ref.split("/")
    ):
        raise ValueError("Invalid Git ref; use a commit, tag, or branch such as release/1.1.")
    return ref


def immutable(ref):
    return re.fullmatch(r"[0-9a-fA-F]{40}", ref) is not None


def urls(source, ref, path):
    suffix = f"{quote(ref, safe='')}/{quote(path, safe='/')}"
    raw, web = SOURCES[source]
    return f"{raw}/{suffix}", f"{web}/{suffix}"


def validate_body(raw, expected_hash=None):
    if len(raw) > MAX_BYTES:
        raise ValueError("Document exceeds the 3 MiB limit.")
    text = raw.decode("utf-8")
    start = text.lstrip("\ufeff \t\r\n").lower()
    if not start or start.startswith(("<!doctype html", "<html", "<head", "<body")):
        raise ValueError("Server returned an empty page or HTML, not Markdown.")
    if expected_hash and hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError("Content does not match the pinned document SHA-256.")
    return text


def download(url, expected_hash=None):
    validate_redirect(url, url)
    request = Request(url, headers={"User-Agent": "cangjie-skill/1", "Accept": "text/plain"})
    with urlopen(request, timeout=20) as response:
        validate_redirect(url, response.geturl())
        if response.status != 200:
            raise ValueError(f"Unexpected HTTP status: {response.status}")
        if "html" in response.headers.get("Content-Type", "").lower():
            raise ValueError("Server returned HTML instead of a raw document.")
        return validate_body(response.read(MAX_BYTES + 1), expected_hash)


def default_cache():
    if os.environ.get("XDG_CACHE_HOME"):
        base = Path(os.environ["XDG_CACHE_HOME"])
    elif os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        base = Path(os.environ["LOCALAPPDATA"])
    else:
        base = Path.home() / ".cache"
    return base / "cangjie-skill"


def fetch_document(path, args, catalog):
    validate_path(path)
    expected = next(
        (row["sha256"] for row in catalog if row["path"] == path), None
    ) if args.ref == SNAPSHOT else None
    # Branch names may refer to different commits on different hosts.
    providers = ["gitcode", "github"] if args.source == "auto" and immutable(args.ref) else [
        "gitcode" if args.source == "auto" else args.source
    ]
    errors = []
    for source in providers:
        raw_url, web_url = urls(source, args.ref, path)
        cache_file = args.cache_dir / (hashlib.sha256(raw_url.encode()).hexdigest() + ".json")
        if not args.refresh:
            try:
                item = json.loads(cache_file.read_text(encoding="utf-8"))
                if not isinstance(item, dict) or not isinstance(item.get("text"), str):
                    raise ValueError("Invalid cache record")
                raw = item["text"].encode("utf-8")
                text = validate_body(raw, expected)
                if item["url"] != raw_url or hashlib.sha256(raw).hexdigest() != item["sha256"]:
                    raise ValueError("Invalid cache metadata")
                fresh = immutable(args.ref) or 0 <= time.time() - item["fetched_at"] < BRANCH_CACHE_SECONDS
                if fresh or args.offline:
                    return text, web_url, raw_url, "offline cache" if args.offline else "cache"
            except (OSError, ValueError, KeyError, TypeError):
                pass
        if args.offline:
            errors.append(f"{source}: no valid cached document")
            continue
        try:
            text = download(raw_url, expected)
        except (OSError, ValueError, URLError, HTTPException) as error:
            errors.append(f"{source}: {error}")
            continue
        item = {
            "url": raw_url, "fetched_at": time.time(), "text": text,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
        temporary = None
        try:
            args.cache_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.cache_dir, delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(item, stream, ensure_ascii=False)
            temporary.replace(cache_file)
        except OSError as error:
            print(f"Warning: document fetched but cache could not be saved: {error}", file=sys.stderr)
        finally:
            if temporary is not None and temporary.exists():
                try:
                    temporary.unlink()
                except OSError:
                    pass
        return text, web_url, raw_url, "network"
    raise ValueError("; ".join(errors) + ". No version was substituted; use the printed URL with a web reader if needed.")


def catalog_search(catalog, args):
    query = args.query.casefold().strip() if args.command == "search" else ""
    if args.command == "search" and not query:
        raise ValueError("Search query must not be empty.")
    terms = query.split() if args.command == "search" and args.match == "all" else [query]
    results = []
    for row in catalog:
        if row["kind"] != "markdown":
            continue
        if args.lang != "all" and row["language"] != args.lang:
            continue
        if args.area != "all" and not row["path"].startswith(f"docs/{args.area}/"):
            continue
        fields = [row["title"], row["path"], *row.get("headings", [])]
        matches = [field for field in fields if any(term in field.casefold() for term in terms)]
        if not all(any(term in field.casefold() for field in fields) for term in terms):
            continue
        score = sum(20 * (term in fields[0].casefold()) + 10 * (term in fields[1].casefold()) for term in terms) + len(matches)
        results.append((score, row, matches))
    results.sort(key=lambda result: (-result[0], result[1]["path"]))
    print(f"Bundled catalog at {SNAPSHOT}; title/path/heading search, NOT live full-text search.")
    if args.ref != SNAPSHOT:
        print(f"Requested ref: {args.ref}. Catalog paths may differ; consult that ref's online table of contents.")
    if not results:
        print("No catalog matches. Try a shorter topic, or web search the public repository.")
        return 1
    limit = args.limit if args.command == "search" else len(results)
    for _, row, matches in results[:limit]:
        source = "gitcode" if args.source == "auto" else args.source
        raw, web = urls(source, args.ref, row["path"])
        print(f"\n{row['path']} | {row['title']}\nSource: {web}\nRaw: {raw}")
        if query:
            for heading in [m for m in matches if m not in (row["title"], row["path"])][:3]:
                print(f"  Heading: {heading}")
    return 0


def catalog_info(catalog, args):
    row = next((row for row in catalog if row["path"] == args.path), None)
    if row is None:
        raise ValueError("Path is not in the bundled catalog; use url/read to check the requested ref.")
    source = "gitcode" if args.source == "auto" else args.source
    raw, web = urls(source, args.ref, args.path)
    metadata = {
        **row, "catalog_ref": SNAPSHOT, "requested_ref": args.ref,
        "snapshot_metadata_only": args.ref != SNAPSHOT, "source_url": web, "raw_url": raw,
    }
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


def next_read_command(args, start):
    command = [
        sys.executable, str(Path(__file__).resolve()), "--ref", args.ref,
        "--source", args.source, "--cache-dir", str(args.cache_dir),
    ]
    if args.offline:
        command.append("--offline")
    command.extend(["read", args.path, "--start", str(start)])
    if os.name == "nt":
        return "& " + " ".join("'" + part.replace("'", "''") + "'" for part in command)
    return shlex.join(command)


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("value must be positive")
    return number


def parser():
    result = argparse.ArgumentParser(
        description=__doc__,
        epilog="Examples: search Option --lang all | info docs/dev-guide/source_zh_cn/function/define_functions.md. "
        "Put global options (--ref, --source, --offline) before the subcommand.",
    )
    result.add_argument("--ref", default=SNAPSHOT, help="Git commit, tag, or branch (default: audited commit)")
    result.add_argument("--source", choices=["auto", *SOURCES], default="auto")
    result.add_argument("--cache-dir", type=Path, default=default_cache())
    mode = result.add_mutually_exclusive_group()
    mode.add_argument("--refresh", action="store_true", help="Bypass cache")
    mode.add_argument("--offline", action="store_true", help="Read only existing cache; never use network")
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("list", "search"):
        sub = commands.add_parser(name, help="List catalog documents" if name == "list" else "Search all catalog headings")
        sub.add_argument("--area", choices=["all", "dev-guide", "tools", "central-repo"], default="all")
        sub.add_argument("--lang", choices=["zh", "en", "all"], default="zh")
        if name == "search":
            sub.add_argument("query", help="Literal phrase in bundled titles, paths, or headings")
            sub.add_argument("--limit", type=positive, default=8)
            sub.add_argument("--match", choices=["phrase", "all"], default="phrase", help="Match a literal phrase (default) or every whitespace-separated term across catalog fields")
    for name in ("read", "url", "info"):
        sub = commands.add_parser(name, help={
            "read": "Read a document; print the next-page command when more lines remain",
            "url": "Print document URLs without network access",
            "info": "Print bundled metadata as JSON without downloading a document",
        }[name])
        sub.add_argument("path", help="Public repository path: docs/.../*.md")
        if name == "read":
            sub.add_argument("--start", type=positive, default=1)
            sub.add_argument("--end", type=positive)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        validate_ref(args.ref)
        if args.command in ("list", "search"):
            return catalog_search(load_catalog(), args)
        validate_path(args.path)
        if args.command == "url":
            sources = SOURCES if args.source == "auto" else [args.source]
            for source in sources:
                raw, web = urls(source, args.ref, args.path)
                print(f"{source}\nSource: {web}\nRaw: {raw}")
            return 0
        catalog = load_catalog()
        if args.command == "info":
            return catalog_info(catalog, args)
        end = args.end if args.end is not None else args.start + 79
        if end < args.start:
            raise ValueError("--end must be greater than or equal to --start.")
        raw, web = urls("gitcode" if args.source == "auto" else args.source, args.ref, args.path)
        print(f"Requested ref: {args.ref}\nSource: {web}\nRaw: {raw}", flush=True)
        text, web, raw, origin = fetch_document(args.path, args, catalog)
        lines = text.lstrip("\ufeff").splitlines()
        if args.start > len(lines):
            raise ValueError(f"--start exceeds document length ({len(lines)} lines).")
        print(f"Retrieved via {origin}: {raw}\nCitation: {web}\n{args.path} ({len(lines)} lines)")
        if args.ref != SNAPSHOT:
            print("Not the audited snapshot; a branch/tag cache may be up to 5 minutes old (offline cache may be older).")
        for n in range(args.start, min(end, len(lines)) + 1):
            print(f"{n}: {lines[n - 1]}")
        if end < len(lines):
            shell = "PowerShell" if os.name == "nt" else "POSIX shell"
            print(f"Next: {next_read_command(args, end + 1)}")
            print(f"Next command shell: {shell}")
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
