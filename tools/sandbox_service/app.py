from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sandbox_impl import run_python_sandbox

app = FastAPI(title="adi-agi-found-sandbox", version="0.1")

class Req(BaseModel):
    tool: str = Field("python")
    code: str
    timeout_sec: float | None = None

@app.post("/v1/tools/execute")
def execute(req: Req):
    if req.tool.strip().lower() != "python":
        raise HTTPException(status_code=400, detail="tool not allowlisted")
    workdir = os.getenv("FOUND_SANDBOX_WORKDIR","data/sandbox_work")
    timeout = float(req.timeout_sec or os.getenv("FOUND_SANDBOX_TIMEOUT_SEC","2.0"))
    return run_python_sandbox(req.code, workdir=workdir, timeout_sec=timeout)
