from __future__ import annotations
import asyncio
from typing import Callable, Awaitable, TypeVar
T = TypeVar("T")
async def with_retries(fn: Callable[[], Awaitable[T]], retries: int, base_delay: float, max_delay: float) -> T:
    delay = base_delay
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await fn()
        except Exception as e:
            last = e
            if attempt >= retries:
                raise
            await asyncio.sleep(delay)
            delay = min(max_delay, delay * 2)
    raise last or RuntimeError("retry failed")
