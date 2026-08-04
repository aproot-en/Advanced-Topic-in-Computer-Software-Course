

# prompt_templates.py
# Store all prompt templates in one place.
# Makes prompts easier to manage, compare, and update.
# Answers must be based only on the retrieved context.
# Inline citations are required for traceable and verifiable responses.


import config

SYSTEM_PROMPT = """คุณคือผู้ช่วยให้ข้อมูลด้านสุขภาพทางเพศและเพศศึกษา ตอบโดยอ้างอิงจาก "ข้อมูลอ้างอิง" ที่ให้มาเท่านั้น

กฎ:
1. ใช้เฉพาะข้อมูลใน "ข้อมูลอ้างอิง" ห้ามเพิ่มความรู้จากภายนอก
2. ถ้าข้อมูลไม่พอ ให้ตอบว่า "{no_context}" ห้ามเดา
3. อ้างอิงหมายเลขแหล่งข้อมูลแบบ [1] [2] ท้ายประโยคที่ใช้ข้อมูลนั้น
4. ใช้ภาษาสุภาพ ตรงไปตรงมา ไม่ตัดสิน
5. ถ้าเป็นอาการรุนแรงหรือฉุกเฉิน ให้แนะนำพบแพทย์ทันที
6. ตอบกระชับ ไม่เกิน 5-6 ประโยค"""

USER_PROMPT = """{history}ข้อมูลอ้างอิง:
{context}

คำถามของผู้ใช้: {question}

ตอบโดยใช้ข้อมูลอ้างอิงข้างต้นเท่านั้น พร้อมอ้างอิงหมายเลข [n]"""


def format_context(chunks, max_chars=6000):
    """
    เรียง chunk เป็นบล็อกอ้างอิงมีหมายเลข

    max_chars กันไม่ให้ prompt ยาวเกิน context window — chunk เรียงจากดีสุดมาก่อน
    การตัดท้ายจึงตัดชิ้นที่เกี่ยวข้องน้อยที่สุดออก
    """
    blocks, used = [], 0
    for i, chunk in enumerate(chunks, start=1):
        block = f"[{i}] {chunk.get('answer') or chunk.get('text', '')}"
        if used + len(block) > max_chars:
            break
        blocks.append(block)
        used += len(block)
    return "\n\n".join(blocks)


def build_messages(question, chunks, history=""):
    """ประกอบเป็น messages list สำหรับส่งให้ LLM"""
    history_block = f"บทสนทนาก่อนหน้า:\n{history}\n\n" if history else ""
    return [
        {"role": "system", "content": SYSTEM_PROMPT.format(no_context=config.NO_CONTEXT_MESSAGE)},
        {
            "role": "user",
            "content": USER_PROMPT.format(
                history=history_block,
                context=format_context(chunks),
                question=question,
            ),
        },
    ]


# --------------------------------------------------- query transform
REWRITE_PROMPT = """แปลงคำถามให้ชัดเจนและเหมาะกับการค้นหาในฐานข้อมูลสุขภาพทางเพศ
- แก้คำสะกดผิด แทนคำแสลงด้วยศัพท์ทางการแพทย์
- ถ้าเป็นคำถามต่อเนื่อง ให้เติมบริบทจากบทสนทนาก่อนหน้าให้สมบูรณ์ในตัวเอง
- ตอบเป็นคำค้นหาบรรทัดเดียว ไม่ต้องอธิบาย

{history}คำถามเดิม: {question}

คำค้นหาที่แปลงแล้ว:"""

MULTI_QUERY_PROMPT = """สร้างคำถามที่มีความหมายเดียวกัน {n} แบบ เพื่อค้นหาให้ครอบคลุมขึ้น
- ใช้คำต่างกัน ทั้งภาษาพูดและศัพท์ทางการแพทย์
- ความหมายต้องตรงกับคำถามเดิม
- ตอบ 1 คำถามต่อ 1 บรรทัด ไม่ต้องใส่เลขข้อ

คำถามต้นฉบับ: {question}

คำถามที่สร้างขึ้น:"""

HYDE_PROMPT = """เขียน "คำตอบสมมติ" สำหรับคำถามนี้ ในสำนวนเดียวกับบทความให้ความรู้ด้านสุขภาพ
- ยาว 3-5 ประโยค ใช้ศัพท์เฉพาะทางที่น่าจะอยู่ในเอกสารจริง
- ไม่ต้องกังวลว่าข้อเท็จจริงถูกไหม เพราะใช้เป็นตัวแทนในการค้นหาเท่านั้น

คำถาม: {question}

คำตอบสมมติ:"""


# ------------------------------------------- LLM judge (ตอน evaluate)
JUDGE_PROMPT = """ประเมิน "คำตอบ" ตามเกณฑ์ {criteria} ให้คะแนน 1-5
(5 = ดีมาก, 3 = พอใช้, 1 = แย่)

{reference}
คำถาม: {question}

คำตอบ:
{answer}

ตอบกลับเป็น JSON เท่านั้น: {{"score": <1-5>, "reason": "<เหตุผลสั้นๆ>"}}"""
