# Analytics Engine

## 1. Purpose

The Analytics Engine provides deterministic, evidence-based analysis of business performance.

Its main responsibility is to transform trusted business data into structured analytical evidence that can later be consumed by higher-level application layers, including grounding and LLM-based interpretation.

The engine does not delegate numerical calculations to an LLM.

Python performs the calculations.

The Analytics Engine structures the resulting evidence.

Future LLM layers will interpret and communicate that evidence.

---

## 2. Current Analytical Question

The current MVP is designed around the business question:

> What is affecting revenue performance, and what should I investigate first?

The engine currently focuses on revenue comparison between two periods and identifies observed areas of deterioration across selected business dimensions.

The current implementation is descriptive and diagnostic in nature.

It does not claim causal relationships.

---

## 3. Design Principles

The Analytics Engine follows these principles:

- Revenue calculations are deterministic.
- Business metrics are computed in Python.
- LLMs are not used as calculators.
- Analytics outputs must be reproducible.
- Results should be structured before they are passed to AI layers.
- Observed contribution does not imply causation.
- Driver ranking prioritizes areas for investigation rather than declaring root causes.
- DataFrame operations are internal implementation details.
- Dataclasses define stable result contracts for downstream layers.
- Simplicity is preferred over unnecessary analytical complexity.

---

## 4. Revenue Definition

Revenue is derived from the trusted order data.

Gross revenue is:

```text
gross_revenue = quantity * unit_price
```

Net revenue is:

```text
net_revenue = quantity * unit_price * (1 - discount)
```

The Analytics Engine uses net revenue as the authoritative revenue KPI.

Revenue is derived during analysis and is not stored as an authoritative field in the raw orders dataset.

---

## 5. Current Analytics Pipeline

The current analytics flow is:

```text
Trusted orders
    +
Trusted customers
    +
Trusted products
        ↓
Net revenue calculation
        ↓
Customer dimension enrichment
        ↓
Product dimension enrichment
        ↓
Period filtering
        ↓
Overall revenue comparison
        ↓
Dimension-level revenue comparison
        ↓
Contribution analysis
        ↓
Driver candidate construction
        ↓
Observed driver ranking
        ↓
AnalyticsResult
```

---

## 6. Analytics Modules

The current implementation is organized under:

```text
app/analytics/
```

The main modules are:

```text
contracts.py
dimensions.py
drivers.py
engine.py
errors.py
revenue.py
```

Each module has a focused responsibility.

---

## 7. Revenue Module

File:

```text
app/analytics/revenue.py
```

Responsibilities:

- calculate net revenue
- calculate total revenue
- compare revenue between periods
- filter data by date range

### `add_net_revenue`

Adds the derived `net_revenue` field:

```text
quantity * unit_price * (1 - discount)
```

The function returns a copy and does not mutate the original DataFrame.

### `calculate_total_revenue`

Returns the sum of `net_revenue` as a Python float.

### `compare_revenue_periods`

Compares baseline and comparison periods.

It returns a `RevenueComparison` contract containing:

```text
baseline_revenue
comparison_revenue
absolute_change
percentage_change
```

Where:

```text
absolute_change =
comparison_revenue - baseline_revenue
```

and:

```text
percentage_change =
absolute_change / baseline_revenue
```

When baseline revenue is zero, the current implementation returns:

```text
percentage_change = 0.0
```

This behavior is an explicit current design choice and may be revisited if the product later requires a different semantic representation for undefined growth.

### `filter_period`

Filters rows using inclusive start and end dates.

---

## 8. Dimension Enrichment

File:

```text
app/analytics/dimensions.py
```

The engine currently analyzes:

```text
region
segment
category
sales_channel
```

### Customer Dimensions

Customer data enriches orders with:

```text
segment
region
```

using:

```text
customer_id
```

The merge is validated as:

```text
many_to_one
```

### Product Dimensions

Product data enriches orders with:

```text
category
```

using:

```text
product_id
```

The merge is also validated as:

```text
many_to_one
```

The `sales_channel` dimension already exists directly in orders.

---

## 9. Revenue Aggregation by Dimension

