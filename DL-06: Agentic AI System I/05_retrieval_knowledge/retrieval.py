### retrieval.py - 05 retrieval pipeline (runs for every question)
### ACL filter → vector search (PyTorch cosine) + BM25 (PyThaiNLP) → RRF → rerank → top N

import json
import torch
from rank_bm25 import BM25Okapi

import config
import embedder
from thai_text import tokenize

### which access_level each role can see
ROLE_ACCESS = {
    "student": ["public", "student"],
    "staff": ["public", "student", "staff"],
    "admin": ["public", "student", "staff"],
}


class Retriever:
    def __init__(self):
        self.chunks = json.loads((config.INDEX_DIR / "chunks.json").read_text(encoding="utf-8"))
        saved = torch.load(config.INDEX_DIR / "embeddings.pt", weights_only=True)
        self.vectors = saved["vectors"]
        self.bm25 = BM25Okapi([tokenize(c["metadata"]["title"] + " " + c["text"]) for c in self.chunks])
        self.reranker = None
        self.reranker_failed = False

    def documents_info(self):
        active = {c["metadata"]["doc_id"]: c["metadata"]["published_at"]
                  for c in self.chunks if c["metadata"]["status"] == "active"}
        return len(active), max(active.values()) if active else None

    def allowed_ids(self, user_context, lang=None):
        ### filter before search: active only, role, faculty, same language
        role = user_context.get("role", "student")
        faculty = user_context.get("faculty", "all")
        ids = []
        for i, c in enumerate(self.chunks):
            m = c["metadata"]
            if m["status"] != "active":
                continue
            if lang and c["lang"] not in (lang, "mixed"):
                continue
            if m["access_level"] not in ROLE_ACCESS.get(role, ["public"]):
                continue
            if m["faculty"] not in ("all", faculty):
                continue
            ids.append(i)
        return ids

    def vector_search(self, query, ids, k):
        q = embedder.encode([query])[0]
        scores = self.vectors[ids] @ q
        order = torch.argsort(scores, descending=True)[:k]
        return [ids[i] for i in order.tolist()]

    def bm25_search(self, query, ids, k):
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(ids, key=lambda i: scores[i], reverse=True)
        return [i for i in ranked[:k] if scores[i] > 0]

    def rerank(self, query, ids):
        ### cross-encoder scores (query, chunk); keep the old order if it fails
        if not config.RERANK_ENABLED or self.reranker_failed:
            return [(i, None) for i in ids]
        ### no candidates: skip the model (avoids turning the reranker off for good)
        if not ids:
            return []
        try:
            if self.reranker is None:
                from sentence_transformers import CrossEncoder
                ### max_length=512 is enough for our chunks (default 8192 is very slow)
                self.reranker = CrossEncoder(config.RERANKER_MODEL, device=embedder.get_device(),
                                             max_length=512)
            pairs = [(query, self.chunks[i]["text"]) for i in ids]
            scores = self.reranker.predict(pairs, activation_fn=torch.nn.Sigmoid())
            return sorted(zip(ids, [float(s) for s in scores]), key=lambda x: x[1], reverse=True)
        except Exception as e:
            print("reranker error:", e)
            self.reranker_failed = True
            return [(i, None) for i in ids]

    def search(self, query, user_context, method="hybrid_rrf", top_n=5, lang=None,
               force_degraded=False):
        degraded = []
        ids = self.allowed_ids(user_context, lang)
        k = config.RETRIEVAL_TOP_K

        ### 1) keyword and vector search
        bm25_ids = self.bm25_search(query, ids, k) if method != "vector" else []
        vec_ids = []
        if method != "bm25":
            try:
                if force_degraded:
                    raise RuntimeError("simulated vector db outage")
                vec_ids = self.vector_search(query, ids, k)
            except Exception:
                degraded.append("vector_db")
                bm25_ids = self.bm25_search(query, ids, k)

        ### 2) Reciprocal Rank Fusion: score = sum(1 / (RRF_K + rank))
        fused = {}
        for ranked in [bm25_ids, vec_ids]:
            for rank, i in enumerate(ranked, start=1):
                fused[i] = fused.get(i, 0) + 1 / (config.RRF_K + rank)
        candidates = sorted(fused, key=fused.get, reverse=True)[:k]

        ### 3) rerank and keep top N; best score too low = no relevant document
        reranked = self.rerank(query, candidates)
        if reranked and reranked[0][1] is not None and reranked[0][1] < config.RERANK_MIN_SCORE:
            return {"chunks": [], "reason": "no_relevant_document", "degraded": degraded}
        if reranked and reranked[0][1] is not None:
            reranked = [(i, s) for i, s in reranked if s >= config.RERANK_MIN_SCORE]

        results = []
        for ref, (i, score) in enumerate(reranked[:top_n], start=1):
            c = self.chunks[i]
            results.append({"ref": ref, "chunk_id": c["chunk_id"], "text": c["text"],
                            "metadata": c["metadata"],
                            "score": round(score if score is not None else fused[i], 4),
                            "untrusted": True})
        reason = None if results else "no_relevant_document"
        return {"chunks": results, "reason": reason, "degraded": degraded}


_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
