# ML Engine

## 1. Purpose

The ML Engine adds a machine-learning-based anomaly detection layer to DecisionAI.

Its responsibility is to identify unusual business behavior in time-based revenue signals and expose that evidence in a structured form for downstream use.

The ML Engine does not replace deterministic analytics. Instead, it complements the Analytics Engine.

The separation is:

```text
Deterministic Analytics
→ What changed?

ML Engine
→ What looks unusual?

Future Grounding + LLM Layer
→ What does the evidence mean and what should be investigated next?
```

## 2. Current ML Problem

The current machine learning task is:

```text
Revenue anomaly detection
```

The system analyzes daily business behavior across:

```text
region
segment
category
sales_channel
```

The current implementation uses unsupervised anomaly detection.

## 3. Why ML Is Used Here

The deterministic Analytics Engine already provides:

```text
period comparison
revenue change
dimension aggregation
contribution analysis
observed driver ranking
```

ML is used for a different capability:

> Detect unusual behavior that may deserve investigation.

## 4. ML Development Principle

The ML Engine follows:

```text
DEFINE
↓
BUILD
↓
TEST
↓
EVALUATE
↓
ERROR ANALYSIS
↓
DECIDE
↓
ITERATE
```

The current architecture was revised several times based on observed model behavior.

## 5. Current Model

The current model is:

```text
Isolation Forest
```

It is used for unsupervised anomaly detection and produces:

```text
anomaly_score
is_anomaly
```

for each scored observation.

## 6. Statistical Baseline

Before Isolation Forest, the project implemented a simple statistical baseline using:

```text
rolling mean
rolling standard deviation
z-score
```

The current observation is excluded from its own historical expectation using a shift before rolling calculations.

## 7. Baseline Formula

```text
z_score =
(current_value - expected_value)
/
historical_standard_deviation
```

An observation may be marked anomalous when:

```text
abs(z_score) >= threshold
```

## 8. Feature Dataset

The core ML unit of analysis is:

```text
date × dimension × value
```

Examples:

```text
2025-07-01 | region        | South
2025-07-01 | category      | Computing
2025-07-01 | sales_channel | Partner
2025-07-01 | segment       | SMB
```

## 9. Current Feature Set

The model currently uses:

```text
daily_revenue
order_count
units_sold
average_order_value
average_discount
```

These are defined in:

```text
app/ml/features.py
```

## 10. Feature Definitions

### `daily_revenue`

```text
sum(net_revenue)
```

### `order_count`

```text
nunique(order_id)
```

### `units_sold`

```text
sum(quantity)
```

### `average_order_value`

```text
daily_revenue / order_count
```

### `average_discount`

```text
mean(discount)
```

## 11. Why Multiple Features Were Added

The initial model used only:

```text
daily_revenue
```

Evaluation showed that the synthetic scenario contains different mechanisms:

```text
South
→ volume weakness

Computing
→ category weakness

Partner
→ higher discounts
```

The feature set was expanded to capture:

```text
volume
revenue
order economics
discount pressure
```

## 12. Initial Global Model

The first Isolation Forest implementation used one global model across all dimensions and values.

Evaluation showed that this mixed business series with very different natural scales.

The result was noisy anomaly detection.

## 13. Error Analysis Result

The global model frequently ranked low-scale series such as `Accessories` as anomalous.

This suggested that the model was partially learning:

```text
small absolute values are unusual
```

instead of:

```text
this observation is unusual relative to its own historical behavior
```

## 14. Current Per-Series Architecture

The current ML Engine trains one model per:

```text
(dimension, value)
```

Examples:

```text
("region", "South")
("region", "North")
("category", "Computing")
("sales_channel", "Partner")
```

Each model learns the historical behavior of its own series.

## 15. Current Model Count

For the current synthetic dataset and supported dimensions, the training pipeline creates:

```text
14 Isolation Forest models
```

## 16. Training Pipeline

File:

```text
app/ml/training.py
```

Main function:

```text
train_revenue_anomaly_model(...)
```

The flow is:

```text
enriched historical data
↓
daily feature generation
↓
group by dimension + value
↓
train one Isolation Forest per series
↓
TrainedAnomalyModel
```

## 17. Trained Model Contract

`TrainedAnomalyModel` contains:

```text
models
features
dimensions
contamination
random_state
```

`models` maps:

```text
(dimension, value)
```

