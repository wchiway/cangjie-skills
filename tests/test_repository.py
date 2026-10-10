from pathlib import Path
import re
import unittest

import cloud_docs


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/cangjie"


class RepositoryTests(unittest.TestCase):
    def test_catalog_integrity(self):
        rows = cloud_docs.load_catalog()
        paths = set()
        self.assertTrue(rows)
        for row in rows:
            with self.subTest(path=row.get("path")):
                path = row["path"]
                self.assertNotIn(path, paths)
                paths.add(path)
                self.assertTrue(path.startswith("docs/"))
                self.assertNotIn("..", path.split("/"))
                self.assertRegex(row["sha256"], r"^[a-f0-9]{64}$")
                self.assertIs(type(row["bytes"]), int)
                self.assertGreaterEqual(row["bytes"], 0)
                self.assertIn(row["language"], {"zh", "en", "shared"})
                self.assertIn(row["kind"], {"markdown", "image"})
                if row["kind"] == "markdown":
                    cloud_docs.validate_path(path)
                    self.assertIsInstance(row["title"], str)
                    self.assertIsInstance(row["headings"], list)
                    self.assertTrue(all(isinstance(heading, str) for heading in row["headings"]))
                    self.assertIs(type(row["lines"]), int)
                    self.assertGreaterEqual(row["lines"], 0)

    def test_relative_links_exist_and_references_are_reachable(self):
        documents = [ROOT / "README.md", SKILL / "SKILL.md", SKILL / "NOTICE.md", *sorted((SKILL / "references").glob("*.md"))]
        graph = {}
        for document in documents:
            targets = []
            for link in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                if "://" in link or link.startswith("#"):
                    continue
                target = (document.parent / link.split("#")[0]).resolve()
                self.assertTrue(target.exists(), f"Broken link in {document}: {link}")
                targets.append(target)
            graph[document.resolve()] = targets
        pending, visited = [(SKILL / "SKILL.md").resolve()], set()
        while pending:
            document = pending.pop()
            if document not in visited:
                visited.add(document)
                pending.extend(graph.get(document, []))
        self.assertTrue(set((SKILL / "references").glob("*.md")) <= visited)

    def test_cited_document_files_exist_in_catalog(self):
        paths = {row["path"] for row in cloud_docs.load_catalog()}
        for document in (SKILL / "references").glob("*.md"):
            for path in re.findall(r"`(docs/[^`\s]+\.md)`", document.read_text(encoding="utf-8")):
                self.assertIn(path, paths, f"Unknown citation in {document}")

    def test_standalone_license_matches_root(self):
        self.assertEqual((ROOT / "LICENSE").read_bytes(), (SKILL / "LICENSE").read_bytes())
        self.assertIn(cloud_docs.SNAPSHOT, (SKILL / "NOTICE.md").read_text())

    def test_ui_metadata_uses_documented_fields(self):
        # Metadata is deliberately a small scalar-only YAML subset (no dependency needed).
        text = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        allowed = {"interface", "policy", "display_name", "short_description", "default_prompt", "brand_color", "icon_small", "icon_large", "allow_implicit_invocation"}
        for key in re.findall(r"^\s*([a-z_]+):", text, re.M):
            self.assertIn(key, allowed)
        self.assertIn("$cangjie", text)
        for asset in re.findall(r'icon_(?:small|large): "([^"]+)"', text):
            self.assertTrue((SKILL / asset).is_file())
