


# generator.py
# Generate answers with an LLM from retrieved documents.
# Disable USE_LLM to return retrieved text only.

import os
import re

from openai import OpenAI

import config
from src.prompt_templates import build_messages


class LLM:
    """เรียก LLM ผ่านไลบรารี openai (ใช้ได้ทั้ง ollama / openai / gemini)"""

    def __init__(self):
        base_url, default_model, key_name = config.LLM_PROVIDERS[config.LLM_PROVIDER]

        self.model = config.LLM_MODEL or default_model

        # Ollama ไม่ต้องใช้ key 
        api_key = os.getenv(key_name) if key_name else "ollama-ไม่ใช้-key"

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        #print(f"[llm] use {config.LLM_PROVIDER} · model {self.model}")

    def chat(self, messages):
        #แล้วคืนคำตอบเป็น string
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )
        return response.choices[0].message.content.strip()


class NoLLM:

    model = "don't use LLM"

    def chat(self, messages):
        user_message = messages[-1]["content"]

        # ดึงคำตอบจากบล็อก [1] ของ prompt ภาษาไทย
        context_match = re.search(
            r"ข้อมูลอ้างอิง:\s*(.*?)\n\nคำถามของผู้ใช้:",
            user_message,
            flags=re.DOTALL,
        )
        if not context_match:
            return config.NO_CONTEXT_MESSAGE

        first_block = context_match.group(1).split("\n\n[2]", 1)[0]
        answer_match = re.search(r"คำตอบ:\s*(.*)", first_block, flags=re.DOTALL)
        answer = answer_match.group(1).strip() if answer_match else ""

        return f"{answer} [1]" if answer else config.NO_CONTEXT_MESSAGE


def get_llm():
    if not config.USE_LLM:
        return NoLLM()

    try:
        return LLM()
    except Exception as error:
        print(f"[llm] Failed to use {config.LLM_PROVIDER}: {error}")
        print("[llm] Falling back to retrieved text only.")
        return NoLLM()


class Generator:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, question, chunks, history=""):

        # ค้นไม่เจออะไรเลย — ตอบว่าไม่รู้ ดีกว่าให้ LLM เดา
        if not chunks:
            return {
                "answer": config.NO_CONTEXT_MESSAGE,
                "sources": [],
                "no_context": True,
            }

        messages = build_messages(question, chunks, history)

        try:
            answer = self.llm.chat(messages)
        except Exception as error:
            #print(f"[llm] เรียกไม่สำเร็จ ({error}) — แสดงข้อมูลที่ค้นได้แทน")
            answer = f"{chunks[0]['answer']} [1]"

        if config.DISCLAIMER not in answer:
            answer = f"{answer}\n\n{config.DISCLAIMER}"

        return {
            "answer": answer.strip(),
            "sources": self.build_sources(chunks),
            "no_context": False,
        }

    def build_sources(self, chunks):    #  สร้างรายการแหล่งอ้างอิง ให้เลข [1] [2] ตรงกับที่อยู่ใน prompt
        sources = []
        for number, chunk in enumerate(chunks, start=1):
            sources.append({
                "n": number,
                "chunk_id": chunk["chunk_id"],
                "question": chunk["question"],
                "line_no": chunk["line_no"],
                "score": round(float(chunk["score"]), 4),
            })
        return sources
