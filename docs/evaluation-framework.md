# Phase 10 — Evaluation Framework

## Status

**Completed**

DecisionAI now has a structured evaluation framework that measures execution quality, tool-selection quality, deterministic numeric correctness, semantic safety, multi-run stability, provider availability, suite-level quality, and explicit evaluation gates.

The phase closes with the evaluation suite passing all registered cases and the release gate passing.

## Phase Objective

Move DecisionAI from:

> "The agent appears to work."

to:

> "The agent is evaluated against explicit, repeatable, machine-readable quality criteria."

## Evaluation Architecture

```text
EvaluationCase
    |
    v
Agent Run
    |
    +--> Run Metrics
    +--> Tool Selection Evaluation
    +--> Ground-Truth Evaluation
    +--> Semantic Evaluation
    |
    v
Per-Run Result
    |
    v
Multi-Run Summary
    |
    v
Evaluation Suite
    |
    v
Suite Summary
    |
    v
Evaluation Gate
```

Provider failures are tracked separately and do not count as AI-quality failures.

## Evaluation Layers

### 1. Deterministic Run Metrics

The framework measures:

- completion status;
- steps used;
- tool calls;
- successful tool calls;
- tool failures;
- duplicate tool calls;
- tool success rate;
- duplicate tool-call rate;
- invalid final evidence;
- invalid final grounding.

### 2. Tool-Selection Quality

Each `EvaluationCase` defines required and optional tools.

A case passes tool selection only when all required tools are used and no unexpected tools are used.

This measures both capability and discipline.

### 3. Numeric Ground Truth

The official revenue ground truth is:

| Metric | Expected value |
|---|---:|
| Baseline revenue | 1773419.9302160002 |
| Comparison revenue | 1275769.9454039999 |
| Absolute change | -497649.9848120003 |
| Percentage-change ratio | -0.28061598741105115 |

The percentage is stored as a ratio, so `-0.280615...` corresponds to approximately `-28.06%`.

The LLM is never treated as the source of truth for deterministic arithmetic.

### 4. Semantic Safety

Current deterministic checks include:

- causal overclaim;
- unsupported certainty;
- overlap-summing risk;
- recommendation presence when the case requires one.

These rules are intentionally narrow and explainable. They are heuristics, not full semantic understanding.

### 5. Provider Failure Handling

Real Gemini quota failures such as:

```text
429 RESOURCE_EXHAUSTED
```

are classified separately from AI-quality failures.

Current categories include:

```text
rate_or_quota_limit
provider_error
```

The evaluator saves partial results, avoids misleading quality rates, and stops additional runs when continuing would be wasteful.

### 6. Multi-Run Evaluation

The framework aggregates:

- requested runs;
- attempted runs;
- evaluated runs;
- provider errors;
- quality pass rate;
- completion rate;
- tool-selection pass rate;
- ground-truth pass rate;
- semantic pass rate;
- average steps;
- average tool calls;
- tool success rate;
- duplicate tool-call rate;
- evaluation coverage.

If no quality run is available, quality metrics are reported as `N/A`.

### 7. Case Registry

Registered cases:

#### `revenue_decline_v1`

Purpose: identify revenue deterioration and what to investigate first.

Required tools:

```text
analyze_revenue
analyze_revenue_drivers
```

Optional:

```text
detect_revenue_anomalies
```

Recommendation required: `True`.

#### `revenue_comparison_only_v1`

Purpose: compare revenue only without unnecessary driver or anomaly analysis.

Required tools:

```text
analyze_revenue
```

Optional tools: none.

Recommendation required: `False`.

This case measures disciplined scope compliance and avoidance of unnecessary tools.

## Generic Runner

Cases can be selected with:

```powershell
$env:EVAL_CASE="revenue_decline_v1"
$env:EVAL_RUNS="1"
python scripts/evaluate_revenue_decline_case.py
```

or:

```powershell
$env:EVAL_CASE="revenue_comparison_only_v1"
$env:EVAL_RUNS="1"
python scripts/evaluate_revenue_decline_case.py
```

Artifacts are saved under:

```text
artifacts/phase10/
```

## Evaluation Suite

The full suite can be executed with:

```powershell
$env:EVAL_RUNS_PER_CASE="1"
python scripts/evaluate_suite.py
```

The suite produces per-case results, suite-level summary, evaluation coverage, provider-error count, overall suite status, and evaluation-gate output.

Combined artifact:

```text
artifacts/phase10/evaluation_suite.json
```

## Evaluation Gate

Default Phase 10 criteria:

```text
minimum evaluation coverage = 100%
minimum case pass rate      = 100%
provider errors             = 0
suite must complete         = True
```

The gate means:

> This version has enough evaluation evidence to advance.

It does not mean the application is production-ready.

## Final Phase 10 Results

