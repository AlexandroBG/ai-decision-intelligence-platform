# Phase 12 — FastAPI + Streamlit

## Status

**Closed**

## Objective

Turn DecisionAI from an internal AI/analytics system into a minimal full-stack application with a stable HTTP API and a simple user interface.

Target architecture:

```text
Streamlit
    ↓ HTTP
FastAPI
    ↓
RuntimeDecisionService
    ↓
AgentLoop
    ↓
Tools / Analytics / ML / Gemini
```

Architectural rule:

> Streamlit communicates with DecisionAI through HTTP. It does not import the agent runtime, Gemini client, or data layer directly.

## 12.1 — API Contract Foundation

Created explicit Pydantic contracts for:

- `DecisionRequest`
- `DecisionResponse`
- `HealthResponse`

Important decisions:

- extra fields are forbidden
- response status is explicit
- execution metadata is returned
- contracts are independently testable

## 12.2 — Health Endpoint

Implemented:

```http
GET /health
```

Example:

```json
{
  "status": "ok",
  "service": "decisionai-api",
  "version": "0.1.0"
}
```

This verifies that FastAPI is alive without invoking Gemini or the agent.

## 12.3 — Decision Endpoint with Dependency Injection

Implemented:

```http
POST /decisions
```

Flow:

```text
POST /decisions
    ↓
DecisionService dependency
    ↓
RuntimeDecisionService
```

Dependency injection keeps the HTTP layer separated from runtime implementation and lets tests inject fake services without calling Gemini.

## 12.4A — Runtime Adapter

Connected the API service abstraction to the real DecisionAI agent runtime.

`RuntimeDecisionService` maps `AgentRunResult` into `DecisionResponse`.

Semantic mapping:

```text
AgentRunResult.status == "completed"
→ DecisionResponse.status == "completed"

Any valid agent termination / guardrail stop
→ DecisionResponse.status == "failed"
```

## 12.4B — Production Application Wiring

Created the production factory that assembles:

```text
LLMConfig
    ↓
GeminiClient
    ↓
CSV data loaders
    ↓
build_agent_loop(...)
    ↓
RuntimeDecisionService
```

This connected the real application stack while preserving test isolation.

An obsolete test initially triggered real Gemini calls through the default dependency. That test was corrected so automated tests no longer consume provider quota accidentally.

## 12.5 — Real HTTP End-to-End Validation

FastAPI was started with Uvicorn and validated through real HTTP.

Confirmed:

- server startup
- `/health` returns 200
- `/decisions` routing works
- dependency injection works
- runtime factory works
- CSV data loads
- agent loop is reached
- Gemini client is reached

The final AI answer could not be validated because Gemini returned:

```text
429 RESOURCE_EXHAUSTED
```

This was treated as an external provider availability issue, not as an application wiring failure.

At this stage the provider failure still surfaced as HTTP 500. That concern was intentionally deferred to Phase 13.

## 12.6A — Streamlit HTTP Client

Created:

```text
app/ui/client.py
```

The client:

- calls `/health`
- calls `/decisions`
- validates API responses with existing Pydantic contracts
- converts connection and response failures into application-level exceptions

The client was unit tested with `httpx.request` monkeypatched, so tests made no real network or Gemini calls.

A pytest module-name collision occurred because these files shared the same basename:

```text
tests/llm/test_client.py
tests/ui/test_client.py
```

The UI test was renamed to:

```text
tests/ui/test_ui_client.py
```

## 12.6B — Streamlit User Interface

Created:

```text
app/ui/streamlit_app.py
```

The original name `app/ui/app.py` caused an import collision with the root `app` package, so it was renamed.

The UI includes:

- title and caption
- API health indicator
- business question input
- Analyze button
- AI answer rendering
- execution metrics
  - steps
  - tool calls
  - evidence steps
- graceful error rendering

Validated locally with:

```powershell
python -m uvicorn app.api.main:app --reload
```

and:

```powershell
python -m streamlit run app/ui/streamlit_app.py
```

Streamlit loaded successfully and communicated with FastAPI.

The live decision request again reached Gemini and failed because of provider quota, but the UI handled the failure without crashing.

## Final Phase 12 Architecture

```text
┌──────────────────────────────┐
│ Streamlit                    │
│ User interface               │
└───────────────┬──────────────┘
                │ HTTP
┌───────────────▼──────────────┐
│ FastAPI                      │
│ Public API contracts         │
└───────────────┬──────────────┘
                │
┌───────────────▼──────────────┐
│ RuntimeDecisionService       │
│ Application adapter          │
└───────────────┬──────────────┘
                │
┌───────────────▼──────────────┐
│ AgentLoop                    │
│ AI orchestration             │
├──────────────────────────────┤
│ Deterministic tools          │
│ Analytics / ML / data        │
├──────────────────────────────┤
│ Gemini                       │
└──────────────────────────────┘
```

## Validation

Confirmed during the phase:

- API contracts tested
- health endpoint tested
- decisions endpoint tested
- dependency injection tested
- runtime adapter tested
- production factory tested
- real Uvicorn startup validated
- real Streamlit startup validated
- Streamlit → FastAPI communication validated
- test suite remained green

At the end of the Streamlit client work, the full suite had reached:

```text
640 passed
```

The count increased later in Phase 13 as new security and reliability tests were added.

## Known Caveats at Closure

1. Gemini provider quota prevented validation of a successful live AI answer.
2. Provider errors still surfaced as HTTP 500 at the end of Phase 12.
3. Dependency packaging for deployment could be finalized later.
4. Authentication was intentionally not introduced for the local MVP.
5. Observability and request tracing were deferred.

## Learning Outcome

Phase 12 demonstrated an important AI Engineering principle:

> An AI capability becomes a real application only when it is integrated behind stable software boundaries.

DecisionAI now has:

- a backend API
- explicit contracts
- dependency injection
- a runtime adapter
- a production assembly path
- a frontend
- real HTTP integration

## Closure Decision

**Phase 12 — FastAPI + Streamlit is closed.**

The remaining provider failure became the first reliability concern addressed in Phase 13.
