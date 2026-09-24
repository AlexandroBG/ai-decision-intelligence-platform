# Phase 13 — Security / Reliability

## Status

**Closed**

## Objective

Improve the reliability and security posture of the DecisionAI MVP without overengineering the system.

This phase focused on concrete production-oriented failure modes and defensive boundaries:

```text
provider failure
timeouts
invalid responses
oversized inputs
HTTP hardening
CORS
request correlation
```

The goal was not enterprise security. The goal was to make the MVP fail more predictably, communicate failures more clearly, and establish safer API defaults.

## 13.1 — Provider Error Handling

Problem observed in Phase 12:

```text
Gemini quota / provider failure
→ LLMProviderError
→ unhandled exception
→ HTTP 500
```

Implemented:

```text
LLMProviderError
→ HTTP 503 Service Unavailable
```

Response:

```json
{
  "detail": "AI provider is temporarily unavailable."
}
```

This separates external dependency failure from internal application defects.

## 13.2 — Failure Semantics

Formalized the distinction between:

```text
Agent termination
→ system executed correctly
→ HTTP 200
→ status="failed"
```

and:

```text
Provider unavailable
→ external dependency failed
→ HTTP 503
```

This prevents all failures from being treated as the same kind of event.

## 13.3 — UI Reliability Semantics

Introduced explicit client-side exception types:

- `DecisionAPIUnavailableError`
- `DecisionProviderUnavailableError`
- `DecisionAPIResponseError`
- `DecisionAPIHTTPError`

The UI now distinguishes:

```text
503
→ AI provider temporarily unavailable

connection failure
→ DecisionAI API unavailable

invalid JSON / contract
→ invalid API response

other HTTP failure
→ generic HTTP error
```

## 13.4 — HTTP Timeout Handling

Added explicit timeout semantics.

Previously:

```text
timeout
→ generic RequestError
→ treated like unreachable API
```

Now:

```text
timeout
→ DecisionAPITimeoutError
```

The client also verifies that its configured timeout is actually passed to `httpx`.

The UI can distinguish:

```text
connection refused
→ API unavailable

timeout
→ API too slow

503
→ provider unavailable
```

## 13.5 — Defensive Input Bounds

Added a maximum length to the public question contract:

```text
minimum: 1 character
maximum: 2000 characters
```

Implemented through Pydantic:

```python
question: str = Field(
    min_length=1,
    max_length=2000,
)
```

Boundary behavior:

```text
2000 characters
→ accepted

2001 characters
→ rejected with 422
```

A dedicated API test verifies that oversized input never reaches the application service.

## 13.6 — Basic Security Headers

Added global headers:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
```

Tests verify these headers on multiple routes, including `/health` and `/openapi.json`.

## 13.7 — Explicit CORS Policy

Configured FastAPI CORS explicitly.

Allowed development origins:

```text
http://localhost:8501
http://127.0.0.1:8501
```

Allowed methods:

```text
GET
POST
```

Allowed header:

```text
Content-Type
```

Credentials are disabled.

Unknown origins and arbitrary methods are rejected in preflight tests.

Important note:

The current Streamlit application calls FastAPI from Python server-side code, so CORS is not required for the current UI path. The explicit policy is still a safer default for future browser-side clients.

Wildcard CORS was intentionally avoided.

## 13.8 — Request ID / Correlation ID

Added a unique UUID to every HTTP request.

Response header:

```text
X-Request-ID
```

The same value is stored internally on:

```python
request.state.request_id
```

Tests verify:

- every request receives an ID
- IDs are valid UUIDs
- consecutive requests receive different IDs
- request IDs coexist with security headers

CORS also exposes `X-Request-ID` for future browser clients.

This prepares the application for Phase 14 observability.

## Reliability Model After Phase 13

```text
User request
    ↓
Input validation
    ↓
FastAPI
    ↓
Request ID assigned
    ↓
Service / Agent
    ↓
Provider
```

Failure semantics:

```text
Oversized / invalid input
→ 422

Agent guardrail termination
→ 200 + status="failed"

Provider unavailable
→ 503

Frontend connection failure
→ API unavailable message

Frontend timeout
→ timeout-specific message

Invalid API response
→ response-validation message
```

## Security Posture After Phase 13

Implemented:

- strict Pydantic request contracts
- forbidden extra fields
- bounded user input
- explicit CORS
- security response headers
- provider failure isolation
- HTTP timeout handling
- request correlation IDs

Intentionally deferred:

- authentication
- authorization
- user accounts
- persistent sessions
- public rate limiting
- secrets manager integration
- TLS termination
- WAF / edge security
- production network policy

These were deferred because the system is still a local MVP and has not yet been publicly deployed.

## Validation

The phase was developed incrementally with Ruff and pytest after every block.

Final confirmed state:

```text
Request ID tests: 3 passed
API suite: 38 passed
Full suite: 657 passed
```

Final full-suite result:

```text
657 passed
2 warnings
```

The two remaining warnings are known and non-blocking:

1. `google-genai` uses `_UnionGenericAlias`, deprecated for future Python versions.
2. Starlette emits a deprecation warning related to `httpx` / `TestClient`.

Neither warning represents a failing DecisionAI test.

## Learning Outcome

Phase 13 reinforces that reliability is not just “catch exceptions”.

A reliable application needs to distinguish:

```text
bad input
application termination
network failure
timeout
provider failure
invalid response
```

and assign each one a clear contract.

Security also benefits from explicit defaults:

```text
bounded inputs
known origins
known methods
known headers
browser hardening
correlation IDs
```

## Closure Decision

**Phase 13 — Security / Reliability is closed for the current MVP scope.**

The next phase is:

# Phase 14 — Observability

The existing `X-Request-ID` will become the foundation for structured logs and request tracing across:

```text
FastAPI
→ service
→ agent
→ tools
→ LLM
```
