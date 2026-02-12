from __future__ import annotations
import os
from dataclasses import dataclass

def _b(name: str, default: str="false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1","true","yes","y","on")

@dataclass(frozen=True)
class Settings:
    backend: str = os.getenv("FOUND_BACKEND","vllm").strip().lower()
    port: int = int(os.getenv("FOUND_PORT","9000"))

    vllm_text_base_url: str = os.getenv("FOUND_VLLM_TEXT_BASE_URL","http://vllm-text:8000").rstrip("/")
    vllm_vision_base_url: str = os.getenv("FOUND_VLLM_VISION_BASE_URL","http://vllm-vision:8000").rstrip("/")
    asr_base_url: str = os.getenv("FOUND_ASR_BASE_URL","http://asr:7001").rstrip("/")
    tts_base_url: str = os.getenv("FOUND_TTS_BASE_URL","http://tts:7002").rstrip("/")
    sandbox_base_url: str = os.getenv("FOUND_SANDBOX_BASE_URL","http://sandbox:7010").rstrip("/")

    model_id_7b: str = os.getenv("FOUND_MODEL_ID_7B","deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
    model_id_30b: str = os.getenv("FOUND_MODEL_ID_30B","deepseek-ai/DeepSeek-R1-Distill-Qwen-32B")
    model_id_70b: str = os.getenv("FOUND_MODEL_ID_70B","deepseek-ai/DeepSeek-R1-Distill-Llama-70B")

    vision_model_id: str = os.getenv("FOUND_VISION_MODEL_ID","qwen2-vl")

    alias_7b: str = "adi-agi-found-7b"
    alias_30b: str = "adi-agi-found-30b"
    alias_70b: str = "adi-agi-found-70b"
    alias_auto: str = os.getenv("FOUND_ALIAS_AUTO","adi-agi-found-auto")
    alias_mm: str = os.getenv("FOUND_ALIAS_MM","adi-agi-found-mm")
    alias_swarm: str = os.getenv("FOUND_ALIAS_SWARM","adi-agi-found-swarm")

    auto_threshold_chars: int = int(os.getenv("FOUND_AUTO_THRESHOLD_CHARS","1200"))

    retries: int = int(os.getenv("FOUND_RETRIES","3"))
    retry_base_delay: float = float(os.getenv("FOUND_RETRY_BASE_DELAY","0.4"))
    retry_max_delay: float = float(os.getenv("FOUND_RETRY_MAX_DELAY","4.0"))

    dlq_path: str = os.getenv("FOUND_DLQ_PATH","data/dlq.jsonl")
    audit_path: str = os.getenv("FOUND_AUDIT_LOG_PATH","data/audit.jsonl")

    circuit_fail_threshold: int = int(os.getenv("FOUND_CIRCUIT_FAIL_THRESHOLD","5"))
    circuit_reset_seconds: int = int(os.getenv("FOUND_CIRCUIT_RESET_SECONDS","30"))

    memory_db_path: str = os.getenv("FOUND_MEMORY_DB_PATH","data/memory.sqlite3")

    sandbox_workdir: str = os.getenv("FOUND_SANDBOX_WORKDIR","data/sandbox_work")
    sandbox_timeout_sec: float = float(os.getenv("FOUND_SANDBOX_TIMEOUT_SEC","2.0"))

    swarm_n: int = int(os.getenv("FOUND_SWARM_N","3"))
    swarm_mode: str = os.getenv("FOUND_SWARM_MODE","weighted").strip().lower()
    swarm_weight_fast: float = float(os.getenv("FOUND_SWARM_WEIGHT_FAST","1.0"))
    swarm_weight_deep: float = float(os.getenv("FOUND_SWARM_WEIGHT_DEEP","1.5"))
    swarm_require_verifier: bool = _b("FOUND_SWARM_REQUIRE_VERIFIER","true")

    api_key: str = os.getenv("FOUND_API_KEY","").strip()
