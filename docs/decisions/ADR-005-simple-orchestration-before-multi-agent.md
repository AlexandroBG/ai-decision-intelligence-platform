# ADR-005: Prefer Simple Orchestration Before Multi-Agent Architecture

## Status

Accepted

## Context

DecisionAI may eventually benefit from agentic capabilities such
as planning, tool use, analytical specialization, or review.

However, multi-agent architectures introduce additional model
calls, latency, cost, coordination behavior, failure modes, and
evaluation complexity.

The initial product hypothesis has not yet demonstrated that this
additional complexity is required.

## Decision

DecisionAI will first implement and evaluate simpler application
orchestration and controlled tool use.

A multi-agent architecture will only be introduced when measured
evidence demonstrates that simpler workflows are insufficient.

## Alternatives Considered

- Multi-agent architecture from the beginning.
- Single autonomous agent.
- Deterministic application orchestration with incremental AI
  capabilities.

## Consequences

Positive consequences include:

- Lower complexity.
- Lower model cost.
- Lower latency.
- Easier debugging.
- Easier evaluation.
- Better understanding of which problems actually require
  agentic behavior.

Negative consequences include:

- Some complex workflows may eventually require architectural
  evolution.
- Specialized agent roles are deferred.

## Revisit When

This decision should be revisited if evaluation demonstrates
persistent limitations in:

- Planning.
- Tool selection.
- Context management.
- Specialized analytical reasoning.
- Independent review or critique.

Any proposed multi-agent architecture should demonstrate
measurable improvement over the simpler baseline.