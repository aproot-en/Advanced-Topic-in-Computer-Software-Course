
## DL-04-RAG System Development I

Build a complete RAG system in Python, from loading a knowledge base and splitting text into chunks to retrieving relevant information and generating answers.

---- 
# Structure

```text
RAG-Project/
│
├── data/
│   ├── sex_q_a.txt
│   └── golden_set.json                     # Evaluation set
│
├── outputs/
│   ├── extracted_text.json                 # Parsed Q&A pairs with line numbers
│   ├── chunks.json                         # 541 text chunks with metadata
│   ├── embeddings.npy                      # Embedding vectors
│   ├── retrieval_results.json              # Top-k retrieval results
│   ├── eval_retrieval.json                 ⭐ Retrieval scores per configuration
│   └── eval_generation.json                ⭐ Answer quality scores
│
├── vector_db/
│   ├── document.index                      # FAISS index — dense semantic search
│   ├── bm25_index.pkl                      ⭐ BM25 index — exact-token search
│   ├── chunk_store.json                    # Chunks + metadata, aligned with FAISS order
│   └── index_meta.json                     ⭐ Fingerprint of the dataset this index was built from
│
├── labs/
│   ├── lab01_extract_text.py               # Extract text from the source file
│   ├── lab02_chunking.py                   # Split text into chunks
│   ├── lab03_create_embeddings.py          # Generate embeddings
│   ├── lab04_create_vector_db.py           # Build the FAISS vector database
│   ├── lab05_query_embedding.py            # Create query embeddings
│   ├── lab06_similarity_search.py          # Retrieve top-k relevant chunks
│   └── lab07_complete_retrieval.py         # Complete retrieval pipeline
│
├── src/
│   ├── document_loader.py                  # File loading and text extraction
│   ├── text_splitter.py                    # Text chunking
│   ├── embedding_model.py                  # Embedding model
│   ├── vector_store.py                     # FAISS vector database
│   ├── index_meta.py                       ⭐ Detect when the index is stale vs the dataset
│   ├── retriever.py                        # Dense-only retrieval
│   ├── hybrid_retriever.py                 ⭐ BM25 + Dense + RRF Fusion
│   ├── rerankers.py                        ⭐ Cross-Encoder Reranking
│   ├── query_transform.py                  ⭐ Query Rewrite, Multi-Query, HyDE
│   ├── prompt_templates.py                 ⭐ Prompt Templates
│   ├── generator.py                        ⭐ LLM Answer Generation
│   ├── memory.py                           ⭐ Conversation History
│   └── rag_pipeline.py                     ⭐ End-to-End RAG Pipeline
│
├── evaluation/
│   ├── metrics.py                          ⭐ Hit@k, Recall@k, Precision@k, MRR, nDCG
│   ├── build_golden_set.py                 ⭐ Generate the evaluation set
│   ├── eval_retrieval.py                   ⭐ Compare retrieval configurations
│   └── eval_generation.py                  ⭐ Evaluate answer quality
│
├── config.py                               # Project configuration
├── build_index.py                          # Build all indexes
└── main.py                                 # Run the RAG system
```

## Summary

This project is designed for learning how a RAG system works step by step. **Stage 1 (Labs 01–07)** covers the core pipeline, including loading a Q&A knowledge base, splitting text into chunks, generating embeddings, building a FAISS vector database, and performing semantic search. **Stage 2** improves retrieval quality by adding BM25 keyword search, hybrid retrieval, cross-encoder reranking, query transformation, LLM answer generation with citations, and conversation memory.

All features can be enabled or disabled in **config.py**, making it easy to experiment with different RAG configurations. The project also includes an evaluation module that compares retrieval performance using **Hit@k, MRR, and nDCG**, allowing you to measure how much each technique improves the results.

The knowledge base contains **391 Thai sexual-health Q&A pairs (541 text chunks)**. The project runs without an API key by default and supports **Ollama, OpenAI, and Gemini** through a single interface.



