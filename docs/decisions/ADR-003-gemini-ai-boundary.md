# ADR-003: Isolate Gemini Behind an AI Boundary

## Status

Accepted

## Context

Gemini is the initial external AI provider for DecisionAI.

Direct provider-specific calls throughout the application would
increase coupling and make testing, replacement, and provider
evolution more difficult.

## Decision

Gemini-specific integration will remain isolated behind the
DecisionAI AI boundary.

Higher-level application components should depend on AI
capabilities or contracts rather than Gemini SDK details where
practical.

## Alternatives Considered

- Call Gemini directly from multiple application modules.
- Create a provider-agnostic abstraction from the beginning.
- Isolate Gemini-specific integration behind a focused AI
  boundary.

## Consequences

Positive consequences include:

- Reduced provider coupling.
- Easier testing.
- Easier model or provider evolution.
- Clearer AI error handling.
- Better observability of model calls.

Negative consequences include:

- Some additional integration structure is required.
- Premature abstraction must still be avoided.

## Revisit When

The boundary should be revisited if:

- Multiple AI providers are introduced.
- Model-routing requirements emerge.
- Evaluation shows a need for different AI execution strategies.