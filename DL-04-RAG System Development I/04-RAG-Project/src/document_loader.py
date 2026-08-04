


# document_loader.py
# Load data/sex_q_a.txt and convert it into a list of Q&A records.
# Each record includes the source line number for reference.


import os


def load_qa_file(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ไม่พบไฟล์: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    records = []
    category = "ไม่ระบุหมวด"
    question = None
    question_line = None

    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("[หมวด"):
            category = line.strip("[]").replace("หมวด:", "").strip()
        elif line.startswith("Q:"):
            question = line[2:].strip()
            question_line = line_no
        elif line.startswith("A:") and question:
            records.append({
                "id": len(records),
                "category": category,
                "question": question,
                "answer": line[2:].strip(),
                "line_no": question_line,
            })
            question = None

    return records


    #คืน list ของ dict ที่มีคีย์:
    #    id        ลำดับของคู่คำถาม-คำตอบ เริ่มจาก 0
    #    category  หมวดที่คู่นี้อยู่
    #    question  ข้อความคำถาม
    #    answer    ข้อความคำตอบ
    #    line_no   บรรทัดของ "Q:" ในไฟล์ต้นฉบับ

