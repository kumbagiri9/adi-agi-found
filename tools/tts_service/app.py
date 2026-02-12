from __future__ import annotations
import base64
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI(title="adi-agi-found-tts", version="0.1")
class Req(BaseModel):
    text: str
    voice: str = "default"
    format: str = "wav"
@app.post("/v1/audio/speech")
def speak(req: Req):
    dummy = f"[stub audio voice={req.voice}] {req.text}".encode("utf-8")
    return {"audio_b64": base64.b64encode(dummy).decode("ascii"), "format": req.format, "voice": req.voice}
