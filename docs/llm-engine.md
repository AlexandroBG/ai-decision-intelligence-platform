# DecisionAI — LLM Engine

## 1. Purpose

The LLM Engine is the evidence interpretation layer of DecisionAI.

Its responsibility is to transform structured outputs from deterministic analytics and machine learning into concise, evidence-backed business interpretations.

The LLM is not the source of business truth.

DecisionAI follows this principle:

> Deterministic systems calculate. The LLM interprets.

The LLM Engine therefore does not replace the Analytics Engine or the ML Engine. It consumes their outputs and communicates what the evidence supports, what it may suggest, and what remains unknown.

## 2. Role of Gemini

Gemini is used for interpreting structured analytical evidence, synthesizing analytics and ML outputs, communicating findings in business-friendly language, separating facts from interpretation, identifying investigation priorities, explaining uncertainty, and producing structured responses.

Gemini is not used for calculating authoritative business metrics, recomputing revenue, inventing dimensions, drivers, anomalies, or events, inferring missing data, claiming causality without explicit causal evidence, or overriding deterministic analytical outputs.

## 3. Architectural Principle

```text
Business Data
    ↓
Data Foundation
    ↓
Analytics Engine
    ↓
ML Engine
    ↓
Evidence Context
    ↓
Prompt Contract
    ↓
Gemini
    ↓
Structured LLM Interpretation
```

The Analytics Engine and ML Engine remain the authoritative producers of numerical evidence.

The LLM receives only structured, bounded evidence.

## 4. Model Configuration

The current DecisionAI configuration uses:

```text
gemini-2.5-flash
```

The model is configurable through environment variables:

```text
GEMINI_API_KEY
GEMINI_MODEL
```

The default model is configured in:

```text
app/llm/config.py
```

Example configuration contract:

```python
@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    model_name: str
```

The API key is never stored in source code.

## 5. LLM Module Structure

```text
app/llm/
├── client.py
├── config.py
├── contracts.py
├── errors.py
├── evidence.py
├── interpreter.py
└── prompts.py
```

`config.py` loads environment-based configuration.

`client.py` encapsulates Gemini SDK interactions and exposes `generate_text(...)` and `generate_interpretation(...)`.

`contracts.py` defines Pydantic models for evidence and structured LLM responses.

`errors.py` defines DecisionAI-specific LLM exceptions.

`evidence.py` transforms Analytics Engine and ML Engine outputs into bounded evidence.

`prompts.py` defines grounding rules and constructs the final prompt.

`interpreter.py` coordinates the complete interpretation flow.

## 6. Structured Output Contract

```python
class LLMInterpretation(BaseModel):
    summary: str
    facts: list[str]
    inferences: list[str]
    unknowns: list[str]
    recommended_investigations: list[str]
```

Facts are statements directly supported by supplied evidence.

Inferences are reasonable interpretations that are not directly proven.

Unknowns are claims that cannot be established from the supplied evidence.

Recommended investigations are areas worth examining based on observed evidence.

This contract improves predictability, testability, and downstream integration.

## 7. Output Validation

The response schema rejects empty or whitespace-only summaries, strips unnecessary whitespace, removes empty list items, and removes duplicate list items.

Example:

```text
["Revenue fell.", "", "Revenue fell."]
```

becomes:

```text
["Revenue fell."]
```

## 8. Evidence Input Contract

The LLM does not receive raw DataFrames.

```text
EvidenceContext
├── question
├── revenue
├── analytics_drivers
└── ml_anomalies
```

Revenue evidence contains:

```text
baseline_revenue
comparison_revenue
absolute_change
percentage_change
```

Analytics driver evidence contains:

```text
dimension
value
absolute_change
percentage_change
contribution_to_total_change
```

ML anomaly evidence contains:

```text
date
dimension
value
daily_revenue
anomaly_score
```

## 9. Analytics Evidence Selection

Analytics drivers are already ranked by the deterministic Analytics Engine. The LLM layer does not rerank them; it only limits how many are sent to the model.

Current default:

```text
DEFAULT_MAX_ANALYTICS_DRIVERS = 5
```

Flow:

```text
AnalyticsResult.drivers
    ↓
existing deterministic ranking
    ↓
top N
    ↓
EvidenceContext
```

## 10. ML Evidence Selection

The LLM layer explicitly filters and ranks anomaly evidence:

```text
MLResult.anomalies
    ↓
keep is_anomaly == True
    ↓
sort by anomaly_score descending
    ↓
top N
    ↓
EvidenceContext
```

Current default:

```text
DEFAULT_MAX_ML_ANOMALIES = 10
```

These limits are current project defaults, not universal optimal values.

## 11. Prompt Contract

Core rules include:

1. Treat supplied analytics and ML outputs as the source of truth.
2. Do not recalculate business metrics.
3. Do not invent numbers, dimensions, drivers, anomalies, or events.
4. Do not claim causality unless causal evidence is explicitly supplied.
5. Distinguish observed facts from interpretation.
6. Explicitly state when evidence is insufficient.
7. Prefer investigation-oriented language over causal language.
8. Never override deterministic analytical results.
9. Do not infer missing data.
10. Keep explanations concise and evidence-backed.

## 12. Certainty Levels

### FACT

Directly supported by supplied evidence.

### INFERENCE

A reasonable interpretation of supplied evidence that is not directly proven.

### UNKNOWN

Not supported by the available evidence.

## 13. Contribution Semantics

Analytics drivers may belong to overlapping dimensions. The same order can simultaneously belong to a category, region, segment, and sales channel.

Therefore contribution values across different dimensions must not be summed.

```text
Computing contribution
+
South contribution
+
SMB contribution
```

is not a valid additive decomposition of total revenue decline.

