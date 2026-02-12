Adi-agi-found
Adi-agi-found is an open-source, OpenAI-compatible multi-model runtime designed for:
•	Swarm reasoning (multi-agent consensus)
•	Model routing (7B / 30B / 70B / auto)
•	Sandbox tool execution (allowlisted)
•	Memory graph with contradiction detection
•	Production reliability (retries, DLQ, circuit breaker)
It allows developers to deploy and operate GPT-style APIs using open-weight models.
________________________________________
🚀 Features
•	✅ OpenAI-compatible API (/v1/chat/completions, /v1/models)
•	✅ Multi-model routing (7B / 30B / 70B / auto)
•	✅ Swarm consensus voting + evaluator gate
•	✅ Offline tool sandbox (secure Python execution)
•	✅ Memory graph + contradiction engine
•	✅ Streaming responses
•	✅ Retries + Dead Letter Queue (DLQ)
•	✅ Circuit breaker protection
•	✅ Docker-based deployment
•	✅ Cloud agnostic (AWS, GCP, Azure, On-prem, DGX)
________________________________________
🏗 Architecture
Client → Adi-agi-found Proxy → Model Backend (vLLM / OpenAI-compatible)
                       ↘ Swarm Engine
                       ↘ Evaluator + Verifier
                       ↘ Sandbox Tools
                       ↘ Memory + Contradiction Engine
This repository does not include model weights.
You must connect a backend such as vLLM or another OpenAI-compatible server.
________________________________________
⚡ Quick Start (5 Minutes)
1. Clone Repository
git clone https://github.com/kumbagiri9/adi-agi-found.git
cd adi-agi-found
2. Setup Environment
cp .env.example .env
3. Start Services
export VLLM_TEXT_MODEL_ID=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
docker compose --profile text --profile proxy up -d
4. Test API
curl http://localhost:9000/v1/models
Example completion:
curl http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "adi-agi-found-auto",
    "messages": [{"role":"user","content":"Explain quantum computing in simple terms."}]
  }'
________________________________________
🧠 Model Aliases
Alias	Description
adi-agi-found-7b	Fast lightweight model
adi-agi-found-30b	Balanced reasoning
adi-agi-found-70b	Deep reasoning
adi-agi-found-auto	Automatic routing
adi-agi-found-swarm	Multi-agent consensus
________________________________________
🔐 Optional: Enable API Key Protection
In .env:
FOUND_API_KEY=your-strong-key
Then call API with:
Authorization: Bearer your-strong-key
________________________________________
🛠 Sandbox Example
Execute safe Python:
curl http://localhost:9000/v1/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool":"python","code":"import math\nprint(math.sqrt(81))\n2+2"}'
________________________________________
🧩 Memory & Contradiction Engine
Store facts:
curl http://localhost:9000/v1/memory/facts/upsert \
  -H "Content-Type: application/json" \
  -d '{"facts":[{"subject":"PatientA","predicate":"has_condition","object":"Diabetes","confidence":0.9}]}'
Query contradictions:
curl http://localhost:9000/v1/memory/contradictions/query \
  -H "Content-Type: application/json" \
  -d '{"subject":"PatientA","predicate":"has_condition"}'
________________________________________
🌍 Deployment Options
Adi-agi-found can be deployed on:
•	AWS (EC2 + GPU)
•	GCP (Compute Engine)
•	Azure (VM)
•	On-prem GPU servers
•	NVIDIA DGX systems
Use Docker Compose or integrate into Kubernetes.
________________________________________
📦 Roadmap
•	Enterprise Edition (token-based API + metering)
•	Multi-tenant RBAC
•	Advanced compliance hardening
•	Multimodal fusion enhancements
•	Edge runtime support
________________________________________
📄 License
Apache License 2.0
See LICENSE file for details.
________________________________________
🤝 Contributing
Contributions are welcome.
1.	Fork repository
2.	Create feature branch
3.	Submit Pull Request
________________________________________
⚠️ Disclaimer
This project is infrastructure software.
Model behavior depends on the backend model you deploy.










*************************************************************************
# adi-agi-found 3.1.1 — Verified Multimodal Swarm OS (Rebuilt)
This build is regenerated after an execution-session reset.

**Includes**
- OpenAI-compatible proxy (`/v1/chat/completions`, `/v1/models`, `/metrics`, `/health`)
- Streaming passthrough (SSE style line streaming)
- Retries + DLQ + audit logs + circuit breaker
- Swarm + evaluators + verifier gate (`adi-agi-found-swarm`)
- Offline tool sandbox (allowlisted Python)
- Memory graph + fact store + contradiction engine

> Ships **no weights**. Plug open-weight backends via vLLM or any OpenAI-compatible server.

## Quickstart (Docker)
```bash
unzip adi-agi-found-3.1.1.zip
cd adi-agi-found-3.1.1
cp .env.example .env

VLLM_TEXT_MODEL_ID=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
docker compose --profile text --profile proxy up -d
```

Optional services:
```bash
docker compose --profile sandbox up -d
docker compose --profile asr up -d
docker compose --profile tts up -d
```

## Sandbox test
```bash
curl -s http://localhost:9000/v1/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool":"python","code":"import math\nprint(math.sqrt(81))\n2+2"}'
```

## Contradiction engine test
```bash
curl -s http://localhost:9000/v1/memory/facts/upsert \
  -H "Content-Type: application/json" \
  -d '{"facts":[{"subject":"PatientA","predicate":"has_condition","object":"Diabetes","polarity":"true","confidence":0.9,"provenance":"note1"}]}'

curl -s http://localhost:9000/v1/memory/facts/upsert \
  -H "Content-Type: application/json" \
  -d '{"facts":[{"subject":"PatientA","predicate":"has_condition","object":"Hypertension","polarity":"true","confidence":0.9,"provenance":"note2"}]}'

curl -s http://localhost:9000/v1/memory/contradictions/query \
  -H "Content-Type: application/json" \
  -d '{"subject":"PatientA","predicate":"has_condition"}'
```

## Tests
```bash
python tests/run_unittests.py
```
