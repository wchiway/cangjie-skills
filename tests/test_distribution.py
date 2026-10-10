import contextlib
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import install_skill
import package_skill
from skill_files import payload_files


class DistributionTests(unittest.TestCase):
    def test_install_is_complete_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skills/cangjie"
            self.assertGreater(install_skill.install(target), 10)
            for source, relative in payload_files():
                self.assertEqual(source.read_bytes(), (target / relative).read_bytes())
            marker = target / "user.txt"
            marker.write_text("keep")
            with self.assertRaises(FileExistsError):
                install_skill.install(target)
            self.assertEqual(marker.read_text(), "keep")

    def test_dry_run_and_assistant_locations(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            project = Path(directory)
            for assistant, location in install_skill.LOCATIONS.items():
                self.assertEqual(install_skill.main(["--assistant", assistant, "--project", directory, "--dry-run"]), 0)
                self.assertFalse((project / location).exists())
            self.assertEqual(install_skill.main(["--assistant", "claude", "--project", directory]), 0)
            self.assertTrue((project / ".claude/skills/cangjie/LICENSE").is_file())

    def test_existing_destination_is_reported(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(install_skill.main(["--destination", directory]), 1)

    def test_archive_is_reproducible_and_self_contained(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            archive = package_skill.package(output)
            original = archive.read_bytes()
            package_skill.package(output)
            self.assertEqual(original, archive.read_bytes())
            self.assertEqual((output / "SHA256SUMS").read_text().split()[0], hashlib.sha256(original).hexdigest())
            with zipfile.ZipFile(archive) as stream:
                names = stream.namelist()
                self.assertIn("cangjie/LICENSE", names)
                self.assertIn("cangjie/NOTICE.md", names)
                self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))
                stream.extractall(output / "unpacked")
            skill = output / "unpacked/cangjie"
            result = subprocess.run([sys.executable, "-B", str(skill / "scripts/cloud_docs.py"), "search", "Option", "--lang", "all"], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([sys.executable, "-B", str(skill / "scripts/test_cloud_docs.py")], capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
