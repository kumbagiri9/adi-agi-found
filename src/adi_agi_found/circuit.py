from __future__ import annotations
import time
from dataclasses import dataclass
@dataclass
class CircuitState:
    failures: int = 0
    opened_at: float | None = None
    def is_open(self, threshold: int, reset_seconds: int) -> bool:
        if self.opened_at is None:
            return False
        if (time.time() - self.opened_at) >= reset_seconds:
            self.opened_at = None
            self.failures = 0
            return False
        return True
    def record_success(self):
        self.failures = 0
        self.opened_at = None
    def record_failure(self, threshold: int):
        self.failures += 1
        if self.failures >= threshold and self.opened_at is None:
            self.opened_at = time.time()
