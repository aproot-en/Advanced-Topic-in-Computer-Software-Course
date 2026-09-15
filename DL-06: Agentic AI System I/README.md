

# 06-ProJ: AI Smart University Assistant

Design and document a complete multi-agent RAG system for a university, from the chat frontend and API gateway to AI routing across General AI / University RAG / Local AI models, retrieval, generation, logging, and deployment.

----
# Structure

```text
06-ProJ-Agent I/
│
│
├── 01_web_app/                             # Frontend — Chat / Upload / Dashboard
│   ├── 01_env.txt                          # Environment & requirements
│   ├── 02_step.txt                         # Workflow steps
│   └── 03_process.txt                      # Process & techniques
│
├── 02_api_backend/                         # API / Backend — FastAPI / Flask
│   ├── 01_env.txt
│   ├── 02_step.txt
│   └── 03_process.txt
│
├── 03_ai_router_agent/                     # AI Router / Agent — intent, routing, planning
│   ├── 01_env.txt
│   ├── 02_step.txt
│   └── 03_process.txt
│
├── 04_ai_model_selection/                  # General AI / University RAG / Local AI Model
│   ├── 01_env.txt
│   ├── 02_step.txt
│   └── 03_process.txt
│
├── 05_retrieval_knowledge/                 # BM25 + Vector DB hybrid retrieval + Knowledge Base
│   ├── 01_env.txt
│   ├── 02_step.txt
│   └── 03_process.txt
│
├── 06_llm_generation/                      # Context + Query → LLM answer, citations, safety
│   ├── 01_env.txt
│   ├── 02_step.txt
│   └── 03_process.txt
│
├── 07_response_logging/                    # Response / Log / Feedback loop
│   ├── 01_env.txt
│   ├── 02_step.txt
│   └── 03_process.txt
│
└── 08_monitoring_deployment/                # Docker, Monitoring & Analytics, CI/CD
    ├── 01_env.txt
    ├── 02_step.txt
    └── 03_process.txt
```


## How to Run

This repo is currently at the **design/documentation stage** — each `01-08` folder holds planning notes (`01_env.txt`, `02_step.txt`, `03_process.txt`), not runnable code yet. Once implementation starts, avoid a single all-in-one script such as `proJ-run-all-script.py` to launch everything: the stack mixes languages and runtimes — `01_web_app` is Node.js/Next.js, while `02-08` are separate Python/FastAPI services — so one Python process can't cleanly start, network, and hot-reload all of them together.

Instead, orchestrate the system the way **`08_monitoring_deployment`** already plans to:

- **`docker-compose.yml`** at the project root — one service block per stage (`web_app`, `api_backend`, `ai_router_agent`, `ai_model_selection`, `retrieval_knowledge`, `llm_generation`, `response_logging`), each built from its own `Dockerfile`, wired together on an internal Docker network. `docker compose up -d` starts the whole system with one command, regardless of each service's language.
- A lightweight **`Makefile`** (or `justfile`) on top of Compose for convenience, e.g. `make up`, `make down`, `make logs`, `make rebuild` — optional, but nicer than remembering raw `docker compose` flags.
- For local development **without Docker**, a small **dev-only** helper script (e.g. `scripts/dev_run_all.py`, using `subprocess`) can start each Python service with `uvicorn --reload` plus `npm run dev` for the frontend — but this should stay a convenience wrapper for developers, not the system's real orchestrator; Docker Compose remains the source of truth for how the services actually run together in staging/production.
  
## Summary

This project documents the design of **AI Smart University Assistant**, an agentic RAG system that answers student questions by routing each query to the most appropriate AI engine. The full pipeline is broken down into **8 stages (01–08)**, following the flow shown in `proJ-6.txt` / `proposed-agent-i.png`: a student sends a request through the **Web App**, which forwards it to the **API/Backend**; the **AI Router/Agent** classifies intent and decides whether to call **General AI** (Gemini/OpenAI), **University RAG**, or a **Local AI Model**; RAG queries go through **hybrid retrieval** (BM25 + Vector DB) over the university knowledge base; all results converge at the **LLM Generation** stage, which synthesizes a grounded, cited answer; the answer is then delivered and logged in **Response/Log**, closing a **feedback loop** for follow-up questions; the whole system runs containerized with **Docker** and is observed through the **Monitoring & Analytics** stage.

Each stage folder (`01_env.txt`, `02_step.txt`, `03_process.txt`) documents, respectively, the **environment/requirements** to install, the **workflow steps** executed at that stage, and the **process & techniques** used — written like a per-stage README, so the project can be implemented incrementally, one stage at a time, while keeping the reasoning behind each design choice explicit.

The diagram also shows three auxiliary data stores, each wired to one specific stage rather than to the whole system — they are documented inside that stage's folder instead of getting a folder of their own: **User Data / Context** (profile, conversation history, preferences) feeds **02_api_backend**; **Knowledge Base** (regulations, announcements, course catalogs, handbooks) feeds **05_retrieval_knowledge**; and **Monitoring & Analytics** (logs, user feedback, model performance) observes the output of **07_response_logging**, and is grouped together with Docker deployment in **08_monitoring_deployment** for organizational convenience.



