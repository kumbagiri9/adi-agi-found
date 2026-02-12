import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((ROOT / "src").resolve()))
loader = unittest.TestLoader()
suite = unittest.TestSuite()
suite.addTests(loader.discover(str(Path(__file__).parent), pattern="test_*.py"))
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
