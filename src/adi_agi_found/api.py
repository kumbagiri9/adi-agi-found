from __future__ import annotations
from typing import Any, Dict, List
import time
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse

from .config import Settings
from .retry import with_retries
from .dlq import push as dlq_push
from .audit import write as audit_write, new_trace_id
from .metrics import inc as metric_inc, render as metrics_render
from .circuit import CircuitState
from .router import alias_map, resolve_backend_model
from .backends import openai_chat
from .memory import Memory
from .verifier import verify_response
from .swarm import run_swarm, evaluate
from .sandbox import run_python_sandbox

settings = Settings()
app = FastAPI(title="adi-agi-found", version="3.1.1")

memory = Memory(settings.memory_db_path)
memory.init()

circuit = CircuitState()

def require_auth(req: Request):
    if not settings.api_key:
        return
    if req.headers.get("authorization","") != f"Bearer {settings.api_key}":
        raise HTTPException(status_code=401, detail="unauthorized")

@app.get("/health")
async def health():
    return {"status":"ok","backend": settings.backend, "ts": int(time.time())}

@app.get("/metrics")
async def metrics():
    return PlainTextResponse(metrics_render(), media_type="text/plain; version=0.0.4")

@app.get("/v1/models")
async def models(req: Request):
    require_auth(req)
    data = [{"id": settings.alias_7b, "object":"model", "owned_by":"adi"},
            {"id": settings.alias_30b, "object":"model", "owned_by":"adi"},
            {"id": settings.alias_70b, "object":"model", "owned_by":"adi"},
            {"id": settings.alias_auto, "object":"model", "owned_by":"adi"},
            {"id": settings.alias_mm, "object":"model", "owned_by":"adi"},
            {"id": settings.alias_swarm, "object":"model", "owned_by":"adi"}]
    return {"object":"list","data": data}

@app.post("/v1/tools/execute")
async def tools_execute(req: Request):
    require_auth(req)
    body = await req.json()
    tool = str(body.get("tool","python")).strip().lower()
    if tool != "python":
        raise HTTPException(status_code=400, detail="tool not allowlisted")
    code = body.get("code")
    if not isinstance(code, str) or not code.strip():
        raise HTTPException(status_code=400, detail="code required")
    timeout = float(body.get("timeout_sec") or settings.sandbox_timeout_sec)
    metric_inc("sandbox_exec_total")
    return JSONResponse(run_python_sandbox(code, workdir=settings.sandbox_workdir, timeout_sec=timeout))

@app.post("/v1/memory/facts/upsert")
async def memory_facts_upsert(req: Request):
    require_auth(req)
    body = await req.json()
    facts = body.get("facts") or []
    ids = []
    for f in facts:
        subject = str(f.get("subject","")).strip()
        predicate = str(f.get("predicate","")).strip()
        object_ = str(f.get("object","")).strip()
        polarity = str(f.get("polarity","true")).strip().lower()
        confidence = float(f.get("confidence", 0.8))
        provenance = str(f.get("provenance","unknown"))
        if subject and predicate and object_:
            ids.append(memory.upsert_fact(subject, predicate, object_, polarity, confidence, provenance))
    metric_inc("memory_facts_upsert_total")
    return {"ok": True, "ids": ids}

@app.post("/v1/memory/contradictions/query")
async def memory_contradictions_query(req: Request):
    require_auth(req)
    body = await req.json()
    subject = str(body.get("subject","")).strip()
    predicate = str(body.get("predicate","")).strip()
    if not subject or not predicate:
        raise HTTPException(status_code=400, detail="subject and predicate required")
    metric_inc("memory_contradictions_query_total")
    return {"contradictions": memory.contradictions(subject, predicate)}

