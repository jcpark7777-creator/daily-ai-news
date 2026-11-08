import os
from google import genai
from google.genai import types

from .base import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        self.client = genai.Client(api_key=api_key)
        self.model = os.environ.get("GEMINI_MODEL") or "gemini-3.8-flash"

    def generate_json(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return response.text or "{}"
