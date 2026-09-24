# DecisionAI

> An AI-powered decision intelligence platform that combines business data, deterministic analytics, machine learning, and agentic workflows to turn raw data into evidence-backed decisions.

## Project status

**Checkpoint: Phase 15 complete — Optimization ✅**

DecisionAI currently includes:

- deterministic revenue analytics
- ML-based anomaly detection
- provider-neutral LLM integration
- Gemini and OpenAI adapters
- grounded tool-using agent workflows
- structured evidence and provenance
- evaluation and error-analysis pipelines
- FastAPI backend
- Streamlit interface
- reliability, security, and observability foundations
- optimization metrics for tool usage, failures, duplication, and latency

Current automated test status:

```text
706 passed
1 known google-genai deprecation warning
```

The next phase is **Phase 16 — Docker + CI/CD + Cloud deployment**.

---

## What problem does DecisionAI solve?

Business users often have data but still struggle to answer questions such as:

> What is affecting revenue performance, and what should I investigate first?

DecisionAI is designed to answer this type of question by combining deterministic calculations with LLM-based planning and interpretation.

The core principle is:

> **The LLM decides what evidence is needed. Deterministic tools calculate the business facts.**

The language model is not trusted as a calculator.

---

## Example workflow

For a question such as:

```text
Compare revenue from July 2025 with August 2025.
What is affecting revenue performance, and what should I investigate first?
```

DecisionAI can:

1. calculate the total revenue comparison with a deterministic analytics tool
2. analyze the largest observed deteriorations across business dimensions
3. preserve tool outputs as structured evidence
4. generate a grounded answer referencing that evidence
5. recommend an investigation priority without claiming causality

Example analytical result from the synthetic evaluation dataset:

```text
July 2025 revenue:   $1,773,419.93
August 2025 revenue: $1,275,769.95
Absolute change:      -$497,649.98
Percentage change:    -28.06%
```

Observed deteriorations are treated as associations/contributions, **not causal proof**.

---

## Architecture

```text
User
  |
  v
FastAPI / Streamlit
  |
  v
Agent Runtime
  |
  +--> LLM Decision Layer
  |      |
  |      +--> Gemini
  |      +--> OpenAI
  |
  +--> Tool Registry
          |
          +--> analyze_revenue
          +--> analyze_revenue_drivers
          +--> detect_revenue_anomalies
                  |
                  v
          Deterministic Analytics / ML
                  |
                  v
            Structured Evidence
                  |
                  v
              Final Answer
```

### Separation of responsibilities

**Python / deterministic analytics**
- revenue calculations
- period comparisons
- driver analysis
- contribution calculations
- structured business evidence

**Machine learning**
- anomaly detection with Isolation Forest
- evidence generation, not autonomous business conclusions

**LLM**
- intent interpretation
- next-action planning
- tool selection
- evidence synthesis
- grounded communication

---

## Agent design

DecisionAI currently uses a **single-agent tool-using workflow**.

```text
QUESTION
  ↓
DECIDE NEXT ACTION
  ↓
TOOL CALL OR FINAL ANSWER
  ↓
OBSERVATION
  ↓
DECIDE AGAIN
```

A multi-agent architecture is intentionally deferred until evaluations demonstrate that it is necessary.

### Evidence coverage

An important optimization completed in Phase 15 taught the agent to verify that all analytical needs in a multi-part question are covered before returning a final answer.

For example:

```text
"Compare revenue and identify the largest deteriorations."
```

requires both:

```text
aggregate comparison
+
driver analysis
```

while:

```text
"Report the revenue change only."
```

requires only the aggregate comparison.

This helps prevent both **under-tooling** and unnecessary **over-tooling**.

---

## Grounding and evidence

Tool observations are stored as structured evidence.

The agent must:

- use valid tool observations
- reference valid evidence steps
- avoid inventing evidence IDs
- avoid unsupported certainty
- avoid causal claims from contribution analysis
- avoid summing overlapping dimensional contributions

DecisionAI distinguishes between:

- facts
- inferences
- unknowns

This makes final answers more auditable than free-form generation alone.

---

## Deterministic analytics

The revenue calculation is:

```text
revenue = quantity × unit_price × (1 - discount)
```

The analytics layer supports:

- baseline vs comparison period revenue
- absolute change
- percentage change
- driver analysis across business dimensions
- contribution to total observed change

The current synthetic business dataset includes:

- orders
- customers
- products

with dimensions such as:

- region
- segment
- category
- sales channel

---

## Machine learning

DecisionAI includes anomaly detection based on **Isolation Forest**.

Example daily features include:

- daily revenue
- order count
- units sold
- average order value
- average discount

An anomaly is treated as:

> evidence worth investigating

not as:

> proof of cause

---

## LLM provider abstraction

The core agent does not depend directly on a specific provider SDK.

Current provider adapters:

- **Gemini**
- **OpenAI**

Gemini is the current default provider.

Provider selection is configuration-driven:

```text
LLM_PROVIDER=gemini
```

or:

```text
LLM_PROVIDER=openai
```

Provider-specific SDK logic stays at the edge of the architecture.

---

## Evaluation framework

DecisionAI includes an evaluation system for agent behavior, not only unit tests.

Current evaluation dimensions include:

- agent completion
- required tool coverage
- tool selection
- numeric ground truth
- semantic safety
- causal-overclaim detection
- unsupported-certainty detection
- recommendation presence
- duplicate tool calls
- tool success rate
- tool failures
- agent steps
- tool-call count
- latency
- provider availability

