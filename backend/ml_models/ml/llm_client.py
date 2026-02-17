"""
Lightweight LLM client for skill expansion and contextual inference.
Supports Gemini REST and OpenAI-compatible endpoints (e.g., OpenRouter/Groq).
"""

import json
import os
import re
import urllib.request
from typing import Any, Dict, Optional


class LLMClient:
    def __init__(self):
        self.enabled = os.getenv("LLM_ENABLED", "false").lower() == "true"
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        self.base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "512"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    def _post_json(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _gemini_request(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": self.temperature, "maxOutputTokens": self.max_tokens},
        }
        headers = {"Content-Type": "application/json"}
        result = self._post_json(url, payload, headers)
        candidates = result.get("candidates", [])
        if not candidates:
            return None
        return candidates[0]["content"]["parts"][0]["text"]

    def _openai_compatible_request(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        result = self._post_json(url, payload, headers)
        choices = result.get("choices", [])
        if not choices:
            return None
        return choices[0]["message"]["content"]

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    def extract_skills(self, resume_text: str, jd_text: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        prompt = (
            "Extract normalized skills from the resume and JD. "
            "Return strict JSON with keys: resume_skills, jd_required, jd_preferred, synonyms. "
            "Use lower-case canonical forms (e.g., 'machine learning', 'computer vision', 'javascript'). "
            "Keep resume_skills to max 30 items. "
            "JD required/preferred should be explicit from the JD if possible.\n\n"
            f"RESUME:\n{resume_text[:2000]}\n\n"
            f"JD:\n{jd_text[:2000]}\n"
        )
        if self.provider == "gemini":
            response = self._gemini_request(prompt)
        elif self.provider in {"openai", "openrouter", "groq", "openai_compatible", "hf", "huggingface"}:
            response = self._openai_compatible_request(prompt)
        else:
            return None
        if not response:
            return None
        return self._extract_json(response)
