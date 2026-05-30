from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMService(ABC):
    @abstractmethod
    def generate(self, prompt: str, metadata: Dict[str, Any] | None = None) -> str:
        raise NotImplementedError()


class MockLLMService(LLMService):
    def generate(self, prompt: str, metadata: Dict[str, Any] | None = None) -> str:
        return "mock response"
