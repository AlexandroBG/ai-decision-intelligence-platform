# Phase 11 — Error Analysis

## Status

**Closed with one external validation caveat:** the final post-fix live Gemini rerun was blocked by a provider rate/quota limit. This provider failure is tracked separately and is not counted as an AI quality failure.

Deterministic regression status at closure:

- Evaluation tests: **108 passed**
- Full project suite: **609 passed**
- Known warning: `google-genai` deprecation warning for `_UnionGenericAlias`
- No deterministic test failures at closure

## Objective

Phase 11 turns evaluation results into engineering decisions.

The goal is not only to answer:

> Did the system pass or fail?

The goal is to answer:

> What kind of failure occurred, how severe is it, how often does it happen, what should be investigated first, and what is the smallest justified change?

The working loop is:

```text
DETECT
→ CLASSIFY
→ COUNT
→ PRIORITIZE
→ REVIEW
→ DECIDE
→ CHANGE
→ REGRESSION TEST
→ RE-EVALUATE
```

A key principle in this phase is:

> Do not change agent behavior immediately after seeing a weak output. First determine whether the problem belongs to the agent, the evaluator, the tool layer, grounding, execution, or the provider.

## Source Principles Applied in This Phase

This phase applies the project source framework in four ways:

- **Evaluation-driven development:** use observed outputs to evolve both the AI system and the evaluator.
- **Human review where automation is weak:** qualitative review discovers blind spots before they are automated.
- **Verification before trust:** changes are checked with unit, integration, regression, full-suite, and real-provider validation when available.
- **Small targeted interventions:** change the smallest justified layer instead of changing prompts, architecture, models, and evals at once.

# 11.1 Error Taxonomy

Current error categories:

```text
execution
tool_selection
ground_truth
semantic
grounding
provider
```

Severity levels:

```text
low
medium
high
```

Each error records:

- category
- severity
- code
- message
- case ID
- run number

Example:

```text
category = semantic
severity = high
code = causal_overclaim
```

# 11.2 Error Reporting

The error report tracks:

- total runs analyzed
- runs with errors
- total errors
- high/medium/low severity counts
- errors by category
- errors by code
- top error code

This turns individual run inspection into basic failure analytics.

# 11.3 Error Prioritization

A simple triage heuristic was introduced:

```text
priority_score = occurrences × severity_weight
```

Weights:

```text
high   = 3
medium = 2
low    = 1
```

This is a prioritization heuristic, not mathematical truth.

# 11.4 Automated Error Analysis Report

The Phase 10 evaluation suite can be analyzed without an LLM call.

Artifact:

```text
artifacts/phase11/error_analysis.json
```

Initial result:

```text
Runs analyzed: 2
Runs with errors: 0
Total errors: 0
High severity: 0
Medium severity: 0
Low severity: 0
Top priority: None
```

Key lesson:

```text
0 machine-detected errors
≠
0 possible problems
```

That motivated qualitative review.

# 11.5 Qualitative Failure Review

A structured human-review checklist was introduced.

Statuses:

```text
pass
concern
unclear
```

Criteria:

```text
causal_language
evidence_alignment
scope_adherence
overlapping_contributions
recommendation_strength
unsupported_specificity
answer_completeness
```

A review passes only with zero concerns and zero unclear checks.

## First Qualitative Finding

A real answer that had passed Phase 10 used wording such as:

```text
largest driver
primary factors affecting
root causes
```

Human review classified:

```text
causal_language = UNCLEAR
```

while the other qualitative criteria passed.

This produced the first important Phase 11 finding:

```text
Automatic semantic evaluation: PASS
Human qualitative review: UNCLEAR
```

The issue was semantic ambiguity, not proven explicit causal overclaim.

# 11.6 Targeted Engineering Iteration

## 11.6.1 Causal Language Regression Guard

The semantic evaluator was extended to distinguish:

```text
causal_overclaim
```

from:

```text
causal_language_risk
```

Explicit causal language such as:

```text
Computing caused the decline.
```

remains high severity.

Ambiguous language such as:

```text
largest driver
primary driver
main driver
key driver
root cause
root causes
primary factor affecting
primary factors affecting
```

is tracked separately as medium severity.

Preferred observational wording includes:

```text
largest observed deterioration
largest observed contribution to the revenue change
highest-priority area to investigate
```

A previous real DecisionAI answer is now used as a regression case.

## 11.6.2 Agent Language Policy

A dedicated observational-language policy was added to the agent prompt pipeline.

Architecture:

```text
base agent prompt
+
observational language policy
↓
Gemini
```

The policy instructs the agent to:

