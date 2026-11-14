# service_client.py
# Helper for modules to call each other over HTTP (owned by Module 09)
#
# Local run: 127.0.0.1 + the ports in the table below
# Docker run: set environment variables, e.g. EDS_URL=http://external_data_services:8002 (see 09_backend/.env.docker)

import os

import httpx

SERVICE_URLS = {
    "api": os.getenv("API_URL", "http://127.0.0.1:8000"),        # 02 API / Backend
    "agent": os.getenv("AGENT_URL", "http://127.0.0.1:8001"),    # 03 Travel AI Agent
    "eds": os.getenv("EDS_URL", "http://127.0.0.1:8002"),        # 04 External Data Services
    "di": os.getenv("DI_URL", "http://127.0.0.1:8003"),          # 05 Data Integration
    "rks": os.getenv("RKS_URL", "http://127.0.0.1:8004"),        # 06 Risk & Knowledge Services
    "dle": os.getenv("DLE_URL", "http://127.0.0.1:8005"),        # 07 Decision & LLM Engine
    "rf": os.getenv("RF_URL", "http://127.0.0.1:8006"),          # 08 Recommendation & Feedback
}


class ServiceError(Exception):
    """Calling another service failed."""

    def __init__(self, service, message, status=503):
        super().__init__(f"{service}: {message}")
        self.service = service
        self.status = status


async def call(service, method, path, params=None, json=None, timeout=60):
    url = SERVICE_URLS[service] + path
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.request(method, url, params=params, json=json)
    except httpx.TimeoutException:
        raise ServiceError(service, "timeout", 504)
    except httpx.HTTPError as e:
        raise ServiceError(service, f"เชื่อมต่อไม่ได้ ({e.__class__.__name__})")
    if r.status_code >= 400:
        try:
            detail = r.json().get("error", {}).get("message") or r.text[:150]
        except ValueError:
            detail = r.text[:150]
        raise ServiceError(service, detail, r.status_code)
    try:
        return r.json()
    except ValueError:
        raise ServiceError(service, "answer is not JSON")


async def get(service, path, params=None, timeout=60):
    return await call(service, "GET", path, params=params, timeout=timeout)


async def post(service, path, json=None, timeout=60):
    return await call(service, "POST", path, json=json, timeout=timeout)


async def is_up(service):
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            return (await client.get(SERVICE_URLS[service] + "/health")).status_code == 200
    except httpx.HTTPError:
        return False
