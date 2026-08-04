


# memory.py
# Store recent conversation history for multi-turn question answering.
# Conversation history is sent only to the LLM, not used for retrieval.
# Older conversations are removed automatically to limit memory size.
# The first topic is kept to maintain conversation context.
# Memory size is controlled by config.MEMORY_MAX_TURNS.


import config

# แปลง role ของข้อความ เป็นคำที่คนอ่านเข้าใจ
ROLE_NAMES = {"user": "ผู้ใช้", "assistant": "ผู้ช่วย"}


class ConversationMemory:
    def __init__(self):
        self.messages = []      # [{"role": "user", "content": "..."}, ...]
        self.first_topic = ""   # หัวข้อแรกที่คุยกัน เก็บไว้กันหลุดประเด็น

    def add_user(self, text):
        self.add("user", text)

    def add_assistant(self, text):
        self.add("assistant", text)

    def add(self, role, text):
        self.messages.append({"role": role, "content": text})
        self.forget_old_messages()

    def forget_old_messages(self):
        """ตัดข้อความเก่าทิ้งเมื่อเกินโควตา (1 รอบ = ผู้ใช้ถาม + ผู้ช่วยตอบ = 2 ข้อความ)"""
        limit = config.MEMORY_MAX_TURNS * 2

        while len(self.messages) > limit:
            removed = self.messages.pop(0)

            # จำหัวข้อแรกไว้ ก่อนที่มันจะหายไป
            if not self.first_topic and removed["role"] == "user":
                self.first_topic = removed["content"][:100]

    def get_context(self):  #คืนประวัติทั้งหมดเป็นข้อความ สำหรับใส่ใน prompt
        lines = []

        if self.first_topic:
            lines.append(f"[หัวข้อที่คุยก่อนหน้า: {self.first_topic}]")

        for message in self.messages:
            name = ROLE_NAMES.get(message["role"], message["role"])
            lines.append(f"{name}: {message['content']}")

        return "\n".join(lines)


# Determine whether the query depends on previous conversation context.
# Short follow-up questions usually require conversation history.
# Used to decide whether query rewriting is needed.
# Example: "What are the side effects?" → True
# Example: "What is PrEP?" → False


    def is_followup(self, query):
        if not self.messages:
            return False

        markers = ("แล้ว", "มัน", "อันนั้น", "อันนี้", "ต่อ", "อีก", "ทำไม", "ล่ะ")
        text = query.strip()
        return len(text) < 30 and text.startswith(markers)

    def clear(self):
        self.messages = []
        self.first_topic = ""