The engine can aggregate net revenue by any supported dimension.

Conceptually:

```text
dimension value
        ↓
sum(net_revenue)
```

For example:

```text
South       → revenue
North       → revenue
East        → revenue
West        → revenue
```

The same generic mechanism is used for:

```text
region
segment
category
sales_channel
```

This avoids duplicating analytical logic for each business dimension.

---

## 10. Dimension Comparison

For every value in a dimension, the engine calculates:

```text
baseline_revenue
comparison_revenue
absolute_change
percentage_change
```

For example:

```text
region = South
baseline_revenue
comparison_revenue
absolute_change
percentage_change
```

This enables the engine to identify which business slices changed most strongly between the two periods.

---

## 11. Contribution Analysis

The engine calculates:

```text
contribution_to_total_change
```

using:

```text
absolute_change / total_revenue_change
```

Example:

```text
Total revenue change = -500,000
South revenue change = -300,000

Contribution to total change = 0.60
```

This means that the observed South-region change is equivalent to approximately 60% of the total revenue decline.

This is a descriptive contribution metric.

It is not a causal claim.

---

## 12. Contribution Interpretation

Contribution values must be interpreted within their analytical context.

Different dimensions overlap.

An individual order can simultaneously belong to:

```text
South
Computing
Partner
SMB
```

Therefore, contributions from different dimensions must not be added together.

For example:

```text
South contribution
+
Computing contribution
+
Partner contribution
```

does not represent a valid decomposition of total revenue change.

These values describe different views of the same underlying transactions.

---

## 13. Driver Candidates

File:

```text
app/analytics/drivers.py
```

Dimension-level comparisons are normalized into a common structure.

Each driver candidate contains:

```text
dimension
value
baseline_revenue
comparison_revenue
absolute_change
percentage_change
contribution_to_total_change
```

Examples:

```text
dimension = region
value = South
```

```text
dimension = category
value = Computing
```

```text
dimension = sales_channel
value = Partner
```

This allows candidates from different business dimensions to be processed through the same ranking pipeline.

---

## 14. Observed Driver Ranking

The current ranking strategy is intentionally simple.

The engine:

1. combines driver candidates
2. keeps only negative revenue changes
3. sorts by `absolute_change`
4. places the largest observed deterioration first

Conceptually:

```text
largest negative absolute change
        ↓
highest investigation priority
```

The ranking therefore answers:

> Which observed business slices should be investigated first?

It does not answer:

> What caused the revenue decline?

The current ranking is a prioritization mechanism, not a causal inference system.

---

## 15. Result Contracts

File:

```text
app/analytics/contracts.py
```

The Analytics Engine uses dataclasses as stable result contracts.

### `RevenueComparison`

```text
baseline_revenue
comparison_revenue
absolute_change
percentage_change
```

### `DriverEvidence`

```text
dimension
value
baseline_revenue
comparison_revenue
absolute_change
percentage_change
contribution_to_total_change
```

### `AnalyticsResult`

The top-level engine result contains:

```text
revenue_comparison
drivers
```

Conceptually:

```text
AnalyticsResult
├── RevenueComparison
└── list[DriverEvidence]
```

These contracts separate the internal pandas implementation from the interface exposed to downstream layers.

---

## 16. Analytics Engine Orchestration

File:

```text
app/analytics/engine.py
```

The main orchestration function is:

```text
analyze_revenue_change(...)
```

Inputs:

```text
orders
customers
products
baseline_start
baseline_end
comparison_start
comparison_end
```

Output:

```text
AnalyticsResult
```

The engine performs:

```text
1. input validation
2. net revenue calculation
3. customer enrichment
4. product enrichment
5. period filtering
6. period validation
7. overall revenue comparison
8. dimension comparison
9. contribution calculation
10. candidate construction
11. observed driver ranking
12. structured result creation
```

This function acts as the current internal API of the Analytics Engine.

---

## 17. Analytics Error Handling

File:

```text
app/analytics/errors.py
```

The current error hierarchy includes:

```text
AnalyticsError
EmptyAnalyticsInputError
EmptyPeriodError
```

### `AnalyticsError`

