"""Discover repository tests without installing the skill or a Cangjie SDK."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/cangjie/scripts"))
