"""Site Validation (spec §9.4, §9.6, §7.6): links, disclaimers, scientific checklist, headless layout."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from validate import gate_site  # noqa: E402


class TestSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = gate_site(ROOT)

    def test_all_checks(self):
        for label, ok, detail in self.gate.checks:
            with self.subTest(label):
                self.assertTrue(ok, detail)


if __name__ == "__main__":
    unittest.main()
