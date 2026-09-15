

# 07-ProJ: AI smart travel & emergency assistant

Build an intelligent travel safety assistant that analyzes a traveler's route, real-time weather, transportation status, and disaster alerts to estimate local risk and provide an explainable recommendation.

The system combines an AI agent, external APIs, geospatial data integration, a local risk model, disaster-focused RAG, route analysis, deterministic decision rules, and an LLM-generated explanation inside a Docker-based architecture.

----

# Structure

```text
ProJ-Agent-II/
│
├── 01_web_app/                              # Traveler-facing web and mobile interface
│   ├── 01_env.txt                           # Frontend runtime, packages, and configuration
│   ├── 02_step.txt                          # User input and recommendation display workflow
│   └── 03_process.txt                       # UI architecture, validation, security, and UX
│
├── 02_api_backend/                          # Secure API and request-management layer
│   ├── 01_env.txt                          
│   ├── 02_step.txt                          
│   └── 03_process.txt                       
│
├── 03_travel_ai_agent/                      # Agent orchestration and tool selection
│   ├── 01_env.txt                           
│   ├── 02_step.txt                         
│   └── 03_process.txt                       
│
├── 04_external_data_services/               # Real-time external data adapters
│   ├── 01_env.txt                          
│   ├── 02_step.txt                          
│   └── 03_process.txt                       
│
├── 05_data_integration/                     # Multi-source and geospatial data processing
│   ├── 01_env.txt                           
│   ├── 02_step.txt                          
│   └── 03_process.txt                       
│
├── 06_risk_knowledge_services/              # Risk prediction, Disaster RAG, and route analysis
│   ├── 01_env.txt                           
│   ├── 02_step.txt                          
│   └── 03_process.txt                       
│
├── 07_decision_llm_engine/                  # Safety decision and natural-language explanation
│   ├── 01_env.txt                           
│   ├── 02_step.txt                          
│   └── 03_process.txt                       
│
└── 08_recommendation_feedback/              # Final advice, alerts, and continuous feedback loop
    ├── 01_env.txt                           
    ├── 02_step.txt                          
    └── 03_process.txt                       

```

# Core Recommendations

The system produces one primary action based on the assessed risk, official warnings, transportation conditions, available routes, and supporting safety knowledge:

- **Travel normally** — Conditions are safe and no critical restriction is active.
- **Change route** — A safer alternative route is available.
- **Delay travel** — The risk is time-dependent and may decrease later.
- **Avoid travel** — The route has a high risk, official closure, or no acceptable alternative.
- **Emergency instructions** — Immediate safety actions, official contacts, and local support information.

Every recommendation should include its risk level, confidence, reasons, alternative routes, source citations, data freshness, and any unavailable or degraded services.

----

## How to Run

This repository is currently at the **design and documentation stage**. Each `01-08` folder contains planning files, not runnable source code yet.

Once implemented, use **Docker Compose** as the main system orchestrator for managing and connecting all services.

* **`docker-compose.yml`** — defines and connects all services.
* **`Dockerfile`** — defines the environment and dependencies for each service.
* **`.env`** — stores API keys and private configuration.
* **Docker Network** — enables communication between containers.
* **`Makefile`** *(optional)* — provides shortcuts such as `make up`, `make down`, `make logs`, and `make rebuild`.

Start the complete system with:

```bash
docker compose up -d
```

**Docker Compose is the main orchestrator for the complete system.**


## Summary

This project is designed as an end-to-end architecture for an explainable, real-time travel and emergency assistant. **Modules 01–03** manage user interaction, secure API access, intent understanding, planning, and AI-agent orchestration. **Modules 04–05** collect and normalize live weather, transport, disaster, time, and geospatial data into a versioned travel-context snapshot.

**Module 06** evaluates route risk with a local ML/DL model, retrieves verified emergency guidance through Disaster RAG, and identifies available or alternative routes. **Module 07** applies deterministic safety rules to select the final action before using an LLM to produce a grounded natural-language explanation. **Module 08** delivers the recommendation, supports follow-up questions and travel-plan updates, and captures governed feedback for evaluation and future system improvements.

The architecture keeps safety-critical decisions separate from free-form LLM generation. Official alerts, route closures, model versions, source provenance, data freshness, fallback behavior, and decision traces remain visible and auditable throughout the workflow.
