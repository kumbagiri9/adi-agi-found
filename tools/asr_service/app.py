from __future__ import annotations
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app = FastAPI(title="adi-agi-found-asr", version="0.1")
class Req(BaseModel):
    audio_b64: str
    format: str = "wav"
@app.post("/v1/audio/transcriptions")
def transcribe(req: Req):
    try:
        base64.b64decode(req.audio_b64, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid audio_b64")
    return {"text":"[stub transcript] replace with faster-whisper/whisper.cpp/NeMo"}
