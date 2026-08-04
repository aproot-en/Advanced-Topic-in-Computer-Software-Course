"""
โมดูลหลักที่ใช้ซ้ำได้ทั้งโปรเจกต์

  document_loader   อ่านไฟล์ต้นฉบับ แยกเป็นคู่คำถาม-คำตอบ
  text_splitter     ตัดข้อความยาวเป็น chunk
  embedding_model   แปลงข้อความเป็นเวกเตอร์
  vector_store      ฐานข้อมูลเวกเตอร์ FAISS
  retriever         ค้นหาแบบ dense อย่างเดียว (baseline)
  hybrid_retriever  ค้นหาแบบผสม BM25 + dense + RRF
  rerankers         จัดอันดับใหม่ด้วย cross-encoder
  query_transform   แปลงคำถามก่อนค้น
  prompt_templates  prompt ทั้งหมด
  generator         สร้างคำตอบด้วย LLM
  memory            ประวัติบทสนทนา
  rag_pipeline      ร้อยทุกขั้นเข้าด้วยกัน
"""
