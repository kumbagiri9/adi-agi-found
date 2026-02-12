from __future__ import annotations
import threading
from typing import Dict
_lock = threading.Lock()
_counters: Dict[str, int] = {}
def inc(name: str, n: int = 1) -> None:
    with _lock:
        _counters[name] = _counters.get(name, 0) + n
def render() -> str:
    with _lock:
        lines = []
        for k, v in sorted(_counters.items()):
            metric = k.replace(".", "_").replace("-", "_")
            lines.append(f"# TYPE {metric} counter")
            lines.append(f"{metric} {v}")
        return "\n".join(lines) + "\n"
