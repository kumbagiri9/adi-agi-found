from __future__ import annotations
from typing import Any, Dict
import httpx

async def openai_chat(client: httpx.AsyncClient, base_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = await client.post(f"{base_url}/v1/chat/completions", json=payload)
    r.raise_for_status()
    return r.json()
