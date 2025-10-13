import os
import httpx
from typing import List, Dict, Any, Optional

NVIDIA_API_BASE = os.getenv("NVIDIA_API_BASE", "https://integrate.api.nvidia.com/v1")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "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")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1")

HEADERS = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Content-Type": "application/json",
}

class NimError(Exception):
    pass

async def chat_completion(messages: List[Dict[str, Any]],
                          model: Optional[str] = None,
                          max_tokens: int = 800,
                          temperature: float = 0.2,
                          response_format: Optional[Dict[str, Any]] = None) -> str:
    """
    Calls NVIDIA NIM's OpenAI-compatible chat completions endpoint and returns content text.
    """
    if not NVIDIA_API_KEY:
        raise NimError("Missing NVIDIA_API_KEY in environment")

    payload: Dict[str, Any] = {
        "model": model or NVIDIA_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if response_format:
        payload["response_format"] = response_format

    url = f"{NVIDIA_API_BASE}/chat/completions"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=HEADERS, json=payload)
        if r.status_code >= 400:
            raise NimError(f"NIM error {r.status_code}: {r.text}")
        data = r.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise NimError(f"Unexpected NIM response: {data}") from e
