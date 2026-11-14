### engines.py — 04 AI Model Selection
### Route A General AI : no LLM call here, passthrough=true so 06 makes the only call
### Route B RAG        : search documents with 05, wrap them in an Engine Result
### Route C Local AI   : run the local PyTorch models (data stays on the server)
### every engine returns an EngineResult [C2]; errors go in the error field

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import config
import local_ai
from retrieval import get_retriever
from schemas import EngineResult

_pool = ThreadPoolExecutor(max_workers=4)


def run_general(decision):
    ### simple model tier: long question = complex task
    tier = "large" if len(decision["rewritten_query"]) > 300 else "small"
    return EngineResult(engine="general_ai", passthrough=True,
                        model_version=f"{config.GENERATION_MODEL} ({tier})"), []


def run_rag(decision, user_context, method, top_k, force_degraded):
    found = get_retriever().search(decision["rewritten_query"], user_context, method, top_k,
                                   lang=decision["language"], force_degraded=force_degraded)
    result = EngineResult(engine="university_rag", chunks=found["chunks"],
                          error=found["reason"])
    return result, found["degraded"]


def run_local(decision):
    query = decision["rewritten_query"]
    low = query.lower()
    ### request-type classification
    if "จัดประเภท" in low or "classify" in low or "คำร้อง" in low:
        label, prob, version = local_ai.predict_text("request_type", query)
        return EngineResult(engine="local_ai", label=label, score=round(prob, 3),
                            content="request_type", model_version=version), []
    ### academic risk prediction (needs a GPA in the text)
    features = local_ai.extract_risk_features(query)
    if features is None:
        return EngineResult(engine="local_ai", content="risk", error="missing_features"), []
    prob, factors, version = local_ai.predict_risk(features)
    content = "risk|" + ";".join(f"{name}={value:.3f}" for name, value in factors)
    return EngineResult(engine="local_ai", label="risk", score=round(prob, 3), content=content,
                        model_version=version), []


def run_engines(decision, user_context, method="hybrid_rrf", top_k=5, force_degraded=False):
    ### clarify / decline: no engine call
    route = decision["route"]
    if route == "none":
        return [], []

    if route == "general_ai":
        func, args = run_general, (decision,)
    elif route == "university_rag":
        func, args = run_rag, (decision, user_context, method, top_k, force_degraded)
    else:
        func, args = run_local, (decision,)

    ### run in a thread so the engine can time out
    start = time.time()
    future = _pool.submit(func, *args)
    try:
        result, degraded = future.result(timeout=config.ENGINE_TIMEOUT_MS / 1000)
    except TimeoutError:
        result, degraded = EngineResult(engine=route, error="timeout"), [route]
    except Exception as e:
        result, degraded = EngineResult(engine=route, error=f"engine_error: {e}"), [route]
    result.latency_ms = int((time.time() - start) * 1000)
    return [result], degraded
