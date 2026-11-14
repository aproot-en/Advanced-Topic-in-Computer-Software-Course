# common.py
# Shared by every service: error format, request timing log, /health endpoint

import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from service_client import ServiceError


def create_app(title, service_name):
    """Create a FastAPI app with /health and the same error handling for every service."""
    app = FastAPI(title=title)

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": service_name}

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        if request.url.path != "/health":
            print(f"[{service_name}] {request.method} {request.url.path} -> {response.status_code} "
                  f"({(time.time() - start) * 1000:.0f} ms)")
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        detail = exc.detail if isinstance(exc.detail, dict) else {"code": "ERROR", "message": str(exc.detail)}
        return JSONResponse(status_code=exc.status_code, content={"error": detail})

    @app.exception_handler(ServiceError)
    async def service_error(request, exc):
        return JSONResponse(status_code=exc.status,
                            content={"error": {"code": "UPSTREAM_UNAVAILABLE", "message": str(exc)}})

    @app.exception_handler(RuntimeError)
    async def runtime_error(request, exc):
        # free_apis.py raises RuntimeError when an external API is unavailable
        return JSONResponse(status_code=503, content={"error": {"code": "UPSTREAM_UNAVAILABLE", "message": str(exc)}})

    @app.exception_handler(Exception)
    async def unexpected_error(request, exc):
        # a bug in our code: log it, but still answer with the same JSON error format
        print(f"[{service_name}] unexpected error on {request.url.path}: {repr(exc)}")
        return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL", "message": "unexpected error"}})

    return app


def fail(status, code, message):
    raise HTTPException(status_code=status, detail={"code": code, "message": message})
