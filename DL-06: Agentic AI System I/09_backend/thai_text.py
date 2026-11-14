### thai_text.py - Thai text tools [C4]
### PyThaiNLP newmm tokenizer, same for indexing and queries

import re
from pythainlp.tokenize import word_tokenize
from pythainlp.util import normalize as thai_normalize
from pythainlp.corpus import thai_stopwords

import config

THAI_CHAR = re.compile(r"[฀-๿]")
THAI_STOPWORDS = set(thai_stopwords())
EN_STOPWORDS = {"the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "for", "what",
                "how", "can", "i", "do", "does", "my", "me", "on", "at", "be", "with"}


def is_thai(text):
    return bool(THAI_CHAR.search(text))


def detect_language(text, default="th"):
    ### Thai letters = th, English letters = en
    if is_thai(text):
        return "th"
    if re.search(r"[a-zA-Z]", text):
        return "en"
    return default


def clean_text(text):
    ### remove zero-width spaces, normalize Thai vowels/tone marks and spaces
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = thai_normalize(text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def tokenize(text):
    ### tokens for BM25 / keywords: Thai words, lowercase English, no stopwords
    text = clean_text(text).lower()
    words = word_tokenize(text, engine=config.THAI_TOKENIZER_ENGINE, keep_whitespace=False)
    tokens = []
    for w in words:
        w = w.strip().strip("()[]{}:;,.!?\"'")
        if not w or not re.search(r"\w", w):
            continue
        if w in THAI_STOPWORDS or w in EN_STOPWORDS:
            continue
        tokens.append(w)
    return tokens


def split_sentences(text):
    ### split by line first (1 line = 1 article / table row)
    ### English lines are also split at periods (Thai has no sentence period)
    result = []
    for line in text.split("\n"):
        if is_thai(line):
            result.append(line.strip())
        else:
            ### don't split after a number, e.g. "Article 5."
            result += re.split(r"(?<=[.!?])(?<![0-9][.!?])\s+", line.strip())
    return [s for s in result if s]


def dedup_lines(lines):
    ### remove repeated sentences/bullets (the duplicate bullet bug in web_app.png)
    seen = set()
    result = []
    for line in lines:
        ### compare without bullets, [n] markers and extra spaces
        ### (keep digits, or "(1)" and "(2)" would look the same)
        key = re.sub(r"\[\d+\]", "", line)
        key = re.sub(r"^[\s\-\*•]+", "", key)
        key = re.sub(r"\s+", " ", key).strip().lower()
        if key and key in seen:
            continue
        seen.add(key)
        result.append(line)
    return result


def count_tokens(text):
    ### simple token count (PyThaiNLP words)
    return len(word_tokenize(text, engine=config.THAI_TOKENIZER_ENGINE, keep_whitespace=False))
