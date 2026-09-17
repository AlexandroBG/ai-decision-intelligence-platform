# ADR-002: Use Deterministic Analytics as the Numerical Source of Truth

## Status

Accepted

## Context

DecisionAI must calculate business metrics such as revenue,
growth, order volume, average order value, and contributor
changes.

Language models are probabilistic and may produce inconsistent
or unsupported numerical results.

## Decision

Deterministic Python or SQL logic will remain the authoritative
source for numerical analytical results.

AI models may interpret, prioritize, explain, or orchestrate
analytical capabilities but should not replace deterministic
calculations where exact computation is available.

## Alternatives Considered

- Perform calculations directly through the language model.
- Use a mixed approach without an explicit source-of-truth rule.
- Use deterministic analytical tools as the authoritative layer.

## Consequences

Positive consequences include:

- Reproducible calculations.
- Easier testing.
- Better traceability.
- Improved numerical reliability.
- Clearer separation between evidence and interpretation.

Negative consequences include:

- Analytical capabilities must be explicitly implemented.
- New supported metrics require deterministic code or SQL.
- The system may be less flexible for unsupported calculations.

## Revisit When

This principle should only be reconsidered for analytical tasks
where deterministic implementation is not practical and where
evaluation demonstrates that model-based reasoning is reliable
enough for the intended use.