The prompt explicitly states:

```text
Contribution values from different dimensions MUST NOT be summed together.
```

Contribution values represent observed analytical slices relative to total period-over-period change. They do not establish causal attribution.

## 14. ML Anomaly Semantics

The anomaly detector identifies unusual observations relative to learned historical behavior.

An anomaly does not mean causal impact, probability of failure, confidence, business importance, or magnitude of causal contribution.

The prompt explicitly states that `anomaly_score` must not be interpreted as probability, confidence, impact, or causal strength.

## 15. Hallucination Boundaries

The model must not invent:

```text
metrics
numbers
dimensions
drivers
anomalies
events
causes
missing data
```

Unsupported causal wording such as:

```text
caused
is responsible for
led to
```

should be avoided unless causal evidence is explicitly supplied.

Preferred wording includes:

```text
is associated with
shows deterioration
appears unusual
is worth investigating
may be contributing
```

## 16. Real Evidence-Aware Evaluation

DecisionAI was tested end-to-end using the synthetic `revenue_decline_v1` scenario.

The model received real deterministic analytics and ML evidence and correctly recognized the overall revenue decline while surfacing evidence involving areas such as:

```text
Computing
South
SMB
Partner
Direct
```

The first real evaluation exposed an important semantic issue: individual contribution values were correct, but overlapping dimensions required an explicit instruction preventing additive interpretation.

After the prompt contract was strengthened, a second evaluation explicitly stated that contributions across dimensions are not independent additive components, contribution values do not establish causality, anomalies do not prove business outcomes, and root causes remain unknown without additional evidence.

This follows the project loop:

```text
BUILD
→ TEST
→ EVALUATE
→ ERROR ANALYSIS
→ IMPROVE
```

## 17. Failure Handling

The LLM error hierarchy is:

```text
LLMError
├── LLMInputError
├── LLMProviderError
└── LLMResponseError
```

`LLMInputError` handles invalid application input such as empty prompts.

`LLMProviderError` wraps Gemini or network/provider failures.

`LLMResponseError` handles unusable provider responses such as empty text or invalid structured output.

Example boundary:

```text
Gemini / network error
    ↓
Gemini SDK
    ↓
GeminiClient
    ↓
LLMProviderError
    ↓
DecisionAI application layer
```

## 18. Provider Isolation

Application code depends on `GeminiClient` rather than directly on Gemini SDK calls throughout the codebase.

This improves testing, failure handling, decoupling, future provider replacement, and later retry/observability integration.

## 19. Testing Strategy

The LLM layer tests:

```text
configuration
client behavior
structured contracts
evidence transformation
prompt construction
interpretation orchestration
failure handling
context limits
integration behavior
```

Unit tests mock provider boundaries.

Integration tests verify that all internal LLM components work together without requiring a live API call.

## 20. LLM Pipeline Integration Test

```text
AnalyticsResult
+
MLResult
    ↓
EvidenceContext
    ↓
bounded evidence
    ↓
grounded prompt
    ↓
provider boundary
    ↓
LLMInterpretation
```

The integration test checks structured output, analytics evidence, ML evidence, grounding rules, analytics limits, and ML limits independently.

## 21. Verification Status

At completion of this phase:

```text
LLM test suite:
48 passed

Complete DecisionAI test suite:
152 passed
```

The only reported warning is a dependency-level deprecation warning from the installed `google-genai` package under Python 3.14.

It does not currently represent a failure in DecisionAI application code.

## 22. Current Limitations

The current LLM Engine intentionally does not yet provide:

- tool calling;
- autonomous agent loops;
- retrieval-augmented generation;
- multi-agent orchestration;
- automatic retries;
- production observability;
- token/cost tracking;
- prompt versioning;
- production-grade LLM eval datasets;
- causal inference;
- human approval workflows.

These belong to later phases.

## 23. Design Decisions

### Deterministic metrics remain authoritative

Revenue and analytical metrics are calculated in Python, not by Gemini.

### Structured evidence before prompting

Raw DataFrames are not passed directly to the model.

### Structured output over free text

Pydantic contracts make responses easier to validate and consume.

### Explicit context limits

Analytics and ML evidence are bounded before prompting.

### Prompt semantics matter

Evidence is not sufficient by itself. The model must also know how evidence may and may not be interpreted.

### Provider SDKs remain at architecture edges

Gemini-specific implementation details are isolated behind `GeminiClient`.

### Evaluation drives prompt improvements

Real outputs are reviewed for semantic failure modes and the prompt contract is refined accordingly.

## 24. Phase Outcome

The resulting architecture is:

```text
Data
↓
Deterministic Analytics
↓
Machine Learning
↓
Bounded Evidence Context
↓
Grounded Prompt Contract
↓
Gemini
↓
Validated Structured Interpretation
```

The LLM is positioned as an interpretation layer rather than a calculator or source of truth.

This establishes the foundation for later capabilities such as grounding/context engineering, tool calling, agentic workflows, LLM evaluation, observability, and production reliability.

## 25. Phase Status

```text
Phase 6 — Gemini Foundation / LLM Foundations

1. LLM Problem Definition            ✅
2. Gemini SDK Setup                  ✅
3. Configuration & Environment       ✅
4. Minimal Gemini Call               ✅
5. Prompt Contract                   ✅
6. Structured Output                 ✅
7. Pydantic Response Validation      ✅
8. Evidence Input Contract           ✅
9. AnalyticsResult → LLM Context     ✅
10. MLResult → LLM Context           ✅
11. Evidence-aware Prompting         ✅
12. Hallucination Boundaries         ✅
13. Failure Handling                 ✅
14. Unit Tests                       ✅
15. Integration Test                 ✅
16. Documentation                    ✅
```
