#!/usr/bin/env python3
"""Compile skill examples and run SDK semantic regressions in a fresh temp project."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


SKILL = Path(__file__).resolve().parents[1]
ANSI = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|[78])")
EXPECTED = {
    ("language.md", 1): "7\n",
    ("language.md", 2): "missing\n0\n7\n",
    ("concurrency-and-io.md", 1): "1\n",
    ("toolchain.md", 1): None,
}
NEGATIVE = {
    "positional-default": "func bad(x: Int64 = 1): Int64 { x }\nmain() {}\n",
    "immutable-struct-mut": "struct Counter { public var n = 0; public mut func inc() { n += 1 } }\nmain() { let c = Counter(); c.inc() }\n",
    "class-mut": "class Counter { public mut func inc() {} }\nmain() {}\n",
    "escaping-var": "func bad(): () -> Int64 { var n = 0; return { => n += 1; n } }\nmain() {}\n",
    "cast-is-not-unwrapped": 'main() { let value: Any = "hello"; let text: String = value as String; println(text) }\n',
    "non-exhaustive-match": "func bad(n: Int64): Int64 { match (n) { case 0 => 1 } }\nmain() {}\n",
}


class Runner:
    def __init__(self, work):
        self.work = work
        self.results = []

    def run(self, name, command, cwd, expected_code=0, output=None):
        log = self.work / f"{len(self.results) + 1:02d}-{name}.log"
        try:
            completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=120)
        except (subprocess.TimeoutExpired, OSError) as error:
            def decode(value):
                return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""

            stdout = ANSI.sub("", decode(getattr(error, "stdout", None)))
            stderr = ANSI.sub("", decode(getattr(error, "stderr", None)))
            log.write_text(f"$ {' '.join(command)}\n{stdout}{stderr}\n{error}\n", encoding="utf-8")
            self.results.append({
                "name": name, "passed": False, "exit_code": None, "log": str(log),
                "timed_out": isinstance(error, subprocess.TimeoutExpired), "error": str(error),
            })
            raise RuntimeError(f"{name} could not complete; see {log}") from error
        stdout = ANSI.sub("", completed.stdout)
        stderr = ANSI.sub("", completed.stderr)
        log.write_text(f"$ {' '.join(command)}\n{stdout}{stderr}", encoding="utf-8")
        if expected_code is None:
            passed = completed.returncode > 0 and "error:" in (stdout + stderr) and "main.cj:" in (stdout + stderr)
        else:
            passed = completed.returncode == expected_code
        if output is not None:
            passed = passed and stdout.replace("\r\n", "\n") == output
        # Positive examples must be clean, not merely accepted by the compiler.
        if expected_code == 0 and re.search(r"\b(?:warning|error):", stdout + stderr):
            passed = False
        self.results.append({"name": name, "passed": passed, "exit_code": completed.returncode, "log": str(log)})
        print(f"{'PASS' if passed else 'FAIL'} {name} (exit {completed.returncode})", flush=True)
        if not passed:
            print(stdout + stderr, flush=True)
            raise RuntimeError(f"{name} failed; see {log}")
        return stdout


def verify_xml(directory, expected, expected_skipped=0):
    cases = []
    for path in directory.rglob("*.xml"):
        cases.extend(ET.parse(path).getroot().iter("testcase"))
    skipped = sum(case.find("skipped") is not None for case in cases)
    if len(cases) - skipped != expected or skipped != expected_skipped:
        raise RuntimeError(f"Expected {expected} executed/{expected_skipped} skipped in {directory}; found {len(cases) - skipped}/{skipped}")
    for case in cases:
        if any(child.tag in ("failure", "error") for child in case):
            raise RuntimeError(f"Non-passing test case: {case.attrib}")
        if case.find("skipped") is None and int(case.get("assertions", "0")) < 1:
            raise RuntimeError(f"Test executed no assertions: {case.attrib}")
    print(f"PASS XML report: {expected} executed, {skipped} skipped, zero failed", flush=True)


def collect_examples():
    examples = {}
    for reference in sorted((SKILL / "references").glob("*.md")):
        blocks = re.findall(r"^```cangjie\n(.*?)^```", reference.read_text(encoding="utf-8"), re.M | re.S)
        for index, code in enumerate(blocks, 1):
            examples[(reference.name, index)] = code
    if examples.keys() != EXPECTED.keys():
        raise RuntimeError("Example set changed; add explicit runtime expectations before claiming coverage.")
    return examples


def verify(runner):
    work = runner.work
    examples = collect_examples()
    compiler = runner.run("compiler-version", ["cjc", "-v"], work)
    manager = runner.run("cjpm-version", ["cjpm", "-v"], work)
    print(compiler + manager, flush=True)
    for (filename, index), code in examples.items():
        if EXPECTED[(filename, index)] is None:
            continue
        name = f"{Path(filename).stem}-{index}"
        case = work / name
        case.mkdir()
        (case / "main.cj").write_text(code, encoding="utf-8")
        runner.run(f"{name}-compile", ["cjc", "main.cj", "-o", "main"], case)
        binary = case / ("main.exe" if sys.platform == "win32" else "main")
        runner.run(f"{name}-run", [str(binary)], case, output=EXPECTED[(filename, index)])

    project = work / "project"
    runner.run("cjpm-init", ["cjpm", "init", "--name", "demo", "--path", str(project)], work)
    (project / "src/main_test.cj").write_text(examples[("toolchain.md", 1)], encoding="utf-8")
    shutil.copyfile(SKILL / "scripts/sdk_semantics_test.cj", project / "src/semantics_test.cj")
    runner.run("build-release", ["cjpm", "build"], project)
    runner.run("run-release", ["cjpm", "run"], project)
    runner.run("build-debug", ["cjpm", "build", "-g"], project)
    report_flags = ["--no-color", "--no-progress", "--report-format=xml"]
    runner.run("test-compile-only", ["cjpm", "test", "--no-run", *report_flags], project)
    runner.run("test-release", ["cjpm", "test", *report_flags, "--report-path=reports-release"], project)
    verify_xml(project / "reports-release", 13)
    runner.run("test-debug", ["cjpm", "test", "-g", *report_flags, "--report-path=reports-debug"], project)
    verify_xml(project / "reports-debug", 13)
    runner.run("test-filter", ["cjpm", "test", "--filter=SmokeTests.*", *report_flags, "--report-path=reports-filter"], project)
    verify_xml(project / "reports-filter", 1, expected_skipped=12)
    runner.run("test-coverage", ["cjpm", "test", "--coverage", *report_flags, "--report-path=reports-coverage"], project)
    verify_xml(project / "reports-coverage", 13)
    coverage = project / "cov_output"
    if not list(coverage.rglob("*.gcda")) or not list(coverage.rglob("*.gcno")):
        raise RuntimeError("Coverage run did not produce both .gcda and .gcno data.")

    for name, code in NEGATIVE.items():
        case = work / name
        case.mkdir()
        (case / "main.cj").write_text(code, encoding="utf-8")
        runner.run(name, ["cjc", "main.cj", "-o", "main"], case, expected_code=None)
    return {"compiler": compiler.strip(), "cjpm": manager.strip(), "code_blocks": 4, "semantic_tests": 12, "negative_tests": len(NEGATIVE)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, help="New empty directory for sources, builds and logs")
    args = parser.parse_args()
    for tool in ("cjc", "cjpm"):
        if not shutil.which(tool):
            parser.error(f"{tool} not found; activate your installed SDK environment first")
    if args.work_dir:
        work = args.work_dir.expanduser().resolve()
        work.mkdir(parents=True, exist_ok=False)
    else:
        work = Path(tempfile.mkdtemp(prefix="cangjie-sdk-tests-"))
    runner = Runner(work)
    print(f"Work directory: {work}", flush=True)
    summary = {"passed": False, "work_dir": str(work)}
    try:
        summary.update(verify(runner))
        summary["passed"] = True
        return 0
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ET.ParseError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    finally:
        summary["commands"] = runner.results
        report = work / "results.json"
        report.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Results: {report}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
