#!/usr/bin/env python3
"""Test cloud retrieval without needing a document checkout or live network."""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

import cloud_docs as docs


class CloudDocsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name) / "cache"
        self.path = "docs/dev-guide/source_zh_cn/topic.md"
        self.body = "# Option\n?T means Option<T>.\nNone is empty.\n"
        self.catalog = [{
            "path": self.path, "title": "Option", "headings": ["Named parameters"],
            "language": "zh", "kind": "markdown",
            "sha256": hashlib.sha256(self.body.encode()).hexdigest(),
        }]

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(docs, "load_catalog", return_value=self.catalog):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = docs.main(["--cache-dir", str(self.cache), *args])
        return code, out.getvalue(), err.getvalue()

    def test_search_is_catalog_only_without_network_or_checkout(self):
        with patch.object(docs, "download") as download:
            code, out, _ = self.run_cli("search", "parameters")
        self.assertEqual(code, 0)
        self.assertIn(self.path, out)
        self.assertIn("NOT live full-text", out)
        download.assert_not_called()
        self.assertFalse(self.cache.exists())

    def test_search_filters_and_no_match(self):
        self.assertEqual(self.run_cli("search", "Option", "--lang", "en")[0], 1)
        self.assertEqual(self.run_cli("search", "Option", "--area", "tools")[0], 1)
        self.assertEqual(self.run_cli("search", "missing")[0], 1)
        self.assertEqual(self.run_cli("search", "  ")[0], 2)

    def test_url_encodes_branch_and_does_not_fetch(self):
        with patch.object(docs, "download") as download:
            code, out, _ = self.run_cli("--ref", "release/1.1", "url", self.path)
        self.assertEqual(code, 0)
        self.assertIn("release%2F1.1", out)
        download.assert_not_called()

    def test_read_downloads_only_requested_file_then_uses_cache(self):
        with patch.object(docs, "download", return_value=self.body) as download:
            code, out, _ = self.run_cli("read", self.path, "--start", "2", "--end", "2")
            self.assertEqual(code, 0)
            self.assertIn("2: ?T", out)
            self.assertNotIn("3: None", out)
            self.assertEqual(self.run_cli("read", self.path)[0], 0)
        self.assertEqual(download.call_count, 1)
        self.assertEqual(len(list(self.cache.iterdir())), 1)

    def test_refresh_ignores_cache(self):
        with patch.object(docs, "download", return_value=self.body) as download:
            self.run_cli("read", self.path)
            self.run_cli("--refresh", "read", self.path)
        self.assertEqual(download.call_count, 2)

    def test_pinned_commit_falls_back_without_changing_ref(self):
        with patch.object(docs, "download", side_effect=[URLError("unavailable"), self.body]) as download:
            code, out, _ = self.run_cli("read", self.path)
        self.assertEqual(code, 0)
        self.assertIn("raw.githubusercontent.com", out)
        self.assertEqual(download.call_count, 2)
        self.assertTrue(all(docs.SNAPSHOT in call.args[0] for call in download.call_args_list))

    def test_branch_does_not_silently_switch_mirrors(self):
        with patch.object(docs, "download", side_effect=URLError("unavailable")) as download:
            code, _, err = self.run_cli("--ref", "main", "read", self.path)
        self.assertEqual(code, 2)
        self.assertEqual(download.call_count, 1)
        self.assertIn("No version was substituted", err)

    def test_branch_cache_expires(self):
        with patch.object(docs, "download", return_value=self.body) as download:
            with patch.object(docs.time, "time", return_value=1000):
                self.run_cli("--ref", "main", "read", self.path)
            with patch.object(docs.time, "time", return_value=1400):
                self.run_cli("--ref", "main", "read", self.path)
        self.assertEqual(download.call_count, 2)

    def test_expired_branch_cache_is_not_silent_network_fallback(self):
        with patch.object(docs, "download", return_value=self.body):
            with patch.object(docs.time, "time", return_value=1000):
                self.run_cli("--ref", "main", "read", self.path)
        with patch.object(docs, "download", side_effect=URLError("offline")):
            with patch.object(docs.time, "time", return_value=1400):
                code, out, _ = self.run_cli("--ref", "main", "read", self.path)
        self.assertEqual(code, 2)
        self.assertNotIn("?T means", out)

    def test_cache_is_isolated_by_ref_and_source(self):
        with patch.object(docs, "download", return_value=self.body) as download:
            self.run_cli("read", self.path)
            self.run_cli("--ref", "main", "read", self.path)
            self.run_cli("--source", "github", "read", self.path)
        self.assertEqual(download.call_count, 3)
        self.assertEqual(len(list(self.cache.iterdir())), 3)

    def test_unwritable_cache_does_not_hide_download_success(self):
        self.cache.write_text("not a directory")
        with patch.object(docs, "download", return_value=self.body):
            code, out, err = self.run_cli("read", self.path)
        self.assertEqual(code, 0)
        self.assertIn("?T means", out)
        self.assertIn("cache could not be saved", err)

    def test_offline_cache_is_explicit_and_never_fetches(self):
        with patch.object(docs, "download", return_value=self.body):
            self.run_cli("read", self.path)
        with patch.object(docs, "download") as download:
            code, out, _ = self.run_cli("--offline", "read", self.path)
            self.assertEqual(self.run_cli("--offline", "read", "docs/other/missing.md")[0], 2)
        self.assertEqual(code, 0)
        self.assertIn("offline cache", out)
        download.assert_not_called()

    def test_corrupt_cache_is_not_trusted(self):
        with patch.object(docs, "download", return_value=self.body):
            self.run_cli("read", self.path)
        cache_file = next(self.cache.iterdir())
        item = json.loads(cache_file.read_text())
        item["text"] = "corrupted"
        cache_file.write_text(json.dumps(item))
        self.assertEqual(self.run_cli("--offline", "read", self.path)[0], 2)

    def test_malformed_cache_shapes_are_handled(self):
        with patch.object(docs, "download", return_value=self.body):
            self.run_cli("read", self.path)
        cache_file = next(self.cache.iterdir())
        for item in ([1], {"text": 42}, None):
            cache_file.write_text(json.dumps(item))
            self.assertEqual(self.run_cli("--offline", "read", self.path)[0], 2)

    def test_rejects_html_empty_oversize_and_wrong_hash(self):
        for raw in (b"<!DOCTYPE html><html>login</html>", b"", b"x" * (docs.MAX_BYTES + 1)):
            with self.assertRaises(ValueError):
                docs.validate_body(raw)
        with self.assertRaises(ValueError):
            docs.validate_body(b"# Changed", self.catalog[0]["sha256"])

    def test_download_passes_timeout_and_validates_response(self):
        class Response:
            status = 200
            headers = {"Content-Type": "text/plain"}

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def geturl(self):
                return "https://raw.gitcode.com/document"

            def read(self, limit):
                return b"# Document"

        with patch.object(docs, "urlopen", return_value=Response()) as request:
            self.assertEqual(docs.download("https://raw.gitcode.com/document"), "# Document")
        self.assertEqual(request.call_args.kwargs["timeout"], 20)
        Response.headers = {"Content-Type": "text/html"}
        with patch.object(docs, "urlopen", return_value=Response()):
            with self.assertRaises(ValueError):
                docs.download("https://raw.gitcode.com/document")

    def test_wrong_snapshot_hash_is_forwarded_and_rejected(self):
        def incorrect_content(url, expected_hash):
            self.assertEqual(expected_hash, self.catalog[0]["sha256"])
            return docs.validate_body(b"# Changed", expected_hash)

        with patch.object(docs, "download", side_effect=incorrect_content):
            code, out, err = self.run_cli("read", self.path)
        self.assertEqual(code, 2)
        self.assertIn("SHA-256", err)
        self.assertNotIn("1: # Changed", out)
        self.assertFalse(self.cache.exists())

    def test_bad_paths_refs_and_line_ranges_fail_before_network(self):
        with patch.object(docs, "download") as download:
            for path in ("/etc/passwd", "docs/../secret.md", "https://example.com/x.md", "docs/a//b.md", "docs/a\\b.md"):
                self.assertEqual(self.run_cli("read", path)[0], 2)
            self.assertEqual(self.run_cli("--ref", "../main", "read", self.path)[0], 2)
            self.assertEqual(self.run_cli("read", self.path, "--start", "3", "--end", "2")[0], 2)
        download.assert_not_called()


if __name__ == "__main__":
    unittest.main()