@app.post("/v1/chat/completions")
async def chat(req: Request):
    require_auth(req)
    trace_id = req.headers.get("x-trace-id") or new_trace_id()
    body = await req.json()
    alias = str(body.get("model",""))
    mapping = alias_map(settings)
    if alias not in mapping:
        raise HTTPException(status_code=400, detail=f"unknown model alias: {alias}")

    if circuit.is_open(settings.circuit_fail_threshold, settings.circuit_reset_seconds):
        metric_inc("circuit_open_total")
        raise HTTPException(status_code=503, detail="backend_circuit_open")

    route_hint = req.headers.get("x-adi-route") or (body.get("metadata") or {}).get("route")
    backend_model = resolve_backend_model(settings, alias, mapping, body, route_hint)
    stream = bool(body.get("stream", False))
    messages = body.get("messages") or []

    audit_write(settings.audit_path, {"trace_id": trace_id, "event":"request", "alias": alias})

    async with httpx.AsyncClient(timeout=None) as client:
        # Swarm alias is implemented by sampling multiple times using upstream models
        if alias == settings.alias_swarm:
            metric_inc("swarm_requests_total")
            q_text = ""
            for m in messages:
                c = m.get("content")
                if isinstance(c, str):
                    q_text += c + "\n"
            swarm = await run_swarm(
                client=client, base_url=settings.vllm_text_base_url,
                fast_model=settings.model_id_7b, deep_model=settings.model_id_70b,
                n=settings.swarm_n, mode=settings.swarm_mode,
                question_messages=messages,
                weight_fast=settings.swarm_weight_fast, weight_deep=settings.swarm_weight_deep,
            )
            consensus = swarm.get("consensus","")

            ev_fast = await evaluate(client, settings.vllm_text_base_url, settings.model_id_7b, q_text, consensus)
            ev_deep = await evaluate(client, settings.vllm_text_base_url, settings.model_id_70b, q_text, consensus)
            ver = verify_response(consensus) if settings.swarm_require_verifier else {"ok": True}

            ok = (ev_fast.get("score",0) >= 7) and (ev_deep.get("score",0) >= 7) and bool(ver.get("ok", True))
            if not ok:
                metric_inc("swarm_gate_fail_total")
                repair_prompt = f"Improve and fix issues. FAST_EVAL={ev_fast} DEEP_EVAL={ev_deep} VERIFIER={ver}. Return improved answer only."
                repaired = await openai_chat(client, settings.vllm_text_base_url, {
                    "model": settings.model_id_70b,
                    "messages": messages + [{"role":"user","content":repair_prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1200
                })
                consensus = (((repaired.get("choices") or [{}])[0].get("message") or {}).get("content")) or consensus

            out = {
                "id": f"swarm-{trace_id}",
                "object": "chat.completion",
                "model": alias,
                "choices": [{"index":0, "message":{"role":"assistant","content": consensus}, "finish_reason":"stop"}],
                "meta": {"trace_id": trace_id, "swarm": swarm, "eval_fast": ev_fast, "eval_deep": ev_deep, "verifier": ver},
            }
            audit_write(settings.audit_path, {"trace_id": trace_id, "event":"response", "alias": alias, "ok": True})
            circuit.record_success()
            return JSONResponse(out)

        payload = dict(body)
        payload["model"] = backend_model
        payload["messages"] = messages

        if stream:
            metric_inc("stream_requests_total")
            async def gen():
                try:
                    async with client.stream("POST", f"{settings.vllm_text_base_url}/v1/chat/completions", json=payload) as r:
                        r.raise_for_status()
                        async for line in r.aiter_lines():
                            if line:
                                yield (line + "\n").encode("utf-8")
                    circuit.record_success()
                except Exception as e:
                    circuit.record_failure(settings.circuit_fail_threshold)
                    dlq_push(settings.dlq_path, {"trace_id": trace_id, "event":"stream_fail","error":str(e)})
                    metric_inc("stream_fail_total")
                    raise
            return StreamingResponse(gen(), media_type="text/event-stream")

        metric_inc("chat_requests_total")
        try:
            out = await with_retries(lambda: openai_chat(client, settings.vllm_text_base_url, payload),
                                     settings.retries, settings.retry_base_delay, settings.retry_max_delay)
            out["model"] = alias
            audit_write(settings.audit_path, {"trace_id": trace_id, "event":"response", "alias": alias, "ok": True})
            circuit.record_success()
            return JSONResponse(out)
        except Exception as e:
            circuit.record_failure(settings.circuit_fail_threshold)
            dlq_push(settings.dlq_path, {"trace_id": trace_id, "event":"chat_fail","alias":alias,"error":str(e),"body":body})
            metric_inc("chat_fail_total")
            audit_write(settings.audit_path, {"trace_id": trace_id, "event":"response", "alias": alias, "ok": False, "error": str(e)})
            raise HTTPException(status_code=502, detail="backend_error")
