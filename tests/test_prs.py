"""PRS Validation (spec §9.5): Python reference and the real browser JS against shared cases."""
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from validate import prs_reference  # noqa: E402

CASES = json.loads((ROOT / "tests/prs_cases.json").read_text(encoding="utf-8"))


class TestPRSReference(unittest.TestCase):
    def test_expected_values(self):
        for c in CASES["cases"]:
            with self.subTest(c["name"]):
                self.assertAlmostEqual(prs_reference(c["snps"]), c["expected"], places=9)

    def test_invalid_dosage_rejected(self):
        for c in CASES["invalid"]:
            with self.subTest(c["name"]):
                with self.assertRaises(ValueError):
                    prs_reference(c["snps"])

    def test_required_scenarios_covered(self):
        tags = {t for c in CASES["cases"] for t in c["tags"]}
        for need in ("hom_ref", "het", "hom_alt", "negative_beta", "multi_snp", "fractional_dosage"):
            self.assertIn(need, tags)


@unittest.skipUnless(shutil.which("node"), "node not installed")
class TestPRSBrowserCode(unittest.TestCase):
    def test_js_matches_cases(self):
        proc = subprocess.run(["node", str(ROOT / "tests/run_prs_js.js"), str(ROOT)],
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
