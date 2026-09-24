from typing import Protocol, TypeVar

from pydantic import BaseModel

from app.llm.contracts import LLMInterpretation

StructuredResponseT = TypeVar(
    "StructuredResponseT",
    bound=BaseModel,
)


class StructuredLLMClient(Protocol):
    def generate_structured(
        self,
        prompt: str,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        """Generate a structured LLM response."""


class InterpretationLLMClient(Protocol):
    def generate_interpretation(
        self,
        prompt: str,
    ) -> LLMInterpretation:
        """Generate a grounded LLM interpretation."""


class LLMClient(
    StructuredLLMClient,
    InterpretationLLMClient,
    Protocol,
):
    def generate_text(
        self,
        prompt: str,
    ) -> str:
        """Generate a plain-text LLM response."""