Deterministic test suite:

```text
550 passed
1 warning
```

The warning is a non-blocking `google-genai` deprecation warning under Python 3.14.

Final real evaluation suite:

```text
revenue_decline_v1: PASS
revenue_comparison_only_v1: PASS
```

Suite summary:

```text
Requested cases:      2
Attempted cases:      2
Evaluated cases:      2
Provider errors:      0
Passed cases:         2
Case pass rate:       100%
Evaluation coverage:  100%
Suite completed:      True
Overall suite:        PASS
```

Evaluation gate:

```text
Suite completed check:       True
Coverage check:              True
Case pass-rate check:        True
Provider availability check: True
Failed checks:               []
RELEASE GATE:                PASS
```

## What Phase 10 Proves

DecisionAI can currently:

- complete the registered revenue-analysis tasks;
- select required tools;
- avoid unnecessary tools in a constrained case;
- reproduce deterministic numeric results;
- keep explanations within current semantic-safety constraints;
- provide recommendations when requested;
- avoid unnecessary recommendations when not requested;
- aggregate repeated evaluation results;
- distinguish provider failures from AI-quality failures;
- evaluate multiple cases through a common suite;
- enforce explicit evaluation gates.

## What Phase 10 Does Not Prove

The current framework does not prove:

- causal correctness;
- generalization across arbitrary datasets;
- robustness across many unseen user phrasings;
- production reliability;
- adversarial robustness;
- security;
- latency or cost targets;
- correctness of every free-form natural-language statement;
- full behavioral coverage.

The semantic evaluator remains heuristic and the suite currently contains only two registered cases.

## Known Language Risk

Some successful outputs use wording such as:

```text
"largest driver"
"primary factor"
"root causes"
```

The underlying evidence supports ranking observed deterioration, not proving causality.

This should be examined in Phase 11 before adding more evaluation complexity.

## Source Principles Applied

### AI Engineering / Andrew Ng

- systematic evaluation;
- iteration from observed failures;
- deterministic logic outside the LLM;
- verification instead of blind trust;
- engineering systems around models.

### AI Engineering Skills Map / Coding Agents

- evaluation infrastructure;
- tool-use verification;
- context-grounded behavior;
- agentic workflow testing;
- provider/runtime error handling.

### Shaping the Build

- close uncertainty progressively;
- start narrow;
- add complexity only when justified;
- define acceptance criteria explicitly;
- avoid premature benchmark complexity.

### Building and Deploying AI Applications

- separate deterministic logic from LLM behavior;
- make provider failures explicit;
- use machine-readable evaluation artifacts;
- prepare outputs for CI/CD and observability;
- establish gates before deployment.

### Software Engineering Fundamentals

- explicit contracts;
- modular components;
- single responsibility;
- deterministic tests;
- reusable interfaces;
- clear error categories;
- stable machine-readable outputs.

## Engineering Decisions

### Deterministic calculations remain outside the LLM

Revenue calculations are exact and belong in Python.

### Semantic checks begin with deterministic heuristics

LLM-as-judge would add cost, nondeterminism, and another provider dependency. It should be introduced only if error analysis justifies it.

### Provider errors are not AI-quality failures

A quota or upstream outage says nothing about answer quality when no answer was produced.

### Cases explicitly define tool expectations

Unnecessary tools increase latency, cost, complexity, and failure probability.

### The gate requires full coverage in Phase 10

With only two registered cases, partial execution provides insufficient evidence.

### Suite artifacts are JSON

Structured artifacts can later feed CI/CD, dashboards, observability, and portfolio reporting.

## Phase Exit Criteria

- [x] deterministic run metrics;
- [x] tool-selection evaluation;
- [x] numeric ground truth;
- [x] semantic safety evaluation;
- [x] provider failure classification;
- [x] multi-run summaries;
- [x] multiple evaluation cases;
- [x] case registry;
- [x] generic case runner;
- [x] suite runner;
- [x] suite-level summaries;
- [x] evaluation gates;
- [x] deterministic tests pass;
- [x] real Gemini suite passes;
- [x] release gate passes;
- [x] limitations documented.

## Next Phase

# Phase 11 — Error Analysis

The next objective is not to add more evaluation machinery immediately.

It is to study the weak points exposed by the evaluation system and decide which ones deserve engineering work.

Initial candidates:

- ambiguous causal language such as `driver` and `root cause`;
- overlapping contribution language across category, region, segment, and channel;
- provider dependency;
- tool-selection edge cases;
- prompt sensitivity;
- answer completeness;
- evidence granularity;
- free-form answer divergence from canonical grounded claims.

The loop becomes:

```text
PLAN
  |
BUILD
  |
TEST
  |
EVALUATE
  |
ERROR ANALYSIS
  |
DECIDE
  |
ITERATE
```
