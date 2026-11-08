import os
from openai import OpenAI

from .base import AIProvider


class GroqProvider(AIProvider):
    """Groq는 OpenAI 호환 API를 사용합니다. 선택 구성입니다."""

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        model = os.environ.get("GROQ_MODEL")
        if not api_key or not model:
            raise RuntimeError("GROQ_API_KEY와 GROQ_MODEL을 모두 설정해야 합니다.")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model

    def generate_json(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"
