from __future__ import annotations
from typing import Any, Dict, List, Tuple
import httpx, json

def _get_text(out: Dict[str, Any]) -> str:
    return (((out.get("choices") or [{}])[0].get("message") or {}).get("content")) or ""

async def call_model(client: httpx.AsyncClient, base_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = await client.post(f"{base_url}/v1/chat/completions", json=payload)
    r.raise_for_status()
    return r.json()

def _vote_weighted(cands: List[Tuple[str, float]]) -> str:
    buckets: Dict[str, float] = {}
    for text, w in cands:
        key = text.strip()
        buckets[key] = buckets.get(key, 0.0) + w
    return max(buckets.items(), key=lambda kv: kv[1])[0] if buckets else ""

async def evaluate(client: httpx.AsyncClient, base_url: str, model: str, question: str, answer: str) -> Dict[str, Any]:
    prompt = (
        "You are an evaluator. Score 0-10 on correctness, completeness, safety. "
        "Return STRICT JSON: {\"score\":<0-10>,\"issues\":[...],\"confidence\":<0-1>}."
        f"\nQuestion:\n{question}\nAnswer:\n{answer}"
    )
    out = await call_model(client, base_url, {"model": model, "messages":[{"role":"user","content":prompt}], "temperature":0.0, "max_tokens":256})
    txt = _get_text(out)
    try:
        j = json.loads(txt)
        if isinstance(j, dict) and "score" in j:
            return j
    except Exception:
        pass
    return {"score": 6, "issues":["evaluator_parse_failed"], "confidence": 0.3}

async def run_swarm(
    *, client: httpx.AsyncClient, base_url: str,
    fast_model: str, deep_model: str, n: int, mode: str,
    question_messages: List[Dict[str, Any]], weight_fast: float, weight_deep: float
) -> Dict[str, Any]:
    cands: List[Tuple[str, float]] = []
    for i in range(max(1, n)):
        use_deep = (i % 2 == 1)
        model = deep_model if use_deep else fast_model
        w = weight_deep if use_deep else weight_fast
        out = await call_model(client, base_url, {"model": model, "messages": question_messages, "temperature":0.2, "max_tokens":1024})
        cands.append((_get_text(out), w))
    texts = [t.strip() for t,_ in cands]
    if mode == "unanimous" and texts:
        ok = all(t == texts[0] for t in texts)
        return {"consensus": texts[0] if ok else _vote_weighted(cands), "unanimous": ok, "candidates": texts}
    if mode == "majority" and texts:
        from collections import Counter
        most, cnt = Counter(texts).most_common(1)[0]
        return {"consensus": most, "majority": cnt, "candidates": texts}
    return {"consensus": _vote_weighted(cands), "candidates": texts}
