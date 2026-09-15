

# 06-ProJ: AI smart university assistant

Design and document a complete multi-agent RAG system for a university, from the chat frontend and API gateway to AI routing across General AI / University RAG / Local AI models, retrieval, generation, logging, and deployment.

----
## Structure

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
----

## Core Recommendations

The system settles on one primary response type per query:

- **Answer directly** — General AI, for non-university questions
- **Answer with citations** — University RAG, for regulations/announcements/course info
- **Run a local task** — Local AI Model, for classification/prediction requests
- **Ask for clarification** — when confidence is too low to answer safely
- **Decline and refer to staff** — for out-of-scope or unsafe requests

----

## How to Run

This project is currently at the **design/documentation stage**. The `01-08` folders contain planning and process files; runnable services will be added during implementation.

Once implemented, the complete system will be managed using **Docker Compose**. Each module runs as an independent service/container, allowing Next.js, Python, FastAPI, AI models, and databases to work together.

* **`docker-compose.yml`** — builds, starts, connects, and manages all services.
* **`Dockerfile`** — defines the runtime, dependencies, and environment for each service.
* **`.env`** — stores API keys and environment configuration.
* **Docker Network** — enables communication between service containers.
* **`Makefile`** *(optional)* — provides shortcuts such as `make up`, `make down`, `make logs`, and `make rebuild`.

To start the complete system:

```
docker compose up -d
```
Docker Compose is the main orchestrator for the complete system.

----
## Summary

This project presents the design of **AI Smart University Assistant**, an agentic RAG system organized into **8 stages (01–08)**. The workflow is **Web App → API/Backend → AI Router/Agent → General AI / University RAG / Local AI → Retrieval → LLM Generation → Response/Log**, with the complete system managed using **Docker** and monitored through **Monitoring & Analytics**.

Each stage contains `01_env.txt`, `02_step.txt`, and `03_process.txt`, describing its **requirements, workflow, and techniques**. Supporting data includes **User Data/Context** for the backend, a **Knowledge Base** for RAG, and **Monitoring & Analytics** for system logs, feedback, and model performance.




