from app.llm.client import GeminiClient
from app.llm.config import load_llm_config
from app.llm.openai_client import OpenAIClient
from app.llm.openai_config import load_openai_config
from app.llm.protocols import LLMClient
from app.llm.provider import load_llm_provider


def build_llm_client() -> LLMClient:
    provider = load_llm_provider()

    if provider == "gemini":
        return GeminiClient(
            config=load_llm_config(),
        )

    return OpenAIClient(
        config=load_openai_config(),
    )
