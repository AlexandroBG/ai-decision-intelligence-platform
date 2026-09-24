# Phase 15 — Evaluation Summary

## Checkpoint
```text
706 tests passed
1 known google-genai deprecation warning
```

## Complex case
Case:
```text
revenue_decline_v1
```

### Before optimization
```text
Used tools:
- analyze_revenue_drivers

Required tool coverage: 50%
Ground-truth score: 0%
Semantic safety: 100%
Overall: FAIL
Steps: 2
Tool calls: 1
Latency: ~10.17 s
```

### After optimization
```text
Used tools:
- analyze_revenue
- analyze_revenue_drivers

Required tool coverage: 100%
Ground-truth score: 100%
Semantic safety: 100%
Overall: PASS
Steps: 3
Tool calls: 2
Tool failures: 0
Duplicate calls: 0%
Latency: ~9.39 s
```

## Complex-case multi-run check
Three runs were requested. Two reached quality evaluation and both passed. The third encountered a provider rate/quota limit and was recorded as an availability failure rather than an AI-quality failure.

```text
Requested runs: 3
Attempted runs: 3
Quality-evaluated runs: 2
Provider errors: 1

Quality passes: 2/2
Overall quality pass rate: 100%
Tool-selection pass rate: 100%
Ground-truth pass rate: 100%
Semantic-safety pass rate: 100%

Average steps: 3.00
Average tool calls: 2.00
Average tool failures: 0.00
Average latency: ~8677 ms
Tool success rate: 100%
Duplicate tool-call rate: 0%
```

## Simple case
Case:
```text
revenue_comparison_only_v1
```

Observed:
```text
Used tools:
- analyze_revenue

Required tool coverage: 100%
Ground-truth score: 100%
Semantic safety: 100%
Overall: PASS
Steps: 2
Tool calls: 1
Tool failures: 0
Duplicate calls: 0%
Latency: ~4.29 s
```

This provides evidence that the optimization did not create obvious over-tooling.

## Availability caveat
A later multi-run simple-case attempt was blocked immediately by a provider rate/quota limit.

No AI-quality conclusion was drawn from that failure.

DecisionAI records provider availability separately from model-quality metrics.

## Interpretation
The optimization improved analytical coverage without introducing a visible regression in:
- semantic safety
- tool reliability
- duplicate calls
- simple-case tool efficiency

Latency remains provider-dependent and requires a larger sample before making performance claims.

## Artifacts
```text
artifacts/phase15/gemini/revenue_decline_v1_eval.json
artifacts/phase15/gemini/revenue_comparison_only_v1_eval.json
```
