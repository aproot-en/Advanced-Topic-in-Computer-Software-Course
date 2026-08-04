





# Connect all RAG components into a single pipeline.
#
# User Query
#   → query_transform   Improve the query before retrieval      (config.USE_QUERY_TRANSFORM)
#   → hybrid_retriever  Combine BM25 and dense retrieval        (config.USE_HYBRID)
#   → rerankers         Re-rank the retrieved results           (config.USE_RERANK)
#   → generator         Generate an answer with citations       (config.USE_LLM)
#   → memory            Store conversation history              (config.USE_MEMORY)
#
# Each stage can be enabled or disabled in config.py.
# Makes it easy to compare different RAG configurations.
#
# Usage:
#   rag = RAGPipeline()
#   print(rag.ask("What should I do if a condom breaks?")["answer"])

import time

import config
from src.generator import Generator, get_llm
from src.hybrid_retriever import HybridRetriever
from src.memory import ConversationMemory
from src.query_transform import QueryTransformer
from src.rerankers import get_reranker


class RAGPipeline:
    def __init__(self):
        llm = get_llm()

        self.retriever = HybridRetriever(reranker=get_reranker())
        self.transformer = QueryTransformer(llm)
        self.generator = Generator(llm)
        self.memory = ConversationMemory()

    def ask(self, query, top_k=config.TOP_K):
        """
        ถาม 1 คำถาม คืน dict ที่มี answer, sources, retrieved, timings

        อ่านโค้ดในนี้จากบนลงล่าง จะเห็นลำดับการทำงานทั้งหมดของ RAG
        """
        start_time = time.time()

        # ---- ขั้นที่ 1: ปรับคำถาม ----
        history = self.memory.get_context() if config.USE_MEMORY else ""

        # ส่งประวัติให้ตัวปรับคำถาม เฉพาะตอนที่เป็นคำถามต่อเนื่อง
        transform_history = history if self.memory.is_followup(query) else ""
        queries = self.transformer.transform(query, transform_history)
        time_after_transform = time.time()

        # ---- ขั้นที่ 2: ค้นหา (+ rerank ถ้าเปิดใช้) ----
        chunks = self.retriever.retrieve(
            queries[0],
            top_k=top_k,
            extra_queries=queries[1:],
        )
        time_after_retrieve = time.time()

        # ---- ขั้นที่ 3: เขียนคำตอบ ----
        result = self.generator.generate(query, chunks, history)
        time_after_generate = time.time()

        # ---- ขั้นที่ 4: จำไว้ใช้รอบหน้า ----
        if config.USE_MEMORY:
            self.memory.add_user(query)
            self.memory.add_assistant(result["answer"])

        result["queries_used"] = queries
        result["retrieved"] = chunks
        result["timings"] = {
            "ปรับคำถาม": round(time_after_transform - start_time, 2),
            "ค้นหา": round(time_after_retrieve - time_after_transform, 2),
            "เขียนคำตอบ": round(time_after_generate - time_after_retrieve, 2),
            "รวม": round(time_after_generate - start_time, 2),
        }
        return result

    def search_only(self, query, top_k=config.TOP_K):
        """ค้นอย่างเดียว ไม่เขียนคำตอบ — ใช้ตอนวัดผลการค้นหา"""
        queries = self.transformer.transform(query)
        return self.retriever.retrieve(queries[0], top_k, extra_queries=queries[1:])

    def reset(self):
        self.memory.clear()

    def show_settings(self):
        """พิมพ์ว่าตอนนี้เปิดขั้นตอนไหนอยู่บ้าง"""
        settings = [
            ("ค้นแบบผสม BM25 + dense", config.USE_HYBRID),
            ("จัดอันดับใหม่ (rerank)", config.USE_RERANK),
            ("ปรับคำถามก่อนค้น", config.USE_QUERY_TRANSFORM),
            ("จำบทสนทนา", config.USE_MEMORY),
            ("ใช้ LLM เขียนคำตอบ", config.USE_LLM),
        ]
        print("การตั้งค่า (แก้ได้ที่ config.py):")
        for name, enabled in settings:
            print(f"  {'เปิด' if enabled else 'ปิด '}  {name}")
