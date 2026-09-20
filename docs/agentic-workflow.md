# Phase 09 — Agentic Workflow

## Status

Completed and validated with real Gemini executions.

## Objective

Build a single-agent DecisionAI workflow in which Gemini decides which deterministic tools to call, consumes their observations, and returns a grounded final answer under explicit stopping and safety rules.

## Architecture

```text
User question
   ↓
AgentDecisionClient
   ↓
Gemini
   ↓
AgentDecision
   ├─ Tool action → ToolExecutor → ToolResult → AgentHistory
   └─ Final action → evidence_steps → grounded_claims → AgentRunResult
```

## What was implemented

### Agent contracts

- `AgentToolAction`
- `AgentFinalAction`
- discriminated `AgentAction`
- `AgentDecision`
- `AgentObservation`
- `AgentHistory`
- `AgentRunResult`

### Agent decision layer

The agent receives the original business question, registered tool catalog, prior tool observations, and stable run-level evidence IDs. The LLM must choose exactly one next action.

### Single and multi-step execution loop

The runtime supports one or more tool calls, observation accumulation, final-answer generation, maximum-step enforcement, tool-failure limits, and duplicate-tool-call detection.

### Structured stopping conditions

The loop exposes observable statuses including:

- `completed`
- `max_steps_reached`
- `duplicate_tool_call`
- `tool_failure_limit_reached`
- `invalid_final_evidence`
- `invalid_final_grounding`

Expected workflow guardrails become structured run outcomes rather than opaque exceptions.

### Final-answer evidence contract

When tools have been used:

- the final answer must declare `evidence_steps`;
- the final answer must include `grounded_claims`;
- every referenced step must exist;
- facts and inferences must reference valid evidence IDs;
- declared evidence steps must match the evidence IDs used by grounded claims.

### Agent grounding bridge

Each tool observation receives a stable run-level ID:

- step 1 → `tool_step_1`
- step 2 → `tool_step_2`
- etc.

This creates a deterministic bridge between workflow history and grounding validation.

### Provider-boundary normalization

Real Gemini evaluation revealed that the provider sometimes emitted `action_type = "call"` while DecisionAI's canonical internal contract is `action_type = "tool_call"`.

A narrow provider alias normalization was introduced:

`call → tool_call`

Unknown alternatives remain invalid.

### Structured-output provider integration

Real Gemini evaluation also exposed provider-schema differences.

The Gemini adapter was updated to:

- use `response_json_schema`;
- derive JSON Schema from the Pydantic response model;
- validate `response.parsed` when available;
- fall back to validating `response.text` JSON;
- preserve Pydantic as the final application-level authority;
- expose concise validation diagnostics without leaking prompts or secrets.

## Guardrails

The agent is instructed and validated to:

- use only registered tools;
- never invent tool names;
- use deterministic tools for calculations;
- avoid duplicate calls;
- avoid causal overclaiming;
- avoid summing contribution values across overlapping dimensions;
- reference only existing observation steps;
- reference only existing evidence IDs;
- provide grounded claims after using tools.

## Real Gemini evaluation

Model: `gemini-2.5-flash`

Dataset:

- 2,250 orders
- 300 customers
- 20 products

Evaluation question:

> Compare revenue from 2025-07-01 to 2025-07-31 with 2025-08-01 to 2025-08-31. What is affecting revenue performance, and what should I investigate first?

### Three-run result

| Metric | Result |
|---|---:|
| Requested runs | 3 |
| Completed runs | 3 |
| Guardrail terminations | 0 |
| Execution errors | 0 |
| Total tool calls | 7 |
| Tool failures | 0 |

Observed tool sequences:

1. `analyze_revenue → analyze_revenue_drivers → detect_revenue_anomalies`
2. `analyze_revenue → analyze_revenue_drivers`
3. `analyze_revenue → analyze_revenue_drivers`

All three runs completed successfully with valid evidence steps and grounded claims.

### Observed business answer stability

Across runs, the model consistently reported:

- July 2025 revenue: approximately 1,773,419.93
- August 2025 revenue: approximately 1,275,769.95
- absolute change: approximately -497,649.98
- percentage change: approximately -28.06%
- Computing as the strongest observed category deterioration

One run also used anomaly evidence before producing the final answer.

## Important interpretation boundary

The observed driver dimensions overlap.

For example:

- Computing is a category
- South is a region
- SMB is a segment

Their contribution percentages are therefore not mutually exclusive and must not be summed as a decomposition of total decline.

The agent respected the no-summing rule in the evaluated runs.

The recommendation to investigate Computing first is an inference from observed deterioration, not a causal conclusion.

## Known limitations

### Tool-level grounding is coarse

Current agent evidence IDs refer to whole tool observations (`tool_step_N`) rather than granular business evidence items.

### Free-form answer is not yet deterministically derived from grounded claims

The final answer and `grounded_claims` are returned together, but the system does not yet prove that every factual sentence in the free-form answer has an equivalent canonical grounded claim.

### Semantic quality requires formal evaluation

A claim can reference valid evidence while still being poorly worded, overly broad, or semantically imprecise.

These limitations are intentionally carried into Phase 10 — Evaluation Framework, where they can be measured before adding architectural complexity.

## Engineering lessons from real evaluation

The real provider evaluation revealed issues that unit tests alone could not expose:

1. Pydantic structured schemas interacted differently with the Gemini Developer API.
2. `response_json_schema` was required at the provider boundary.
3. `response.parsed` required a JSON-text validation fallback.
4. Gemini emitted `call` instead of DecisionAI's canonical `tool_call`.
5. Provider normalization belonged at the system boundary rather than inside business logic.

This validates the development loop:

```text
PLAN
→ BUILD
→ TEST
→ REAL EVALUATE
→ ERROR ANALYSIS
→ DECIDE
→ ITERATE
```

## Source principles applied in this phase

### AI Engineering / Andrew Ng

- Build agentic systems around deterministic components.
- Evaluate the full system, not only the model in isolation.
- Use coding and AI agents with verification rather than blind trust.
- Iterate from observed failures.

### AI Engineering Skills Map / Coding Agents

- Tool use, context engineering, agent workflows, structured outputs, and evaluation are separate engineering concerns.
- Agent behavior must be observable and testable.
- Coding-agent and model outputs require verification.

### Shaping the Build

- Start with a single agent.
- Add complexity only when evaluation demonstrates a need.
- Close uncertainty progressively through real execution.

### Building and Deploying AI Applications

- Keep provider SDK behavior at architecture edges.
- Separate LLM decisions from deterministic tools.
- Model expected failures explicitly.
- Validate structured provider outputs in application code.

### Software Engineering Fundamentals

- Canonical internal contracts.
- Narrow normalization at system boundaries.
- Explicit state machines and statuses.
- Regression tests for production-discovered failures.
- Do not hide unexpected programming errors.

## Phase conclusion

Phase 09 establishes a working single-agent DecisionAI orchestration layer with deterministic tool use, explicit stopping conditions, grounding validation, provider-boundary normalization, and successful real Gemini execution.

The agentic workflow is now ready for Phase 10 — Evaluation Framework, where reliability, semantic correctness, tool-choice quality, grounding quality, efficiency, and failure patterns will be measured systematically.
