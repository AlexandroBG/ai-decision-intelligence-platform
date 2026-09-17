# DecisionAI - Synthetic Data Strategy

## 1. Purpose

DecisionAI should use synthetic data as a controlled analytical
and evaluation environment rather than as arbitrary random test
data.

The synthetic dataset should support:

- Data-engineering development.
- Deterministic analytics development.
- Reproducible testing.
- Evaluation with known expected behavior.
- Error analysis.
- Regression testing.

## 2. Design Principle

Synthetic data should contain deliberate business patterns while
preserving enough natural variation to avoid creating a trivial
analytical problem.

The initial strategy is:

```text
controlled baseline
+
intentional business changes
+
bounded random variation
=
reproducible analytical scenario
```

## 3. Reproducibility

Synthetic-data generation should be deterministic when executed
with the same configuration and random seed.

A fixed random seed should be used so that repeated generation
produces reproducible datasets unless the scenario definition
changes intentionally.

Dates should also use fixed historical periods rather than
depending on the current date.

## 4. Initial Business Scenario

The initial synthetic scenario is named conceptually:

`revenue_decline_v1`

The scenario compares:

- Baseline period: July 2025.
- Comparison period: August 2025.

The expected high-level outcome is:

- August net revenue is lower than July net revenue.

## 5. Controlled Analytical Signals

The dataset should contain multiple controlled signals.

### 5.1 Primary Signal

The strongest expected contributor should be weaker revenue
performance associated with the South region.

The primary mechanism introduced by the synthetic generator
should be lower transaction or unit volume in that region during
the comparison period.

### 5.2 Secondary Signal

A secondary negative pattern should exist at the product-category
level.

The initial scenario should introduce weaker performance in a
selected category such as Hardware.

### 5.3 Additional Signal

A smaller effect may be introduced through higher average
discounting in the Partner sales channel during the comparison
period.

This provides a different mechanism through which net revenue
can change.

## 6. Controlled Noise

The dataset should also contain bounded random variation across:

- Customers.
- Products.
- Quantities.
- Order dates.
- Sales channels.
- Business segments.

The noise should make the analytical task realistic without
overwhelming the intentionally introduced signals.

The initial scenario should therefore favor a strong
signal-to-noise ratio.

## 7. Synthetic Business Dimensions

The initial business dimensions may include:

Customer segments:

- SMB.
- Mid-Market.
- Enterprise.

Regions:

- North.
- South.
- East.
- West.

Sales channels:

- Web.
- Direct.
- Partner.

Product categories should remain small and interpretable.

Potential initial categories include:

- Computing.
- Networking.
- Accessories.
- Office.

Exact products and prices will be defined during dataset
creation.

## 8. Dataset Scale

The initial synthetic dataset should be large enough to support
meaningful aggregation while remaining easy to inspect and test
locally.

A reasonable initial target is:

- Hundreds of customers.
- Tens of products.
- Approximately thousands of order records.

The exact size should be selected during implementation based on
clarity, reproducibility, and local-development performance.

## 9. Generation Order

Synthetic entities should be generated in dependency order:

```text
Products
   ↓
Customers
   ↓
Orders
```

Orders should reference only customer and product identifiers
that already exist.

This allows the canonical generated dataset to preserve
referential integrity by construction.

## 10. Product Pricing

Each product should have a stable base unit price for the initial
scenario.

Order-level price behavior should remain simple enough that
volume, product mix, and discount changes remain easy to
interpret.

`unit_cost` and `unit_price` should remain separate concepts:

- `unit_cost` represents product cost to the business.
- `unit_price` represents the customer price before discount.

## 11. Canonical Clean Dataset

The primary generated dataset should represent valid business
data.

The canonical dataset should not intentionally contain:

- Duplicate primary identifiers.
- Invalid foreign keys.
- Missing required columns.
- Impossible discounts.
- Invalid quantities.
- Malformed dates.

Data-quality failures should be tested using controlled corrupted
variants rather than contaminating the canonical analytical
dataset.

## 12. Corrupted Test Variants

Validation tests may create temporary modified copies of clean
data containing cases such as:

- Missing required columns.
- Duplicate identifiers.
- Unknown customer identifiers.
- Unknown product identifiers.
- Negative quantities.
- Discounts outside the accepted range.
- Invalid dates.
- Missing required values.

These variants should test validation behavior independently from
the analytical ground-truth scenario.

## 13. Ground Truth

The synthetic-data generator may know the mechanisms intentionally
introduced into the scenario.

Ground truth should remain separate from the normal analytical
input.

Potential ground-truth information may include:

- Scenario identifier.
- Baseline period.
- Comparison period.
- Expected overall revenue direction.
- Expected major contributors.
- Generator-level scenario assumptions.

Analytics code should infer results from the datasets and should
not receive ground-truth answers as input.

## 14. Contribution vs Causality

Knowledge of the synthetic generation mechanism does not justify
unrestricted causal language in normal DecisionAI analytical
output.

The system should initially communicate observed contribution or
association.

For example:

Preferred:

`The South region was the largest observed contributor to the
revenue decline.`

Avoid without causal analysis:

`The South region caused the revenue decline.`

This preserves the same analytical discipline expected when
working with real business data.

## 15. Data Leakage

Ground-truth labels or scenario explanations should not be
included as normal analytical features.

The production analytical workflow should not receive direct
fields that reveal expected answers.

Ground truth should only be available to generation,
verification, and evaluation workflows.

## 16. Scenario Versioning

Synthetic scenarios should be versionable.

The initial implementation should prioritize one well-understood
scenario before additional scenarios are introduced.

Future scenarios may test:

- Different revenue-decline mechanisms.
- Weaker signals.
- Higher noise.
- Different segment behavior.
- Different discount behavior.
- Different product-mix shifts.

## 17. Expected Initial Evaluation Behavior

For `revenue_decline_v1`, DecisionAI should eventually be able to:

- Detect that August net revenue is lower than July net revenue.
- Quantify the change deterministically.
- Identify major observed contributors.
- Surface the South-region weakness as an important investigation
  area.
- Detect meaningful category-level weakness.
- Recognize discount-related effects where supported by the
  evidence.
- Provide structured evidence.
- Avoid unsupported causal conclusions.

## 18. Synthetic-Data Principle

Synthetic data should serve as an engineering instrument.

The objective is not to imitate every aspect of a real business
dataset.

The objective is to create a reproducible, interpretable, and
controlled environment in which DecisionAI's data, analytics,
AI, and evaluation capabilities can be developed and measured.