to an Isolation Forest instance.

## 18. Reproducibility

The current configuration uses:

```text
random_state = 42
```

The artifact also stores the contamination setting used during training.

## 19. Current Contamination Setting

The selected project setting is:

```text
contamination = 0.08
```

This was selected after a sensitivity analysis rather than chosen arbitrarily.

## 20. Contamination Sensitivity Analysis

Observed results:

```text
contamination = 0.03
total anomalies = 40
South = 11
Computing = 2
Partner = 0

contamination = 0.05
total anomalies = 52
South = 11
Computing = 3
Partner = 2

contamination = 0.08
total anomalies = 79
South = 11
Computing = 3
Partner = 9

contamination = 0.10
total anomalies = 95
South = 14
Computing = 5
Partner = 9
```

The project selected `0.08` as the current compromise between signal recovery and noise.

## 21. Training / Inference Time Split

Synthetic scenario evaluation uses:

```text
July 2025
→ training

August 2025
→ inference
```

This prevents the deteriorated August period from being used as historical training input.

## 22. Inference Pipeline

File:

```text
app/ml/inference.py
```

Main function:

```text
score_revenue_anomalies(...)
```

The flow is:

```text
new data
↓
same feature-generation logic
↓
group by dimension + value
↓
match trained model
↓
score observation
↓
AnomalyEvidence
↓
MLResult
```

## 23. Anomaly Score Semantics

DecisionAI uses:

```text
anomaly_score =
-decision_function(...)
```

so that:

```text
higher anomaly_score
→ more unusual
```

## 24. ML Result Contracts

File:

```text
app/ml/contracts.py
```

### `AnomalyEvidence`

Contains:

```text
date
dimension
value
daily_revenue
anomaly_score
is_anomaly
```

### `MLResult`

Contains:

```text
anomalies: list[AnomalyEvidence]
```

## 25. Why Contracts Matter

Internal computation uses pandas.

Downstream interfaces use dataclasses.

This keeps the ML layer stable even if internal implementation details change.

## 26. Model Evaluation

File:

```text
app/ml/evaluation.py
```

Current metrics include:

```text
total_observations
anomaly_count
anomaly_rate
mean_anomaly_score
max_anomaly_score
```

These describe model behavior but are not classification accuracy.

## 27. Why Accuracy Is Not Used

The current dataset does not contain observation-level ground-truth labels such as:

```text
is_true_anomaly
```

Therefore the project does not claim:

```text
accuracy
precision
recall
F1
```

for the anomaly detector.

## 28. Baseline vs ML Comparison

File:

```text
app/ml/comparison.py
```

The comparison reports:

```text
total_observations
baseline_anomaly_count
ml_anomaly_count
agreement_count
disagreement_count
agreement_rate
```

Alignment uses:

```text
date
dimension
value
```

## 29. Agreement Is Not Accuracy

`agreement_rate` measures how often the statistical baseline and Isolation Forest make the same decision.

It does not measure whether either detector is correct.

## 30. Synthetic Scenario Verification

The ML Engine is evaluated against:

```text
revenue_decline_v1
```

Expected scenario-level signals include:

```text
South-region weakness
Computing category weakness
Partner discount pressure
```

These expectations are used only for evaluation.

## 31. Current Scenario Findings

At:

```text
contamination = 0.08
```

the model produced approximately:

```text
South       → 11 anomalies
Computing   → 3 anomalies
Partner     → 9 anomalies
```

This indicates that the current feature set can recover meaningful parts of the designed scenario.

## 32. Evaluation Limitation

The scenario was designed primarily for revenue deterioration, not as a perfectly labeled daily anomaly benchmark.

Therefore the project distinguishes:

```text
scenario-level expected behavior
```

from:

```text
observation-level anomaly ground truth
```

## 33. Model Persistence

File:

```text
app/ml/persistence.py
```

The engine supports:

```text
save_trained_model(...)
load_trained_model(...)
```

using `joblib`.

## 34. Persistence Metadata

The persisted artifact includes:

```text
trained per-series models
training features
dimensions
contamination
random_state
```

## 35. Artifact Validation

Loaded artifacts are validated to ensure they are instances of:

```text
TrainedAnomalyModel
```

## 36. ML Error Handling

File:

```text
app/ml/errors.py
```

Hierarchy:

```text
MLError
├── MLInputError
├── MLTrainingError
├── MLInferenceError
└── MLModelArtifactError
```

