import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sys

import test_sdk as sdk


class SDKRunnerTests(unittest.TestCase):
    def test_example_inventory_without_sdk(self):
        self.assertEqual(sdk.collect_examples().keys(), sdk.EXPECTED.keys())

    def test_unregistered_example_fails(self):
        with patch.object(sdk, "EXPECTED", {}):
            with self.assertRaisesRegex(RuntimeError, "Example set changed"):
                sdk.collect_examples()

    def test_timeout_and_start_failure_are_logged(self):
        errors = [
            subprocess.TimeoutExpired(["cjc"], 120, output=b"partial output", stderr=b"partial error"),
            FileNotFoundError("cjc missing"),
        ]
        for error in errors:
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                runner = sdk.Runner(Path(directory))
                with patch.object(sdk.subprocess, "run", side_effect=error):
                    with self.assertRaises(RuntimeError):
                        runner.run("compile", ["cjc"], Path(directory))
                result = runner.results[0]
                self.assertFalse(result["passed"])
                self.assertIsNone(result["exit_code"])
                self.assertEqual(result["timed_out"], isinstance(error, subprocess.TimeoutExpired))
                text = Path(result["log"]).read_text()
                self.assertIn("cjc", text)
                if result["timed_out"]:
                    self.assertIn("partial output", text)
                    self.assertIn("partial error", text)

    def test_success_and_warnings(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            runner = sdk.Runner(Path(directory))
            with patch.object(sdk.subprocess, "run", return_value=subprocess.CompletedProcess(["cjc"], 0, "7\n", "")):
                self.assertEqual(runner.run("ok", ["cjc"], Path(directory), output="7\n"), "7\n")
            with patch.object(sdk.subprocess, "run", return_value=subprocess.CompletedProcess(["cjc"], 0, "", "warning: issue")):
                with self.assertRaises(RuntimeError):
                    runner.run("warn", ["cjc"], Path(directory))

    def test_main_preserves_failed_command_in_results_json(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "work"
            with patch.object(sys, "argv", ["test_sdk.py", "--work-dir", str(work)]):
                with patch.object(sdk.shutil, "which", return_value="tool"):
                    with patch.object(sdk.subprocess, "run", side_effect=subprocess.TimeoutExpired(["cjc"], 120, output=b"diagnostic")):
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                            self.assertEqual(sdk.main(), 1)
            report = json.loads((work / "results.json").read_text())
            self.assertFalse(report["passed"])
            self.assertEqual(len(report["commands"]), 1)
            self.assertTrue(report["commands"][0]["timed_out"])

    def test_xml_counts_skips_and_assertions(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            report = Path(directory) / "report.xml"
            report.write_text('<testsuite><testcase assertions="1"/><testcase><skipped/></testcase></testsuite>')
            sdk.verify_xml(Path(directory), 1, 1)
            with self.assertRaises(RuntimeError):
                sdk.verify_xml(Path(directory), 2)
            for case in ('<testcase assertions="0"/>', '<testcase assertions="1"><failure/></testcase>'):
                report.write_text(f"<testsuite>{case}</testsuite>")
                with self.assertRaises(RuntimeError):
                    sdk.verify_xml(Path(directory), 1)
