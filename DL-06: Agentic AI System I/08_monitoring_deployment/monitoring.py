### monitoring.py - 08 monitoring (simple, for local runs)
### in-memory counters, exported in Prometheus format at GET /metrics
### one JSON log line per event (ready for Loki/ELK later)

import json
import logging
from collections import Counter

import config

counters = Counter()
latency_sum = Counter()


def setup_logging():
    logging.basicConfig(level=config.LOG_LEVEL, format="%(asctime)s %(name)s %(levelname)s %(message)s")


def record_request(path, status):
    counters[f'http_requests_total{{path="{path}",status="{status}"}}'] += 1


def record_turn(decision, response):
    ### AI metrics: route, response_type, engine, citation, degraded
    counters[f'route_total{{route="{decision["route"]}"}}'] += 1
    counters[f'response_type_total{{type="{response.response_type}"}}'] += 1
    counters[f'engine_total{{engine="{response.engine_used}"}}'] += 1
    if response.sources:
        counters["citation_answers_total"] += 1
    for service in response.degraded_services:
        counters[f'degraded_total{{service="{service}"}}'] += 1
    latency_sum[response.engine_used] += response.latency_ms
    logging.getLogger("monitoring").info(json.dumps({
        "event": "turn", "trace_id": response.trace_id, "route": decision["route"],
        "response_type": response.response_type, "engine_used": response.engine_used,
        "latency_ms": response.latency_ms, "degraded": response.degraded_services}))


def record_feedback(engine, rating):
    counters[f'feedback_total{{engine="{engine}",rating="{rating}"}}'] += 1


def metrics_text():
    lines = [f"unirag_{name} {value}" for name, value in sorted(counters.items())]
    for engine, total in latency_sum.items():
        lines.append(f'unirag_latency_ms_sum{{engine="{engine}"}} {total}')
    return "\n".join(lines) + "\n"
