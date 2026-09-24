# Phase 15 — Optimization Decision Record

## Decision
**Stop agent optimization at the end of Phase 15 and proceed to deployment engineering.**

## Context
The initial real evaluation showed that the agent could produce a plausible answer while still failing an important analytical requirement.

The question required:
```text
1. aggregate revenue comparison
2. observed deterioration analysis
```

The agent originally performed only the second task.

## Initial evidence
```text
Required tool coverage: 50%
Ground truth: 0%
Semantic safety: 100%
Overall result: FAIL
```

The failure was classified as a planning/evidence-sufficiency problem.

## Alternatives considered

### Hardcode tool order
Example:
```text
always call analyze_revenue before analyze_revenue_drivers
```
Rejected because it would couple the agent to a specific case and reduce generality.

### Change the evaluator to accept driver analysis alone
Rejected because the driver tool does not provide the required aggregate comparison contract.

### Add a more complex planner
Rejected because the current failure could be corrected with a smaller prompt-policy change.

### Improve evidence-coverage policy
Selected.

The agent now checks whether all requested analytical needs are covered before returning a final answer.

## Result
The complex evaluation moved from:
```text
FAIL
50% required-tool coverage
0% numeric ground truth
```
to:
```text
PASS
100% required-tool coverage
100% numeric ground truth
100% semantic safety
```

The simple comparison-only case continued to use one tool and passed, showing that the change did not introduce obvious over-tooling.

## Stability evidence
Two additional quality-evaluated complex runs passed before the provider hit a rate/quota limit:
```text
Quality: 2/2 PASS
Tool selection: 100%
Ground truth: 100%
Semantic safety: 100%
Tool failures: 0
Duplicates: 0%
```

## Trade-offs
The complex case requires an additional tool call compared with the failing baseline.

This is accepted because the extra call supplies evidence explicitly requested by the user.

No clear latency regression was observed, but the sample size is too small to claim a speed improvement.

## Final optimization decision
No further agent modifications are justified by current evidence.

Future optimization should begin only when evaluations identify a concrete problem such as:
- repeated unnecessary calls
- unacceptable latency
- excessive cost
- semantic regressions
- tool-selection failures
- provider-specific quality differences

## Principle
> Optimize measured failures, not hypothetical complexity.
