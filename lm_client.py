from typing import List, Dict, Any

from openai import OpenAI


class LMStudioClient:
    """Thin wrapper around LM Studio's OpenAI-compatible server.

    Usage:
        client = LMStudioClient()
        reply = client.chat(
            model="microsoft/phi-4-mini-reasoning",
            messages=[{"role": "user", "content": "Xin chào"}],
        )
    """

    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1", api_key: str = "lm-studio") -> None:
        self._client = OpenAI(base_url=base_url, api_key=api_key)

    def chat(self, model: str, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content