Quality failures and provider availability failures are measured separately.

This matters because:

```text
bad agent decision != provider outage
```

---

## Phase 15 optimization result

Before optimization, the complex revenue case produced:

```text
Required tool coverage: 50%
Ground truth:            0%
Semantic safety:         100%
Overall result:          FAIL
```

After root-cause analysis, the evidence-coverage policy was improved.

A real Gemini evaluation then produced:

```text
Used tools:
- analyze_revenue
- analyze_revenue_drivers

Required tool coverage: 100%
Ground truth:            100%
Semantic safety:         100%
Overall result:          PASS

Steps:                   3
Tool calls:              2
Tool failures:           0
Duplicate calls:         0%
Latency:                 ~9.39 s
```

A simple comparison-only case correctly used only:

```text
analyze_revenue
```

and also passed with 100% tool selection, ground truth, and semantic safety.

A subsequent multi-run check produced **2/2 quality passes** before the provider hit a rate/quota limit.

---

## Observability

Current observability includes structured logging and in-process metrics such as:

- `requests_total`
- `provider_errors_total`
- `agent_completed_total`
- `agent_failed_total`
- `tool_calls_total`
- `llm_calls_total`

A `/metrics` endpoint exposes current metrics.

Future production work may extend this to external telemetry systems such as Prometheus/OpenTelemetry.

---

## Reliability and safety principles

DecisionAI follows several project rules:

- deterministic tools calculate business metrics
- LLMs do not invent tool results
- provider failures are mapped separately from AI-quality failures
- expected tool errors are structured
- programming bugs are not silently swallowed
- secrets are loaded from environment variables
- prompts and raw provider responses are not intentionally logged
- contribution/association does not imply causality
- human review remains appropriate for important business actions

---

## Repository structure

```text
app/
├── agent/
├── analytics/
├── api/
├── evaluation/
├── llm/
├── ml/
├── observability/
└── tools/

scripts/
tests/
artifacts/
```

Key boundaries:

```text
agent/       orchestration and decision logic
analytics/   deterministic business calculations
evaluation/  quality and optimization measurement
llm/         provider adapters and abstractions
ml/          anomaly detection
tools/       agent-callable deterministic capabilities
api/         FastAPI application
```

---

## Running tests

From the project virtual environment:

```powershell
python -m pytest -q
```

Current checkpoint:

```text
706 passed
```

Lint and format validation:

```powershell
python -m ruff check . --fix
python -m ruff format .
python -m ruff check .
```

---

## Environment variables

Do not commit API keys.

Example PowerShell configuration:

```powershell
$env:LLM_PROVIDER="gemini"
$env:GEMINI_API_KEY="<your-local-key>"
```

For the OpenAI adapter:

```powershell
$env:LLM_PROVIDER="openai"
$env:OPENAI_API_KEY="<your-local-key>"
```

Keep real credentials only in your local environment or a secrets manager.

---

## Evaluation artifacts

Phase 15 evaluation artifacts are stored under:

```text
artifacts/phase15/
```

including provider-specific outputs for cases such as:

```text
revenue_decline_v1
revenue_comparison_only_v1
```

These artifacts make optimization decisions traceable.

---

## Engineering philosophy

DecisionAI is being built around this loop:

```text
PLAN
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

The project intentionally avoids adding architectural complexity without evaluation evidence.

Examples:

- no multi-agent system just because multi-agent systems are fashionable
- no RAG/vector database for structured business data that does not currently require it
- no optimization without a measurable problem
- no causal claims from correlational evidence

---

## Roadmap

Completed:

```text
Phase 0   Foundation                         ✅
Phase 1   Product Spec                       ✅
Phase 2   Architecture                       ✅
Phase 3   Data                               ✅
Phase 4   Deterministic Analytics            ✅
Phase 5   ML                                 ✅
Phase 6   Gemini Foundation                  ✅
Phase 7   Grounding / Context Engineering    ✅
Phase 8   Tool System                        ✅
Phase 9   Agentic Workflow                   ✅
Phase 10  Evaluation Framework               ✅
Phase 11  Error Analysis                     ✅
Phase 12  FastAPI + Streamlit                ✅
Phase 13  Security / Reliability             ✅
Phase 14  Observability                      ✅
Phase 15  Optimization                       ✅
```

Next:

```text
Phase 16  Docker + CI/CD + Cloud             ← NEXT
Phase 17  Coding Agent Lab
Phase 18  Shaping / Communication / Leadership
Phase 19  Portfolio Release
Phase 20  Continuous Learning
```

---

## Current limitations

This is an active engineering project, not a production SaaS release.

Current limitations include:

- synthetic evaluation data
- limited real-world business datasets
- small live multi-run sample sizes
- provider rate/quota variability
- in-process metrics rather than full production telemetry
- cloud deployment not yet completed
- CI/CD and containerization are Phase 16 work
- human review is still expected for important business decisions

These limitations are tracked intentionally rather than hidden.

---

## Why this project exists

DecisionAI is being developed as a practical AI Engineering project focused on the parts that matter beyond a chatbot demo:

- deterministic computation
- tool use
- agent orchestration
- structured evidence
- provider abstraction
- evaluation
- error analysis
- reliability
- observability
- optimization
- deployment

The goal is to build a system whose AI behavior can be **measured, debugged, and improved**.

---

## License

Add the license you choose for the repository before public release.
