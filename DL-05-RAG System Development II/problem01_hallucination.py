# -*- coding: utf-8 -*-
# Problem 01: Hallucination / No evidence in Retrieved Context
# Uses sex_q_a.txt as a real Knowledge Base
from data_loader import load_qa

DOCS = load_qa()


def retrieve(question, top_k=3):
    words = question.lower().split()
    scored = [(sum(w in d["text"].lower() for w in words), d) for d in DOCS]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_k]]


def bad_generate(question, context):
    if not context:
        # Simulated failure: the model still fabricates an answer even without evidence in the KB
        return "กินยาคุมพร้อมน้ำอัดลมช่วยให้ฤทธิ์คุมกำเนิดแรงขึ้น (ข้อมูลนี้ไม่มีอยู่จริงใน Knowledge Base)"
    return context[0]["answer"]


def grounded_generate(question, context):
    if not context:
        return "ไม่พบข้อมูลที่สนับสนุนคำตอบใน Knowledge Base"
    return context[0]["answer"]


def run():
    q_in_kb = "PrEP คืออะไร"
    q_out_of_kb = "ตั๋วเครื่องบินไปเชียงใหม่ราคาเท่าไหร่"

    for label, q in [("Out of KB scope", q_out_of_kb), ("In KB", q_in_kb)]:
        ctx = retrieve(q)
        print(f"--- Query ({label}): {q}")
        print("Retrieved:", [d["question"] for d in ctx] or "Not found")
        print("Bad answer :", bad_generate(q, ctx))
        print("Fixed answer:", grounded_generate(q, ctx))
        print()

    print("Cause: The generator answers even though the Retrieved Context has no supporting evidence")
    print("e.g. a question that is completely outside the scope of the Knowledge Base (sex_q_a.txt)")
