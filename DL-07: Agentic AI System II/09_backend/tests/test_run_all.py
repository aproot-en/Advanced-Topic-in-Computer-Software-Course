# test_run_all.py — tests for the one-window launcher (09_backend/scripts/run_all.py)
# Run:  .venv\Scripts\python.exe -m pytest 09_backend\tests -q

import os
import socket
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(ROOT, "09_backend", "scripts"))

import run_all   # noqa: E402


def test_normal_request_logs_are_hidden():
    assert run_all.is_noise('INFO:     127.0.0.1:5000 - "GET /health HTTP/1.1" 200 OK')
    assert run_all.is_noise('127.0.0.1 - - [14/Nov/2026 20:00:00] "GET /app.js HTTP/1.1" 200 -')
    assert run_all.is_noise("[api_backend] GET /api/alerts -> 200 (120 ms)")
    assert run_all.is_noise("INFO:     Application startup complete.")


def test_errors_and_alerts_are_shown():
    assert not run_all.is_noise("[api_backend] POST /api/trip -> 503 (2000 ms)")
    assert not run_all.is_noise("Traceback (most recent call last):")
    assert not run_all.is_noise("ERROR:    [Errno 10048] address already in use")
    assert not run_all.is_noise("[alert-watcher] แจ้งเตือน 'บ้าน': Storm (30 km, ระดับ 3)")
    assert not run_all.is_noise("[llama] understand failed, using rules: timeout")


def test_port_in_use_detection():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    assert run_all.port_in_use(port)
    server.close()
    assert not run_all.port_in_use(port)


def test_every_service_file_exists():
    for label, port, args in run_all.SERVICES:
        if args[0] != "-m":
            assert os.path.exists(os.path.join(ROOT, args[0])), args[0]
    assert len({port for _, port, _ in run_all.SERVICES}) == 8