## 37. `MLInputError`

Used for invalid data or configuration.

Examples:

```text
empty input
missing features
invalid contamination
missing dimensions
```

## 38. `MLTrainingError`

Used when a usable model cannot be created.

## 39. `MLInferenceError`

Used when inference cannot produce evidence.

## 40. `MLModelArtifactError`

Used for missing or invalid persisted model artifacts.

## 41. Testing Strategy

Tests are stored under:

```text
tests/ml/
```

Coverage includes:

```text
statistical baseline
feature engineering
Isolation Forest
training
inference
contracts
evaluation
baseline comparison
scenario verification
persistence
error handling
integration
```

## 42. Integration Test

The integration flow is:

```text
CSV datasets
↓
loaders
↓
net revenue
↓
customer enrichment
↓
product enrichment
↓
July filtering
↓
feature generation
↓
per-series training
↓
model persistence
↓
model reload
↓
August inference
↓
MLResult
```

## 43. Relationship to Analytics

### Analytics Engine

Answers:

```text
What changed?
Which business slices deteriorated most?
```

### ML Engine

Answers:

```text
Which observations look unusual relative to historical behavior?
```

These responsibilities remain separate.

## 44. Future Grounding Architecture

```text
Trusted Data
     ↓
Analytics Engine
     ↓
AnalyticsResult

Trusted Data
     ↓
ML Engine
     ↓
MLResult

AnalyticsResult
     +
MLResult
     ↓
Grounding Layer
     ↓
Gemini
```

## 45. Current Limitations

The current ML Engine intentionally does not implement:

```text
supervised anomaly classification
forecasting
deep learning
AutoML
causal inference
feature attribution
automatic root-cause analysis
online learning
streaming inference
model registry infrastructure
```

## 46. Per-Series Model Limitation

One model per series improves comparability but increases the number of model objects.

This is manageable for the current project scale.

## 47. Feature Scaling

The current implementation uses raw numerical features.

Scaling may be evaluated later if evidence shows it improves stability or interpretability.

## 48. Feature Attribution Limitation

The current contract identifies which observation is unusual, but not which feature caused the anomaly score.

Future versions may add feature-level diagnostics.

## 49. Contamination Limitation

The current:

```text
contamination = 0.08
```

is specific to the current synthetic scenario and should be reevaluated on materially different datasets.

## 50. Production Considerations

Future production work may include:

```text
model versioning
artifact metadata
dependency compatibility
model registry
training provenance
scheduled retraining
drift monitoring
observability
rollback strategy
```

## 51. Current Phase Status

```text
ML Problem Definition                    ✅
Time-series Feature Dataset              ✅
Statistical Anomaly Baseline             ✅
Baseline Tests                           ✅
Isolation Forest Model                   ✅
Training Pipeline                        ✅
Inference Pipeline                       ✅
ML Result Contracts                      ✅
Model Evaluation                         ✅
Baseline vs ML Comparison                ✅
Synthetic Scenario Verification          ✅
Error Analysis and Iteration             ✅
Feature Engineering                      ✅
Hyperparameter Sensitivity Analysis      ✅
Model Persistence                        ✅
ML Error Handling                        ✅
Unit Tests                               ✅
Integration Test                         ✅
Documentation                            ✅
```

Remaining Phase 5 work:

```text
Git verification
Phase closure
```

## 52. Architectural Outcome

DecisionAI now has an ML layer capable of:

```text
building daily business features
training per-series anomaly models
scoring new periods
producing structured anomaly evidence
comparing against a statistical baseline
persisting and loading models
handling ML-specific errors
verifying behavior with tests
```

## 53. Final ML Flow

```text
Trusted Transaction Data
        ↓
Revenue + Dimension Enrichment
        ↓
Daily Feature Engineering
        ↓
Per-Series Isolation Forest Training
        ↓
TrainedAnomalyModel
        ↓
Persistence
        ↓
Reload
        ↓
New Period Feature Engineering
        ↓
Per-Series Inference
        ↓
AnomalyEvidence
        ↓
MLResult
```

## 54. Next Phase

After Git verification and formal closure of Phase 5, the roadmap continues with:

```text
Phase 6 — Gemini Foundation / LLM Foundations
```

The architectural rule remains:

```text
Python and ML produce evidence.
Gemini interprets and communicates evidence.
```
