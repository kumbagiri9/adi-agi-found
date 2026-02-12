import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((ROOT / "src").resolve()))
import unittest
from adi_agi_found.sandbox import run_python_sandbox

class TestSandbox(unittest.TestCase):
    def test_math_ok(self):
        out = run_python_sandbox("import math\nprint(math.sqrt(81))\n2+2", workdir=str(ROOT/"data"/"sandbox_work"), timeout_sec=2.0)
        self.assertTrue(out["ok"])
        self.assertIn("9.0", out.get("stdout",""))
        self.assertEqual(out.get("result"), 4)

    def test_blocks_attribute(self):
        out = run_python_sandbox("x=1\nx.__class__", workdir=str(ROOT/"data"/"sandbox_work"), timeout_sec=2.0)
        self.assertFalse(out["ok"])

if __name__ == "__main__":
    unittest.main()
