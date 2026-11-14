# run_all.py — start the whole system in ONE terminal (local development helper, Module 09)
#
#   - starts the 8 services as child processes of this script (no extra windows)
#   - shows only important log lines, each with the module name in front
#   - waits until every service answers, then opens the web page
#   - Ctrl+C (or closing the window) stops everything
#
# Run:  .venv\Scripts\python.exe 09_backend\scripts\run_all.py      (web_agent_predic.bat does this for you)

import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB_URL = "http://127.0.0.1:3000"

# (label, port, command arguments after "python")
SERVICES = [
    ("04 data   ", 8002, ["04_external_data_services/eds_server.py"]),
    ("05 integr ", 8003, ["05_data_integration/di_server.py"]),
    ("06 risk   ", 8004, ["06_risk_knowledge_services/rks_server.py"]),
    ("07 decide ", 8005, ["07_decision_llm_engine/dle_server.py"]),
    ("08 recomm ", 8006, ["08_recommendation_feedback/rf_server.py"]),
    ("03 agent  ", 8001, ["03_travel_ai_agent/agent_server.py"]),
    ("02 api    ", 8000, ["02_api_/api_server.py"]),
    ("01 web    ", 3000, ["-m", "http.server", "3000", "--bind", "127.0.0.1", "--directory", "01_web_app/web"]),
]

processes = []
print_lock = threading.Lock()


def say(label, text):
    with print_lock:
        print(f"[{label}] {text}", flush=True)


def is_noise(line):
    """Hide normal request logs so the terminal stays readable. Errors and warnings are always shown."""
    lower = line.lower()
    if "error" in lower or "traceback" in lower or "exception" in lower or "warning" in lower:
        return False
    if 'HTTP/1.1"' in line and ("GET" in line or "POST" in line or "DELETE" in line or "OPTIONS" in line):
        return True                      # uvicorn / http.server access logs
    if (" GET " in line or " POST " in line or " DELETE " in line) and ("-> 2" in line or "-> 3" in line):
        return True                      # our own request timing logs with status 2xx / 3xx
    if "Started server process" in line or "Waiting for application startup" in line:
        return True
    if "Application startup complete" in line or "Serving HTTP on" in line:
        return True
    return False


def show_output(label, process):
    for line in process.stdout:
        line = line.rstrip()
        if line and not is_noise(line):
            say(label, line)


def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def is_up(port):
    url = f"http://127.0.0.1:{port}/" if port == 3000 else f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def stop_all():
    for _, p in processes:
        if p.poll() is None:
            p.terminate()
    for _, p in processes:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()


def main():
    busy = [port for _, port, _ in SERVICES if port_in_use(port)]
    if busy:
        print(f"Ports already in use: {busy}")
        print("The system may already be running (close the other window first), or another program uses these ports.")
        return 1

    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    for label, port, args in SERVICES:
        p = subprocess.Popen([sys.executable] + args, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        processes.append((label, p))
        threading.Thread(target=show_output, args=(label.strip(), p), daemon=True).start()
        say(label.strip(), f"starting on port {port} ...")

    # wait until every service answers (max ~60 s)
    waiting = list(SERVICES)
    for _ in range(60):
        waiting = [s for s in waiting if not is_up(s[1])]
        if not waiting:
            break
        time.sleep(1)
    print()
    for label, port, _ in SERVICES:
        print(f"   {'UP  ' if is_up(port) else 'DOWN'}  {label.strip():10s} http://127.0.0.1:{port}")
    print()
    if waiting:
        print("Some services did not start. Read the [..] messages above for the reason.")
    else:
        print(f"All services are running. Opening {WEB_URL}")
        webbrowser.open(WEB_URL)
    print(f"Web page: {WEB_URL}    API docs: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C (or close this window) to stop everything.\n")

    # keep running; tell the user if a service stops by itself
    reported = set()
    while True:
        for label, p in processes:
            if p.poll() is not None and label not in reported:
                reported.add(label)
                say(label.strip(), f"STOPPED (exit code {p.returncode}) — see the messages above")
        time.sleep(2)


if __name__ == "__main__":
    try:
        code = main()
    except KeyboardInterrupt:
        code = 0
        print("\nStopping all services ...")
    finally:
        stop_all()
    sys.exit(code or 0)
