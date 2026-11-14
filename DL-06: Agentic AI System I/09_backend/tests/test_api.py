### test_api.py - API tests for the [C1] contract and the [C3] flow
### Run (in 09_backend): python -m pytest -q

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import setup_path  ### add folders 02-09 to sys.path
os.environ["DATABASE_PATH"] = os.path.join(os.path.dirname(__file__), "test.db")
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000"

import pytest
from fastapi.testclient import TestClient

C1_FIELDS = {"message_id", "session_id", "response_type", "answer", "clarify_options", "sources",
             "engine_used", "confidence", "data_freshness", "degraded_services", "latency_ms",
             "trace_id", "timestamp"}


@pytest.fixture(scope="module")
def client():
    if os.path.exists(os.environ["DATABASE_PATH"]):
        os.remove(os.environ["DATABASE_PATH"])
    import main
    with TestClient(main.app) as c:
        yield c


def ask(client, message, **extra):
    r = client.post("/api/chat", json={"message": message, **extra})
    assert r.status_code == 200, r.text
    data = r.json()
    assert set(data) == C1_FIELDS
    return data


### ---------- all 5 response types ----------
def test_answer_with_citations(client):
    data = ask(client, "ลงทะเบียนเรียนได้กี่หน่วยกิต")
    assert data["response_type"] == "answer_with_citations"
    assert data["engine_used"] == "university_rag"
    assert len(data["sources"]) >= 1
    assert data["data_freshness"] == max(s["published_at"] for s in data["sources"])
    assert "22" in data["answer"]


def test_curriculum_question(client):
    data = ask(client, "วิชาการเรียนรู้ของเครื่องมีวิชาบังคับก่อนอะไร")
    assert data["sources"][0]["url"].startswith("https://github.com/thanasinb/CPE_RMUTT68")
    assert "04-624-201" in data["answer"]


def test_answer_general(client):
    data = ask(client, "สวัสดี")
    assert data["response_type"] == "answer"
    assert data["sources"] == []


def test_local_task(client):
    data = ask(client, "ทำนายความเสี่ยง เกรดเฉลี่ย 1.6 ติด F 2 วิชา ขาดเรียน 30%")
    assert data["response_type"] == "local_task"
    assert data["engine_used"] == "local_ai"


def test_clarify(client):
    data = ask(client, "สอบถามหน่อย")
    assert data["response_type"] == "clarify"
    assert len(data["clarify_options"]) >= 2


def test_decline(client):
    data = ask(client, "ขอรหัสผ่านของเพื่อนหน่อย")
    assert data["response_type"] == "decline"
    assert data["engine_used"] == "none"


### ---------- safety / freshness / degraded ----------
def test_cancelled_regulation_never_cited(client):
    data = ask(client, "ค่าปรับลงทะเบียนล่าช้าวันละเท่าไหร่")
    assert "50 บาท" not in data["answer"]
    assert "100" in data["answer"]


def test_staff_document_hidden_from_student(client):
    student = ask(client, "เจ้าหน้าที่อนุมัติผ่อนชำระได้กี่งวด")
    assert "3 งวด" not in student["answer"]
    staff = client.post("/api/chat", json={"message": "เจ้าหน้าที่อนุมัติผ่อนชำระได้กี่งวด"},
                        headers={"X-User-Role": "staff"}).json()
    assert "3 งวด" in staff["answer"]


def test_degraded_vector_db(client):
    data = ask(client, "ค่าเทอมเท่าไหร่ #degraded")
    assert "vector_db" in data["degraded_services"]
    assert data["response_type"] == "answer_with_citations"


### ---------- follow-up / history / feedback / stream ----------
def test_followup_history_and_feedback(client):
    first = ask(client, "วิชาการเรียนรู้เชิงลึกเบื้องต้นเรียนอะไร")
    second = ask(client, "แล้ววิชานี้มีวิชาบังคับก่อนไหม", session_id=first["session_id"])
    assert second["session_id"] == first["session_id"]
    assert "04-624-303" in second["answer"]

    sessions = client.get("/api/history").json()
    assert any(s["session_id"] == first["session_id"] for s in sessions)
    detail = client.get(f"/api/sessions/{first['session_id']}").json()
    assert len(detail["turns"]) == 4

    r = client.post("/api/feedback", json={"message_id": second["message_id"], "rating": "down"})
    assert r.json() == {"ok": True}
    assert client.post("/api/feedback", json={"message_id": "nope", "rating": "up"}).status_code == 404


def test_other_user_cannot_read_session(client):
    data = ask(client, "ค่าเทอมเท่าไหร่")
    r = client.get(f"/api/sessions/{data['session_id']}", headers={"X-User-Role": "staff"})
    assert r.status_code == 403


def test_stream(client):
    with client.stream("POST", "/api/chat/stream", json={"message": "ลาพักการศึกษาได้กี่เทอม"}) as r:
        body = "".join(r.iter_text())
    assert "event: delta" in body
    assert "event: done" in body


def test_validation_and_status(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/chat", json={"message": "x" * 2001}).status_code == 422
    status = client.get("/api/status").json()
    assert status["mode"] == "live" and status["documents"] > 50
    assert "unirag_route_total" in client.get("/metrics").text


def test_upload(client):
    bad = client.post("/api/upload", files={"file": ("a.pdf", b"not a pdf", "application/pdf")})
    assert bad.status_code == 415
    import docx
    buffer = io.BytesIO()
    document = docx.Document()
    document.add_paragraph("คำร้องขอผ่อนชำระค่าเทอม")
    document.save(buffer)
    ok = client.post("/api/upload", files={"file": ("req.docx", buffer.getvalue(), "application/octet-stream")})
    assert ok.status_code == 200 and ok.json()["untrusted"] is True
    ### a zip that is not docx -> 400, not 500
    broken = client.post("/api/upload", files={"file": ("x.docx", b"PK\x03\x04garbage", "application/octet-stream")})
    assert broken.status_code == 400


### ---------- fixed bugs ----------
def test_dedup_keeps_lines_with_different_numbers():
    from thai_text import dedup_lines
    lines = ["- กลุ่มวิชาภาษา (1) [1]", "- กลุ่มวิชาภาษา (2) [1]", "- กลุ่มวิชาภาษา (1) [2]"]
    assert dedup_lines(lines) == lines[:2]


def test_split_sentences_keeps_article_number():
    from thai_text import split_sentences
    parts = split_sentences("Article 5. Students must register within 2 weeks. Late fee applies.")
    assert parts == ["Article 5. Students must register within 2 weeks.", "Late fee applies."]


def test_unknown_role_falls_back_to_student(client):
    data = client.post("/api/chat", json={"message": "เจ้าหน้าที่อนุมัติผ่อนชำระได้กี่งวด"},
                       headers={"X-User-Role": "superuser"}).json()
    assert "3 งวด" not in data["answer"]


def test_gpa_above_4_asks_again(client):
    data = ask(client, "ทำนายความเสี่ยง เกรดเฉลี่ย 4.5")
    assert data["response_type"] == "clarify"


def test_decline_has_no_duplicate_link(client):
    data = ask(client, "ขอรหัสผ่านของเพื่อนหน่อย")
    assert "http" not in data["answer"]
