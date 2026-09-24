# Phase 15 — Optimization

## Status
**Completed ✅**

Final checkpoint:
```text
Ruff: passed
Pytest: 706 passed
Known warning: 1 google-genai deprecation warning
```

## Objective
Phase 15 focused on improving DecisionAI using measured evidence rather than adding complexity without justification.

The optimization loop was:
```text
measure
→ identify bottleneck
→ analyze root cause
→ make a small change
→ test
→ evaluate
→ compare
→ decide whether to continue
```

## 15.1 Optimization baseline
A real Gemini evaluation of `revenue_decline_v1` established the baseline:
```text
Used tools:
- analyze_revenue_drivers

Required tool coverage: 50%
Ground truth: 0%
Semantic safety: 100%
Overall result: FAIL
Latency: ~10.17 s
```

The infrastructure worked, but the agent skipped the deterministic aggregate revenue comparison.

## 15.2–15.6 Provider abstraction and cross-provider evaluation
DecisionAI introduced provider-neutral LLM protocols, an OpenAI adapter, configuration-driven provider selection, runtime validation, and provider-specific evaluation artifacts.

Supported provider names:
```text
gemini
openai
```

Gemini remains the default provider.

## 15.7 Optimization metrics
The evaluation system was extended with efficiency metrics including:
```text
average_tool_failures
average_tool_calls
average_steps
tool_success_rate
duplicate_tool_call_rate
```

## 15.8 Latency measurement
Evaluation runs now record wall-clock runtime through:
```text
average_latency_ms
```

Latency is treated as an evaluation/optimization concern rather than a domain contract.

## 15.9 Tool-selection optimization

### Root cause
The complex revenue question contained two analytical needs:
1. aggregate revenue comparison
2. observed revenue deterioration analysis

The prompt allowed the model to treat driver evidence as sufficient and finish without obtaining the aggregate comparison.

### Change
The agent prompt was improved with a general **evidence coverage policy**.

The policy requires the agent to verify that all requested analytical needs have sufficient evidence before returning a final answer.

The solution was intentionally not hardcoded to specific tool names.

### Regression protection
Prompt tests were added to protect:
- recognition of multiple analytical needs
- full evidence coverage
- rejection of partial coverage
- aggregate evidence requirements
- breakdown evidence requirements
- non-substitution between aggregate and driver evidence
- avoidance of redundant evidence calls

### Real evaluation result
After optimization:
```text
Used tools:
- analyze_revenue
- analyze_revenue_drivers

Required tool coverage: 100%
Ground truth: 100%
Semantic safety: 100%
Overall result: PASS
Steps: 3
Tool calls: 2
Tool failures: 0
Duplicate calls: 0%
Latency: ~9.39 s
```

### Anti-overtooling check
The simple case `revenue_comparison_only_v1` correctly used only:
```text
analyze_revenue
```

Result:
```text
Tool selection: 100%
Ground truth: 100%
Semantic safety: 100%
Overall result: PASS
Steps: 2
Tool calls: 1
Tool failures: 0
Duplicate calls: 0%
Latency: ~4.29 s
```

## 15.10 Multi-run stability
For the complex case, two quality-evaluated runs completed before a provider rate/quota limit was reached:
```text
Quality passes: 2/2
Tool selection: 100%
Ground truth: 100%
Semantic safety: 100%
Average steps: 3.0
Average tool calls: 2.0
Tool failures: 0
Duplicate calls: 0%
Average latency: ~8.68 s
```

The provider failure was recorded as availability, not as an AI-quality failure.

The multi-run simple-case check was deferred because the provider rate/quota limit was reached before a quality-evaluable run completed.

## 15.11 Optimization decision
Decision:
> Do not make further agent changes without evidence of a concrete quality problem.

Rationale:
- current quality cases pass
- numeric ground truth passes
- semantic safety passes
- no duplicate tool calls observed
- no tool failures observed
- simple cases do not over-tool
- further prompt/agent changes would increase regression risk without a demonstrated need

## 15.12 Final validation
Final repository validation:
```text
Ruff check: passed
Ruff format: clean
Pytest: 706 passed
```

Phase 15 artifacts confirmed:
```text
artifacts/phase15/gemini/revenue_decline_v1_eval.json
artifacts/phase15/gemini/revenue_comparison_only_v1_eval.json
```

## What Phase 15 demonstrated
The main lesson was the engineering process:
```text
working system
→ measurable failure
→ root-cause analysis
→ smallest justified change
→ regression tests
→ live evaluation
→ stability check
→ stop when evidence is sufficient
```

## Deferred work
Intentionally deferred:
- larger multi-run evaluation samples
- full successful OpenAI quality evaluation when provider credits are available
- production-grade external telemetry
- deeper latency/cost optimization
- Gemini AFC warning cleanup
- infrastructure/container optimization

## Next phase
**Phase 16 — Docker + CI/CD + Cloud**
