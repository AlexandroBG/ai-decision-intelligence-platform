# Phase 07 — Grounding & Context Engineering

## Status

Completed and validated.

## Objective

Build a grounded LLM interpretation layer for DecisionAI so that model-generated business conclusions are tied to explicit evidence rather than unsupported free-form generation.

## What was implemented

- Structured evidence context for analytics and ML outputs.
- Stable evidence IDs within each context.
- Evidence provenance for revenue summary, analytics drivers, and ML anomalies.
- Canonical `grounded_claims` as the source of truth for factual and inferential outputs.
- Claim types: `fact`, `inference`, and `unknown`.
- Grounding validation rules:
  - facts require at least one valid evidence ID;
  - inferences require at least one valid evidence ID;
  - unknown claims may omit evidence;
  - invented evidence IDs are rejected.
- Grounding coverage calculation and threshold enforcement.
- Evidence registry and evidence resolution.
- Context selection policies for analytics drivers and ML anomalies.
- Context budgets, retention, utilization, omission counts, and pressure detection.
- Context-selection invariants.
- Real Gemini grounding evaluation.

## Key architectural decisions

### Deterministic evidence first

Business calculations remain in Python/SQL/ML code. Gemini interprets structured evidence rather than recomputing metrics.

### Canonical grounded claims

`grounded_claims` are the canonical LLM output. Facts, inferences, and unknowns are derived from them rather than maintained as separate competing sources of truth.

### Provenance is explicit

Evidence items preserve where they came from so downstream systems can resolve and inspect the source of a claim.

### Context is selected, not dumped

Only relevant deteriorations and detected anomalies are included. Context budgets are explicit and measurable.

### Contribution is not causality

Observed contribution values are descriptive. The system explicitly prevents causal overclaiming and does not allow contribution percentages from overlapping dimensions to be summed.

## Verification

The grounding and context-engineering layer was validated with unit, integration, and real Gemini evaluations.

Observed real Gemini grounding coverage reached full coverage in repeated runs under the implemented validation rules.

## Known limitations

- Semantic correctness of a fully grounded statement is not guaranteed solely by presence of an evidence ID.
- Context evidence IDs are stable within the constructed context, not globally.
- Final semantic quality and claim usefulness require dedicated evaluation metrics.

These limitations are intentionally deferred to Phase 10 — Evaluation Framework.

## Source principles applied in this phase

### AI Engineering / Andrew Ng

- Build systems around models rather than treating the model as the application.
- Use evaluation and iteration as engineering primitives.
- Ground model behavior in deterministic system components.

### AI Engineering Skills Map / Coding Agents

- Context engineering is a core AI engineering skill.
- Model output must be constrained, inspectable, and evaluated.
- Structured interfaces between LLMs and deterministic systems improve reliability.

### Shaping the Build

- Reduce uncertainty incrementally.
- Introduce only the context-management mechanisms required by the current product.
- Avoid premature multi-agent or retrieval complexity.

### Building and Deploying AI Applications

- Separate model reasoning from deterministic business computation.
- Validate provider output at application boundaries.
- Treat reliability and evaluation as first-class production concerns.

### Software Engineering Fundamentals

- Explicit contracts and invariants.
- Separation of concerns.
- Stable interfaces.
- Defensive validation.
- Testable deterministic components.

## Phase conclusion

Phase 07 established the evidence and grounding foundation required for reliable agentic behavior. It allows DecisionAI to distinguish between what the system knows, what it infers, and what remains unknown while preserving traceability to structured evidence.
