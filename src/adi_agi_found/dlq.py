from __future__ import annotations
import json, time
from pathlib import Path
from typing import Any, Dict
def push(path: str, event: Dict[str, Any]) -> None:
    p = Path(path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    evt = dict(event)
    evt.setdefault("ts", int(time.time()))
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evt, ensure_ascii=False) + "\n")
