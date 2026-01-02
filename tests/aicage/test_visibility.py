from pathlib import Path
from unittest import TestCase


class VisibilityRulesTests(TestCase):
    def test_src_has_no_all(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        src_dir = repo_root / "src"
        violations = []
        for path in src_dir.rglob("*.py"):
            if "__all__" in path.read_text(encoding="utf-8"):
                violations.append(path.relative_to(repo_root))

        self.assertEqual([], violations, f"Found __all__ usage: {violations}")
