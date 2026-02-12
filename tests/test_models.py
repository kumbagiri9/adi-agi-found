import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((ROOT / "src").resolve()))
import unittest
from fastapi.testclient import TestClient
from adi_agi_found.api import app

class TestModels(unittest.TestCase):
    def test_models_list(self):
        c = TestClient(app)
        r = c.get("/v1/models")
        self.assertEqual(r.status_code, 200)
        ids = [m["id"] for m in r.json()["data"]]
        self.assertIn("adi-agi-found-swarm", ids)

if __name__ == "__main__":
    unittest.main()
