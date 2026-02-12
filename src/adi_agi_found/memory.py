from __future__ import annotations
import sqlite3, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

SCHEMA = r'''
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS facts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object TEXT NOT NULL,
  polarity TEXT NOT NULL,
  confidence REAL NOT NULL,
  provenance TEXT,
  created_ts INTEGER
);
CREATE INDEX IF NOT EXISTS idx_facts_sp ON facts(subject, predicate);

CREATE TABLE IF NOT EXISTS contradictions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fact_a_id INTEGER NOT NULL,
  fact_b_id INTEGER NOT NULL,
  reason TEXT NOT NULL,
  created_ts INTEGER,
  FOREIGN KEY(fact_a_id) REFERENCES facts(id),
  FOREIGN KEY(fact_b_id) REFERENCES facts(id)
);
CREATE INDEX IF NOT EXISTS idx_contra_facta ON contradictions(fact_a_id);
'''

@dataclass
class Memory:
    path: str

    def _conn(self) -> sqlite3.Connection:
        Path(self.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self._conn() as c:
            c.executescript(SCHEMA)

    def upsert_fact(self, subject: str, predicate: str, object_: str, polarity: str, confidence: float, provenance: str) -> int:
        ts = int(time.time())
        polarity = (polarity or "true").strip().lower()
        if polarity not in ("true","false"):
            polarity = "true"
        confidence = float(confidence)
        with self._conn() as c:
            c.execute(
                "INSERT INTO facts(subject,predicate,object,polarity,confidence,provenance,created_ts) VALUES (?,?,?,?,?,?,?)",
                (subject, predicate, object_, polarity, confidence, provenance, ts),
            )
            fid = int(c.execute("SELECT last_insert_rowid() AS id").fetchone()["id"])

            rows = c.execute(
                "SELECT id, object, polarity, confidence FROM facts WHERE subject=? AND predicate=? AND id<>?",
                (subject, predicate, fid),
            ).fetchall()

            for r in rows:
                other_id = int(r["id"])
                other_obj = str(r["object"])
                other_pol = str(r["polarity"])
                other_conf = float(r["confidence"])
                reason = None
                if other_obj == object_ and other_pol != polarity and (other_conf >= 0.7 and confidence >= 0.7):
                    reason = "opposite_polarity_same_object"
                elif other_obj != object_ and other_pol == "true" and polarity == "true" and (other_conf >= 0.8 and confidence >= 0.8):
                    reason = "different_object_same_subject_predicate"
                if reason:
                    c.execute(
                        "INSERT INTO contradictions(fact_a_id,fact_b_id,reason,created_ts) VALUES (?,?,?,?)",
                        (fid, other_id, reason, ts),
                    )
            return fid

    def contradictions(self, subject: str, predicate: str) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT ct.id as contradiction_id, ct.reason, "
                "fa.subject as subject, fa.predicate as predicate, "
                "fa.object as object_a, fa.polarity as polarity_a, fa.confidence as conf_a, fa.provenance as prov_a, "
                "fb.object as object_b, fb.polarity as polarity_b, fb.confidence as conf_b, fb.provenance as prov_b "
                "FROM contradictions ct "
                "JOIN facts fa ON ct.fact_a_id=fa.id "
                "JOIN facts fb ON ct.fact_b_id=fb.id "
                "WHERE fa.subject=? AND fa.predicate=? "
                "ORDER BY ct.created_ts DESC LIMIT 200",
                (subject, predicate),
            ).fetchall()
            return [dict(r) for r in rows]
