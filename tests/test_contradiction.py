import sys, tempfile, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((ROOT / "src").resolve()))
import unittest
from adi_agi_found.memory import Memory

class TestContradiction(unittest.TestCase):
    def test_contradiction_diff_object(self):
        with tempfile.TemporaryDirectory() as td:
            db = os.path.join(td, "m.sqlite3")
            m = Memory(db); m.init()
            m.upsert_fact("A","has","X","true",0.9,"p1")
            m.upsert_fact("A","has","Y","true",0.9,"p2")
            cs = m.contradictions("A","has")
            self.assertTrue(len(cs) >= 1)

if __name__ == "__main__":
    unittest.main()
