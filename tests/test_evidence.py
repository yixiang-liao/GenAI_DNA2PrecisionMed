"""Evidence & Wiki Validation (spec §9.1-9.4): gates pass on the repo and catch injected faults."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from validate import GATE_FUNCS, inject  # noqa: E402

CONTENT_GATES = ("sources", "evidence", "wiki", "slides")
FAULTS = ("bad-source-id", "unverified-source", "dangling-relation", "missing-advanced", "slide-count", "fake-quote")


class TestGatesPassOnRepo(unittest.TestCase):
    def test_content_gates(self):
        for name in CONTENT_GATES:
            with self.subTest(name):
                g = GATE_FUNCS[name](ROOT)
                self.assertTrue(g.passed, [c for c in g.checks if not c[1]])


class TestGatesCatchInjectedFaults(unittest.TestCase):
    """Reproducible test cases (RTC): each deliberate fault must fail its gate."""

    def test_faults_caught(self):
        for case in FAULTS:
            with self.subTest(case), tempfile.TemporaryDirectory() as tmp:
                copy = Path(tmp) / "repo"
                shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git"))
                gate = inject(copy, case)
                self.assertFalse(GATE_FUNCS[gate](copy).passed, f"{case} not caught by {gate}")


if __name__ == "__main__":
    unittest.main()
