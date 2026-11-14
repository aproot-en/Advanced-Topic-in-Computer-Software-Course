### evaluate.py - evaluation gate with the [C7] targets
### 1) Router accuracy     >= 0.90  (03)
### 2) Retrieval Recall@5  >= 0.85  (05)  + MRR + no-answer
### 3) Generation: citation accuracy >= 0.90, faithfulness >= 0.85 (06)
### Run: python evaluate.py (exit code 1 = a target failed; can block a CI merge)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "09_backend"))
import setup_path  ### add folders 02-09 to sys.path (must come first)
import json
import re
from collections import Counter

import config
import router_agent
import engines
import generation
from retrieval import get_retriever
from thai_text import tokenize

TARGETS = {"router_accuracy": 0.90, "recall_at_5": 0.85, "citation_accuracy": 0.90,
           "faithfulness": 0.85}
USER = {"role": "student", "faculty": "engineering"}


def load(name):
    return json.loads((config.EVAL_DIR / name).read_text(encoding="utf-8"))


def eval_router():
    rows = load("eval_router.json")
    correct = 0
    confusion = Counter()
    for row in rows:
        got = router_agent.decide(row["q"], [])["response_type"]
        confusion[(row["type"], got)] += 1
        if got == row["type"]:
            correct += 1
        else:
            print(f"  [router miss] {row['q']} -> {got} (expected {row['type']})")
    print("  confusion (expected, got):", dict(confusion))
    return correct / len(rows)


def eval_retrieval():
    rows = load("eval_retrieval.json")
    retriever = get_retriever()
    hits, rr, answerable, no_answer_ok, no_answer = 0, 0.0, 0, 0, 0
    for row in rows:
        found = retriever.search(row["q"], USER, top_n=5, lang=row["lang"])["chunks"]
        doc_ids = [c["metadata"]["doc_id"] for c in found]
        if not row["docs"]:
            no_answer += 1
            no_answer_ok += int(not found)
            if found:
                print(f"  [no-answer miss] {row['q']} -> {doc_ids[:3]}")
            continue
        answerable += 1
        ranks = [i + 1 for i, d in enumerate(doc_ids) if d in row["docs"]]
        if ranks:
            hits += 1
            rr += 1 / ranks[0]
        else:
            print(f"  [retrieval miss] {row['q']} -> {doc_ids[:3]}")
    print(f"  MRR={rr / answerable:.3f}  no-answer correct={no_answer_ok}/{no_answer}")
    return hits / answerable


def eval_generation():
    ### simple proxy: most words of each bullet with [n] must appear in document n
    rows = [r for r in load("eval_retrieval.json") if r["docs"]]
    cited_ok, cited_total, faithful, sentences, duplicates = 0, 0, 0, 0, 0
    for row in rows:
        decision = router_agent.decide(row["q"], [])
        if decision["route"] != "university_rag":
            continue
        results, _ = engines.run_engines(decision, USER)
        draft = generation.generate(row["q"], decision, results, [])
        chunks = {c["ref"]: c for c in results[0].chunks} if results else {}
        lines = [l for l in draft["answer"].split("\n") if l.startswith("- ")]
        duplicates += len(lines) - len(set(lines))
        for line in lines:
            sentences += 1
            refs = [int(x) for x in re.findall(r"\[(\d+)\]", line)]
            tokens = set(tokenize(line))
            support = [len(tokens & set(tokenize(chunks[r]["text"]))) / max(len(tokens), 1)
                       for r in refs if r in chunks]
            cited_total += len(refs)
            cited_ok += sum(1 for s in support if s >= 0.7)
            faithful += int(bool(support) and max(support) >= 0.7)
    print(f"  duplicate bullets={duplicates}")
    return cited_ok / max(cited_total, 1), faithful / max(sentences, 1)


if __name__ == "__main__":
    scores = {}
    print("[03] router")
    scores["router_accuracy"] = eval_router()
    print("[05] retrieval")
    scores["recall_at_5"] = eval_retrieval()
    print("[06] generation")
    scores["citation_accuracy"], scores["faithfulness"] = eval_generation()

    failed = False
    print("\nresult")
    for name, target in TARGETS.items():
        ok = scores[name] >= target
        failed = failed or not ok
        print(f"  {name:18s} {scores[name]:.3f}  target >= {target}  {'PASS' if ok else 'FAIL'}")
    sys.exit(1 if failed else 0)
