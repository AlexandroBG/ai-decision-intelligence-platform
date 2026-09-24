from app.agent.contracts import (
    AgentRunResult,
)
from app.evaluation.contracts import (
    EvaluationCase,
    ToolSelectionEvaluation,
)


def evaluate_tool_selection(
    case: EvaluationCase,
    result: AgentRunResult,
) -> ToolSelectionEvaluation:
    used_tools = _collect_unique_used_tools(result=result)

    required_tools = case.required_tools

    optional_tools = case.optional_tools

    used_tool_set = set(used_tools)

    required_tool_set = set(required_tools)

    allowed_tool_set = required_tool_set | set(optional_tools)

    missing_required_tools = [
        tool_name for tool_name in required_tools if tool_name not in used_tool_set
    ]

    unexpected_tools = [
        tool_name for tool_name in used_tools if tool_name not in allowed_tool_set
    ]

    if not required_tools:
        required_tool_coverage = 1.0
    else:
        used_required_tools = required_tool_set & used_tool_set

        required_tool_coverage = len(used_required_tools) / len(required_tool_set)

    passed = not missing_required_tools and not unexpected_tools

    return ToolSelectionEvaluation(
        used_tools=used_tools,
        required_tools=(required_tools),
        optional_tools=(optional_tools),
        missing_required_tools=(missing_required_tools),
        unexpected_tools=(unexpected_tools),
        required_tool_coverage=(required_tool_coverage),
        passed=passed,
    )


def _collect_unique_used_tools(
    result: AgentRunResult,
) -> list[str]:
    used_tools: list[str] = []

    seen: set[str] = set()

    for observation in result.history.observations:
        tool_name = observation.call.tool_name

        if tool_name in seen:
            continue

        seen.add(tool_name)

        used_tools.append(tool_name)

    return used_tools
