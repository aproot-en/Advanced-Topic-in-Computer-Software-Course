# -*- coding: utf-8 -*-
# Problem 07: Retrieval is correct, but the Generated Answer distorts the Context (Faithfulness)
# Uses a real answer from sex_q_a.txt (PEP, which has a medically critical time window)
from data_loader import load_qa


def find_entry(data):
    return next(d for d in data if d["lang"] == "ทางการ" and d["question"].startswith("PEP คืออะไร"))


def bad_generator(context):
    # Simulated failure: the generator unknowingly changes a critical number/condition
    return context.replace("72 ชั่วโมง", "7 วัน").replace("ไม่เกิน", "ภายใน")


def grounded_generator(context):
    return context


def run():
    data = load_qa()
    entry = find_entry(data)
    context = entry["answer"]

    print("Question:", entry["question"])
    print("\nRetrieved Context:")
    print(context)

    print("\nBad Generation (distorts the critical time window):")
    print(bad_generator(context))

    print("\nGrounded Generation (sticks to the original Context):")
    print(grounded_generator(context))

    print("\nCause: Retrieval is correct, but the Generator changes a critical detail (the PEP start-time window)")
    print("In a health domain this kind of error can be dangerous; the Prompt must force answers to come from Context only")
    print("and Faithfulness must be evaluated before sending the answer to the user")
