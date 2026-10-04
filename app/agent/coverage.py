from app.agent.contracts import AgentHistory

REVENUE_ANALYSIS_TOOL = "analyze_revenue"
REVENUE_DRIVERS_TOOL = "analyze_revenue_drivers"

_REVENUE_TERMS = (
    "revenue",
    "ingreso",
    "ingresos",
    "facturacion",
    "facturación",
)

_COMPARISON_TERMS = (
    "compare",
    "comparison",
    "change",
    "changed",
    "decline",
    "declined",
    "decrease",
    "decreased",
    "increase",
    "increased",
    "versus",
    " vs ",
    "between ",
    "comparar",
    "comparacion",
    "comparación",
    "cambio",
    "cambió",
    "disminucion",
    "disminución",
    "aumento",
)

_DRIVER_TERMS = (
    "affected",
    "affecting",
    "driver",
    "drivers",
    "deterioration",
    "deteriorations",
    "investigate",
    "why",
    "breakdown",
    "explain",
    "explanation",
    "region",
    "segment",
    "category",
    "channel",
    "afecto",
    "afectó",
    "afectando",
    "caida",
    "caída",
    "deterioro",
    "investigar",
    "por que",
    "por qué",
    "region",
    "región",
    "segmento",
    "categoria",
    "categoría",
    "canal",
)


def infer_required_tools(
    question: str,
) -> tuple[str, ...]:
    normalized = _normalize_text(question)

    if not normalized:
        return ()

    if not _mentions_revenue(normalized):
        return ()

    requires_comparison = _requires_aggregate_comparison(
        normalized_question=normalized,
    )

    requires_drivers = _requires_driver_analysis(
        normalized_question=normalized,
    )

    if requires_comparison and requires_drivers:
        return (
            REVENUE_ANALYSIS_TOOL,
            REVENUE_DRIVERS_TOOL,
        )

    return ()


def successful_tool_names(
    history: AgentHistory,
) -> set[str]:
    return {
        observation.call.tool_name
        for observation in history.observations
        if observation.result.success
    }


def missing_required_tools(
    question: str,
    history: AgentHistory,
) -> tuple[str, ...]:
    required_tools = infer_required_tools(
        question=question,
    )

    completed_tools = successful_tool_names(
        history=history,
    )

    return tuple(
        tool_name for tool_name in required_tools if tool_name not in completed_tools
    )


def build_coverage_retry_question(
    original_question: str,
    missing_tools: tuple[str, ...],
) -> str:
    normalized_question = original_question.strip()

    if not normalized_question:
        raise ValueError("Original question must not be empty.")

    if not missing_tools:
        raise ValueError("Missing tools must not be empty.")

    missing_tool_list = ", ".join(missing_tools)

    return (
        f"{normalized_question}\n\n"
        "RUNTIME COVERAGE FEEDBACK:\n"
        "The previous final answer was rejected because "
        "deterministic evidence required by the original "
        "question is still missing.\n"
        f"Missing required tool evidence: "
        f"{missing_tool_list}.\n"
        "Request the missing tool evidence before returning "
        "a final answer. Do not repeat successful tool calls."
    )


def _normalize_text(
    value: str,
) -> str:
    return " ".join(value.lower().split())


def _mentions_revenue(
    normalized_question: str,
) -> bool:
    return any(term in normalized_question for term in _REVENUE_TERMS)


def _requires_aggregate_comparison(
    normalized_question: str,
) -> bool:
    if any(term in normalized_question for term in _COMPARISON_TERMS):
        return True

    padded_question = f" {normalized_question} "

    has_from_to_range = " from " in padded_question and " to " in padded_question

    has_spanish_range = " de " in padded_question and " a " in padded_question

    return has_from_to_range or has_spanish_range


def _requires_driver_analysis(
    normalized_question: str,
) -> bool:
    return any(term in normalized_question for term in _DRIVER_TERMS)
