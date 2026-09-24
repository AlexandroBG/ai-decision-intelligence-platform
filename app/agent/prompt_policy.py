from app.agent.language_policy import (
    OBSERVATIONAL_LANGUAGE_POLICY,
)


def apply_language_policy(
    prompt: str,
) -> str:
    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        raise ValueError("Prompt must not be empty.")

    return f"{cleaned_prompt}\n\n{OBSERVATIONAL_LANGUAGE_POLICY}"
