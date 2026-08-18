"""Pure retrieval helpers shared by the runtime and regression tests."""

import re

import config


THAI_PATTERN = re.compile(r"[ก-๙]+")
ENGLISH_PATTERN = re.compile(r"[A-Za-z0-9]+")


def tokenize(text):
    """Tokenize mixed Thai/English text for BM25."""
    tokens = [match.group().lower() for match in ENGLISH_PATTERN.finditer(text)]
    for thai_text in THAI_PATTERN.findall(text):
        tokens.extend(tokenize_thai(thai_text))
    return tokens


def tokenize_thai(text):
    """Use PyThaiNLP when available, otherwise fall back to character trigrams."""
    try:
        from pythainlp.tokenize import word_tokenize

        return [word for word in word_tokenize(text, engine="newmm") if word.strip()]
    except ImportError:
        return [text[i:i + 3] for i in range(max(1, len(text) - 2))]


def top_positive_scores(scores, top_k):
    """Return the highest positive scores without treating zeroes as matches."""
    ranked = (
        (position, float(score))
        for position, score in enumerate(scores)
        if score > 0
    )
    return sorted(ranked, key=lambda item: (-item[1], item[0]))[:top_k]


def reciprocal_rank_fusion(ranked_lists, weights=None, rrf_k=None):
    """Combine rankings with optional per-list weights and deterministic ties."""
    if weights is None:
        weights = [1.0] * len(ranked_lists)
    if len(weights) != len(ranked_lists):
        raise ValueError("weights must contain one value for every ranked list")

    k = config.RRF_K if rrf_k is None else rrf_k
    scores = {}
    best_ranks = {}
    for ranked, weight in zip(ranked_lists, weights):
        if weight < 0:
            raise ValueError("RRF weights must be non-negative")
        for rank, position in enumerate(ranked, start=1):
            scores[position] = scores.get(position, 0.0) + weight / (k + rank)
            best_ranks[position] = min(best_ranks.get(position, rank), rank)

    return sorted(
        scores.items(),
        key=lambda item: (-item[1], best_ranks[item[0]], item[0]),
    )
