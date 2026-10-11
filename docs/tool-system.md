# Phase 08 — Tool System

## Status

Completed and validated.

## Objective

Expose deterministic DecisionAI capabilities as a stable, inspectable tool system that an LLM-driven agent can invoke safely.

## Architecture

```text
Agent
  ↓
ToolCall
  ↓
ToolExecutor
  ↓
ToolRegistry
  ↓
BaseTool
  ↓
Business capability
  ↓
ToolResult
```

## What was implemented

### Core contracts

- `ToolDefinition`
- `ToolCall`
- `ToolResult`

The contracts normalize names, validate payloads, and enforce success/error invariants.

### Base tool abstraction

The base tool defines the execution template and enforces tool-name identity, failure conversion, and result identity. `ToolExecutionError` is an expected, controlled failure whose authored message is preserved. Unexpected ordinary exceptions become a failed result with the fixed message `Tool execution failed.`; `KeyboardInterrupt` and `SystemExit` propagate.

Expected and unexpected tool failures remain observable as structured `ToolResult(success=False, ...)` values.

### Tool registry

The registry supports registration, duplicate-name rejection, lookup, listing names, listing public definitions, and containment checks.

### Tool executor

The executor safely handles external payloads and converts unknown tools or malformed tool requests into structured failures.

### Revenue comparison tool

Tool: `analyze_revenue`

Capabilities include date-window validation, dataset validation, deterministic revenue comparison, and explicit serialization of the analytics contract.

### Revenue driver tool

Tool: `analyze_revenue_drivers`

Capabilities include deterministic analytics execution, ranked observed deteriorations, preserved analytics ordering, configurable limits, and a descriptive—not causal—contribution interpretation.

### Revenue anomaly tool

Tool: `detect_revenue_anomalies`

Capabilities include baseline-period training, comparison-period scoring, selected dimensions, anomaly evidence, and preservation of the no-data-leakage boundary.

### Tool factory and catalog

The default registry exposes:

- `analyze_revenue`
- `analyze_revenue_drivers`
- `detect_revenue_anomalies`

The public catalog exposes only names, descriptions, and input schemas.

## Key architectural decisions

### Tools wrap product capabilities

The tool layer does not duplicate analytics or ML logic. It delegates to already-tested deterministic modules.

### Tool failures are observable

Operational failures are returned as structured values so the agent can reason about them.

### Unexpected implementation failures are sanitized

Unexpected ordinary exceptions from tool implementations become structured failures without exposing their raw messages. Process-level exceptions such as `KeyboardInterrupt` and `SystemExit` are not caught.

### Tool schemas are explicit

The agent sees only public contracts and cannot access implementation objects.

### The LLM is not a calculator

All metrics and analytical outputs are produced by deterministic code.

## Verification

The tool system was validated through unit tests, schema tests, factory tests, and integration tests.

The completed system demonstrated stable registry behavior, correct tool execution, correct external-payload validation, deterministic analytics integration, deterministic ML integration, and no hidden mutation of source data.

## Source principles applied in this phase

### AI Engineering / Andrew Ng

- Use LLMs for planning and interpretation while deterministic code handles computation.
- Build reliable systems around the model.

### AI Engineering Skills Map / Coding Agents

- Tool use requires explicit schemas, execution boundaries, and verification.
- Agent capabilities should be modular and observable.

### Shaping the Build

- Start with the minimum set of high-value business capabilities.
- Avoid adding speculative tools before evaluation demonstrates a need.

### Building and Deploying AI Applications

- Separate tools, models, deterministic services, and provider integrations.
- Make failure modes explicit.
- Preserve testability before deployment.

### Software Engineering Fundamentals

- Interface segregation.
- Stable contracts.
- Explicit errors.
- No hidden side effects.
- Composition through registry/executor abstractions.

## Phase conclusion

Phase 08 converted DecisionAI's deterministic analytics and ML capabilities into a safe tool interface suitable for agentic orchestration without moving business logic into the LLM layer.
