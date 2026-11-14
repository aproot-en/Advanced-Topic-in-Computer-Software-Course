# llm_client.py
# Small helper to call a free Llama model through an API (used by Module 03 and Module 07).
#
# Default provider: Groq (has a free tier and serves Llama models, OpenAI-compatible format).
#   1) Create a free API key at https://console.groq.com
#   2) Put it in a file named .env in the project root:   LLM_API_KEY=your_key_here
#   3) Restart the system. Without a key the system still works (rules + templates only).
#
# You can switch to another OpenAI-compatible provider by setting LLM_API_URL and LLM_MODEL.
# Check the provider's docs for the current free models; model names change over time.

import json
import os

import httpx

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_env_file(path=os.path.join(ROOT, ".env")):
    """Read KEY=VALUE lines from the .env file (only if the variable is not set already)."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


load_env_file()

LLM_API_URL = os.getenv("LLM_API_URL") or "https://api.groq.com/openai/v1/chat/completions"
LLM_MODEL = os.getenv("LLM_MODEL") or "llama-3.3-70b-versatile"
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "15"))


def enabled():
    return bool(LLM_API_KEY)


async def chat(system_text, user_text, max_tokens=300, want_json=False):
    """Send one question to the Llama API and return the answer text."""
    body = {
        "model": LLM_MODEL,
        "temperature": 0,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ],
    }
    if want_json:
        body["response_format"] = {"type": "json_object"}
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        r = await client.post(LLM_API_URL, headers=headers, json=body)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


async def chat_json(system_text, user_text, max_tokens=300):
    """Same as chat() but returns a dict. Returns None if the answer is not valid JSON."""
    text = await chat(system_text, user_text, max_tokens, want_json=True)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None
