from __future__ import annotations

import json
import logging

import httpx
from pydantic import ValidationError

from app.llm.contract import LLMProvider, LLMProviderError, LLMProviderTimeout
from app.llm.models import LLMScamAnalysisRequest, LLMScamAnalysisResult
from app.llm.prompts.scam_analysis import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger("cyberalerta.llm")


def _extract_json(content: str) -> dict:
    """Pull the JSON object out of a chat completion's text content.

    Tolerates a stray ```json fence but nothing more — anything that is not a
    parseable object raises, and the caller turns that into a safe fallback.
    """
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text[:4].lower() == "json":
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise LLMProviderError("no JSON object in LLM response")
    return json.loads(text[start : end + 1])


class OpenAICompatibleProvider(LLMProvider):
    """Calls any OpenAI-compatible /chat/completions endpoint (OpenAI, OpenRouter, …).

    The API key is only ever used as a bearer header; it is never logged, never
    put into exceptions, and never returned. Failures are normalized to
    :class:`LLMProviderError` / :class:`LLMProviderTimeout` with generic text.
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 12.0,
        temperature: float = 0.0,
        name: str = "openai_compatible",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self.model = model
        self._timeout = timeout_seconds
        self._temperature = temperature
        self.name = name

    def analyze_scam(self, request: LLMScamAnalysisRequest) -> LLMScamAnalysisResult:
        payload = {
            "model": self.model,
            "temperature": self._temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(request)},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self._base_url}/chat/completions"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=payload, headers=headers)
        except httpx.TimeoutException:
            raise LLMProviderTimeout("LLM request timed out") from None
        except httpx.HTTPError:
            # Do NOT chain the original exception: httpx errors can embed the
            # request URL/headers. Raise a clean, generic error instead.
            raise LLMProviderError("LLM transport error") from None

        if response.status_code >= 400:
            # Log status only — never the body (may echo the prompt) or the key.
            logger.warning("LLM endpoint returned HTTP %s", response.status_code)
            raise LLMProviderError(f"LLM endpoint HTTP {response.status_code}")

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            raise LLMProviderError("malformed LLM response envelope") from None

        try:
            data = _extract_json(content)
            return LLMScamAnalysisResult.model_validate(data)
        except (ValueError, ValidationError):
            # Invalid/hallucinated output -> caller treats as unavailable.
            raise LLMProviderError("LLM output failed schema validation") from None