Base exception for analytics-specific errors.

### `EmptyAnalyticsInputError`

Raised when the Analytics Engine receives an empty orders dataset.

### `EmptyPeriodError`

Raised when either the baseline or comparison period contains no orders.

The goal is to expose domain-specific errors rather than leaking low-level pandas failures to future API or UI layers.

---

## 18. Synthetic Scenario

The current analytics implementation is verified against the synthetic scenario:

```text
revenue_decline_v1
```

The scenario contains:

```text
Baseline period:
July 2025

Comparison period:
August 2025
```

Expected overall behavior:

```text
August net revenue < July net revenue
```

The scenario was intentionally designed with several analytical signals.

---

## 19. Synthetic Ground Truth

The main expected signals are:

### Primary Signal

```text
South-region volume weakness
```

### Secondary Signal

```text
Computing category weakness
```

### Additional Signal

```text
Higher Partner-channel discounts
```

The Analytics Engine does not receive these answers directly.

They exist as scenario design ground truth and are used only to evaluate whether the engine discovers the intended patterns from the generated data.

This avoids ground-truth leakage into the analytical implementation.

---

## 20. Observed Overall Revenue Result

For the current generated dataset:

```text
July net revenue:
approximately 1,773,419.93

August net revenue:
approximately 1,275,769.95
```

Observed absolute change:

```text
approximately -497,649.98
```

Observed percentage change:

```text
approximately -28.06%
```

Therefore, the Analytics Engine correctly identifies an overall revenue deterioration between the baseline and comparison periods.

---

## 21. Observed Regional Signal

The strongest observed regional deterioration is:

```text
South
```

Approximate values:

```text
July:
491,147.18

August:
190,155.74

Absolute change:
-300,991.44

Percentage change:
-61.28%
```

South accounts for approximately 60.5% of the total observed revenue decline when viewed through the region dimension.

This matches the intended primary synthetic signal.

---

## 22. Observed Category Signal

The strongest category deterioration is:

```text
Computing
```

Approximate values:

```text
Baseline revenue:
1,060,508

Comparison revenue:
608,595

Absolute change:
-451,913

Percentage change:
-42.61%
```

This matches the intended category weakness in the synthetic scenario.

---

## 23. Observed Sales Channel Signal

The Partner channel shows a meaningful negative revenue change.

Approximate values:

```text
Baseline revenue:
601,166.49

Comparison revenue:
419,909.96

Absolute change:
-181,256.53

Percentage change:
-30.15%
```

The synthetic data generation process also introduced higher Partner discounts during August.

However, the current Analytics Engine does not infer that the discount change caused the revenue decline.

The current evidence only establishes an observed negative Partner-channel signal.

---

## 24. Segment Results

The segment dimension also shows deterioration across the generated scenario.

Observed results include negative revenue changes for:

```text
SMB
Enterprise
Mid-Market
```

These are valid descriptive signals even though segment was not designed as the primary synthetic driver.

This illustrates why the engine should expose evidence rather than return a hardcoded scenario answer.

---

## 25. Ground-Truth Verification

The analytics test suite explicitly verifies that:

```text
comparison revenue < baseline revenue
```

and that:

```text
South
```

is the strongest regional deterioration.

It also verifies that:

```text
Computing
```

is the strongest category deterioration.

The Partner channel is verified as a negative observed signal.

This creates a reproducible link between:

```text
scenario design
↓
generated data
↓
deterministic analytics
↓
expected evidence
```

---

## 26. Testing Strategy

Analytics tests are stored under:

```text
tests/analytics/
```

The test suite covers:

```text
revenue calculations
period filtering
dimension enrichment
dimension aggregation
dimension comparison
contribution calculations
driver candidate construction
driver ranking
result contracts
engine orchestration
error handling
real dataset integration
synthetic ground-truth verification
```

The project uses both small deterministic unit-test fixtures and the generated canonical dataset.

---

## 27. Unit Tests

Unit tests use small DataFrames with known expected outputs.

Examples include:

```text
net revenue calculation
total revenue calculation
period comparison
zero baseline handling
customer enrichment
product enrichment
dimension aggregation
contribution calculation
driver ordering
positive-change exclusion
```