- treat evidence as observational unless causal evidence exists
- avoid causal or causally ambiguous wording
- prefer observational descriptions
- avoid summing overlapping dimensions
- frame recommendations as investigation priorities rather than proven corrective actions

Components:

```text
app/agent/language_policy.py
app/agent/prompt_policy.py
app/agent/prompts.py
```

## Live Behavior After Language Mitigation

A real Gemini evaluation after the mitigation produced wording equivalent to:

```text
The analysis indicates that the Computing category showed
the largest observed deterioration...

This category should be investigated first to understand
the observed deterioration.
```

The run preserved:

```text
Agent completed: true
Tool success rate: 100%
Duplicate tool rate: 0%
Required tool coverage: 100%
Tool selection passed: true
Ground-truth score: 100%
Ground-truth passed: true
Causal overclaim: false
Unsupported certainty: false
Overlap summing risk: false
```

However, semantic safety initially failed because the evaluator did not recognize:

```text
should be investigated
```

as a recommendation.

This exposed a second evaluator blind spot.

## 11.6.3 Recommendation Detector Robustness

The recommendation detector was expanded to recognize natural variants such as:

```text
investigate
investigated
investigating
investigation
should be investigated
should investigate
review
reviewing
recommend
recommended
examine
```

The real post-mitigation answer was added as a deterministic semantic regression.

Final deterministic verification:

```text
tests/evaluation/test_semantic.py
26 passed

tests/evaluation/test_causal_language_regression.py
3 passed

tests/evaluation
108 passed

full project
609 passed
1 warning
```

# Provider Failure Separation

The final planned live Gemini re-evaluation could not execute because the provider returned a rate/quota limit.

The evaluation system classified it as:

```text
run_type = provider_error
type = rate_or_quota_limit
```

The run was not counted as an AI quality failure.

Result:

```text
Requested runs: 1
Attempted runs: 1
Quality-evaluated runs: 0
Provider errors: 1
```

Quality metrics correctly became unavailable instead of falsely reporting model failure.

Key boundary:

```text
provider availability
≠
AI quality
```

# Key Error-Analysis Lessons

1. **Passing evals do not prove the evaluator is complete.**
   Human review exposed a semantic blind spot.

2. **Human review can improve automated evaluation.**
   A qualitative finding became a permanent regression.

3. **A failing eval does not automatically mean the agent is wrong.**
   The evaluator itself can produce false positives.

4. **Change one layer at a time.**
   This preserves causal understanding of engineering changes.

5. **Provider failures require separate accounting.**
   Quota failure is not evidence of poor model quality.

# Architecture After Phase 11

```text
Execution Metrics
        ↓
Tool Selection
        ↓
Numeric Ground Truth
        ↓
Semantic Safety
        ↓
Qualitative Human Review
        ↓
Error Taxonomy
        ↓
Error Reporting
        ↓
Error Prioritization
        ↓
Targeted Regression Tests
```

# Known Limitations

- The real suite is still narrow.
- The semantic evaluator is rule/regex based and remains a smoke alarm, not semantic truth.
- Evidence IDs are still coarse at `tool_step_N` level.
- Final prose is not deterministically generated only from canonical grounded claims.
- Overlapping dimensions remain a semantic risk that heuristics cannot fully prove safe.
- The final post-fix live validation should be rerun when Gemini quota is available.

# Deferred Decisions

Intentionally deferred:

- LLM-as-a-judge
- multi-agent evaluation
- embedding-based semantic judges
- large benchmark suites
- automatic prompt optimization
- advanced statistical confidence intervals

These should be introduced only when simpler mechanisms stop being sufficient.

# Phase 11 Completion Criteria

Phase 11 is complete because DecisionAI now has:

- formal error taxonomy
- structured error reports
- frequency/severity prioritization
- machine-generated analysis artifacts
- human qualitative review
- documented evaluator false negative
- causal-language regression guard
- targeted agent language mitigation
- documented evaluator false positive
- improved recommendation detection
- full deterministic regression coverage
- provider failures separated from model-quality failures

Final deterministic verification:

```text
609 passed
1 non-blocking dependency warning
```

External caveat:

```text
Final post-fix Gemini quality rerun pending because the provider
returned a rate_or_quota_limit before producing a quality result.
```

# Final Phase 11 Decision

No further agent changes are justified by the currently available evidence.

The causal-language issue has been converted from:

```text
human intuition
```

into:

```text
structured qualitative finding
→ automated regression
→ targeted mitigation
→ deterministic verification
```

The project can now proceed to:

# Phase 12 — API + User Interface

Planned direction:

```text
FastAPI
+
Streamlit
+
existing DecisionAI runtime
```

The existing analytics, ML, grounding, tools, agent workflow, evaluation, and error-analysis layers should remain reusable behind the application boundary.
