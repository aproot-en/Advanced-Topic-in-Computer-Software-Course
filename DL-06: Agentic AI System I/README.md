

# 06-ProJ: AI smart university assistant

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

This project is currently at the **design/documentation stage**. The `01-08` folders contain planning and process files; runnable services will be added during implementation.

Once implementation starts, the complete system will be managed using **Docker Compose** rather than a single run-all script. Each module runs as an independent service/container, allowing different technologies such as Next.js, Python, FastAPI, AI models, and databases to work together.

* **`docker-compose.yml`** — the main system orchestrator. It builds, starts, connects, and manages all service containers through the Docker network.
* **`Dockerfile`** — each service can have its own Dockerfile defining its runtime, dependencies, and environment.
* **`Makefile`** *(optional)* — provides shortcuts such as `make up`, `make down`, `make logs`, and `make rebuild`.
* **`scripts/dev_run_all.py`** *(optional)* — can be used to start services without Docker during local development.

To start the complete system:

```bash
docker compose up -d
```

Docker Compose remains the **main orchestrator** for running and connecting all services in the project.

  
## Summary

This project documents the design of **AI Smart University Assistant**, an agentic RAG system that answers student questions by routing each query to the most appropriate AI engine. The full pipeline is broken down into **8 stages (01–08)**, following the flow shown in `proJ-6.txt` / `proposed-agent-i.png`: a student sends a request through the **Web App**, which forwards it to the **API/Backend**; the **AI Router/Agent** classifies intent and decides whether to call **General AI** (Gemini/OpenAI), **University RAG**, or a **Local AI Model**; RAG queries go through **hybrid retrieval** (BM25 + Vector DB) over the university knowledge base; all results converge at the **LLM Generation** stage, which synthesizes a grounded, cited answer; the answer is then delivered and logged in **Response/Log**, closing a **feedback loop** for follow-up questions; the whole system runs containerized with **Docker** and is observed through the **Monitoring & Analytics** stage.

Each stage folder (`01_env.txt`, `02_step.txt`, `03_process.txt`) documents, respectively, the **environment/requirements** to install, the **workflow steps** executed at that stage, and the **process & techniques** used — written like a per-stage README, so the project can be implemented incrementally, one stage at a time, while keeping the reasoning behind each design choice explicit.

The diagram also shows three auxiliary data stores, each wired to one specific stage rather than to the whole system — they are documented inside that stage's folder instead of getting a folder of their own: **User Data / Context** (profile, conversation history, preferences) feeds **02_api_backend**; **Knowledge Base** (regulations, announcements, course catalogs, handbooks) feeds **05_retrieval_knowledge**; and **Monitoring & Analytics** (logs, user feedback, model performance) observes the output of **07_response_logging**, and is grouped together with Docker deployment in **08_monitoring_deployment** for organizational convenience.