These tests isolate specific analytical behaviors.

---

## 28. Integration Tests

Integration tests use the real generated files loaded through the Data Foundation.

The flow tested is:

```text
data/*.csv
↓
loaders
↓
Analytics Engine
↓
AnalyticsResult
```

The integration tests verify that:

```text
baseline revenue is positive
comparison revenue is positive
comparison revenue is lower
absolute change is negative
percentage change is negative
drivers are produced
all expected dimensions are represented
```

---

## 29. Separation of Responsibilities

The current architecture deliberately separates concerns.

### Data Foundation

Responsible for:

```text
loading
schema validation
business-rule validation
referential integrity
normalization
profiling
trusted-data boundary
```

### Analytics Engine

Responsible for:

```text
metric calculation
period comparison
dimension analysis
contribution analysis
observed driver prioritization
structured analytical evidence
```

### Future AI Layer

Will be responsible for:

```text
interpreting evidence
explaining findings
planning further investigation
communicating results
```

The AI layer should not replace deterministic analytics.

---

## 30. Grounding Boundary

`AnalyticsResult` is the intended boundary between deterministic analytics and future grounding / LLM layers.

Conceptually:

```text
Trusted Data
    ↓
Analytics Engine
    ↓
AnalyticsResult
    ↓
Grounding Layer
    ↓
Gemini
```

This architecture helps keep future AI responses tied to calculated evidence.

---

## 31. Current Limitations

The current Analytics Engine intentionally does not implement:

```text
causal inference
forecasting
advanced anomaly detection
statistical significance testing
multi-dimensional interaction decomposition
Shapley attribution
machine-learning-based ranking
automated root-cause claims
```

These features are outside the current deterministic analytics scope.

They should only be introduced when the product need and evaluation evidence justify the added complexity.

---

## 32. Causality Limitation

The Analytics Engine currently measures:

```text
change
association
descriptive contribution
```

It does not establish causality.

Statements such as:

```text
South caused the revenue decline
```

or:

```text
Partner discounts caused the decline
```

are not supported by the current methodology.

Correct language includes:

```text
South shows the largest regional deterioration.
```

```text
Computing shows the largest category deterioration.
```

```text
Partner is a negative sales-channel signal worth investigating.
```

Future causal claims would require an explicit causal methodology.

---

## 33. Driver Ranking Limitation

The current driver ranking orders candidates by negative absolute revenue change.

This strategy is transparent and easy to verify, but it is intentionally simple.

Future versions may evaluate alternative ranking factors such as:

```text
absolute impact
relative impact
business materiality
statistical confidence
persistence
cross-period consistency
supporting evidence
```

Any ranking changes should be evaluation-driven.

---

## 34. Current Phase Status

The Analytics Engine currently supports:

```text
Revenue metric implementation              ✅
Period comparison                          ✅
Dimension aggregation                      ✅
Revenue contribution analysis              ✅
Observed driver ranking                    ✅
Result contracts                           ✅
Analytics error handling                   ✅
Unit tests                                 ✅
Integration testing                        ✅
Synthetic ground-truth verification        ✅
Documentation                              ✅
```

Remaining Phase 4 work:

```text
Git verification
Phase closure
```

---

## 35. Architectural Outcome

At the end of the current Analytics Engine implementation, DecisionAI has a deterministic analytical layer capable of transforming trusted transactional data into structured business evidence.

The architecture is now:

```text
Raw Data
    ↓
Data Foundation
    ↓
Trusted Data
    ↓
Analytics Engine
    ↓
AnalyticsResult
    ↓
Future Grounding Layer
    ↓
Future Gemini Layer
```

This creates a strong boundary between numerical computation and AI interpretation.

---

## 36. Next Phase

After Phase 4 is formally closed, the roadmap continues with:

```text
Phase 5 — ML Engine / ML Foundations
```

The purpose of that phase will be to introduce machine learning only where it adds measurable value beyond deterministic analytics.

The current deterministic Analytics Engine remains the baseline against which more advanced analytical approaches should be evaluated.
