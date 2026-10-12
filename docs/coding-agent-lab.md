# Phase 17 — Coding Agent Lab

## Overview

Phase 17 focused on learning how to direct coding agents as engineering collaborators rather than treating them as autocomplete tools. The goal was to develop a repeatable operating model for shaping tasks, controlling scope, reviewing agent work, verifying evidence, handling failures, and authorizing state-changing actions safely.

The phase used DecisionAI as the working environment and emphasized evidence-based engineering, minimal changes, explicit permission boundaries, and human review.

## Objectives

By the end of this phase, the workflow should be able to:

- Shape coding-agent tasks with explicit scope and acceptance criteria.
- Distinguish direct evidence from inference and historical documentation.
- Review agent-generated code and plans rather than trusting summaries.
- Detect stopping short, overengineering, scope drift, and evidence overclaiming.
- Use repository guidance such as `AGENTS.md` as standing context.
- Classify failures by layer before changing code.
- Choose the right tool or evidence source for each claim.
- Use subagents or parallel work only when coordination cost is justified.
- Enforce permission boundaries for Git, CI/CD, cloud, secrets, and deployment.
- Report completion using `VERIFIED`, `INFERRED`, and `UNVERIFIED` claims.
- Treat tests, CI, deployment, and runtime verification as separate evidence levels.

## 17.1 — First Controlled Coding-Agent Task

The first task deliberately constrained the agent to a very small deployment workflow change.

The agent was asked to reduce verbose ECS deployment output in `.github/workflows/deploy.yml`.

The implementation added `--no-cli-pager > /dev/null` to the ECS service update commands.

### Lesson

A good first coding-agent task should be small, easy to review, operationally bounded, reversible, and verifiable with a narrow diff.

The agent should not receive broad autonomy before its behavior under constraints is understood.

## 17.2 — Agent Autonomy Levels

A dependency lock-freshness task demonstrated why agent plans must be reviewed technically before execution.

The first proposal was rejected because it used the wrong `pip-tools` version, a questionable `pip-compile --check` assumption, and unnecessary `--no-index`.

The corrected CI implementation initially ran on Ubuntu, but this exposed platform-specific lockfile differences involving packages such as `colorama` and `tzdata`.

The final design moved lock freshness verification to `windows-latest`, matching the environment used to generate the lockfiles.

### Lesson

Agent autonomy should increase only after the agent demonstrates that it can inspect existing tooling, preserve exact pinned versions, understand platform-specific behavior, and respond correctly to CI evidence.

A plausible implementation is not the same as a correct implementation.

## 17.3 — Review Quality and Failure Modes

A tool error-handling task exposed a critical review pattern.

The agent initially changed `BaseTool.execute()` so all exceptions were sanitized into the same generic failure.

That caused existing controlled `ToolExecutionError` messages to be lost and produced 22 test failures.

The final design preserved expected domain errors while sanitizing only unexpected implementation failures.

### Final behavior

- `ToolExecutionError` keeps its authored message.
- Unexpected ordinary exceptions become `Tool execution failed.`
- `KeyboardInterrupt` and `SystemExit` continue to propagate.

### Lesson

Tests are behavioral contracts.

Do not “fix” a large set of tests merely to accommodate a bad implementation. First determine whether the implementation broke an intentional contract.

## 17.4 — Directing the Workflow

A request-level logging improvement was shaped before implementation.

The final change added aggregate tool-call counts per request: total tool calls, successful tool calls, and failed tool calls.

The implementation stayed inside `RuntimeDecisionService` and reused existing observations instead of introducing new state, middleware, or logging infrastructure.

### Lesson

A well-shaped task should define the behavior, owning layer, accepted scope, forbidden redesigns, and verification requirements.

The agent should be directed toward the smallest sufficient implementation.

## 17.5 — Customizing the Agent Environment

A root-level `AGENTS.md` was added to provide repository-specific standing context.

It documents defaults for architecture, tool failure semantics, privacy, verification, dependencies, Git behavior, and deployment safety.

A documentation mismatch in the tool-system guide was also corrected so the written behavior matched the current tool boundary.

### Lesson

Repository guidance improves agent defaults, but it does not replace human review.

Standing instructions are especially useful for invariants that should apply repeatedly across tasks.

## 17.6 — Retrieval, Context Discipline, and Stopping Short

The agent was tested on whether it could distinguish remembered context from directly verified repository evidence.

When repository access failed, the agent correctly stopped and reported that it could not verify the requested files.

Later, when the environment worked, it produced a complete plan and implemented an API-level regression test for unexpected tool exceptions.

Verification included focused regression tests, related tests, Ruff, the full pytest suite, `git diff --check`, `git status`, and final diff review.

Final local result:

```text
741 passed, 1 warning
```

### Lesson

A coding agent should never convert memory, standing context, or inference into a claim of direct verification.

Stopping short is avoided when “done” includes the full verification loop, not merely writing code.

## 17.7 — Avoiding Overengineering

The agent was asked to add a regression test for an existing provider 429 response.

Repository inspection revealed that the test already existed.

The correct response was to make no change and verify the existing behavior instead.

### Lesson

The best implementation is sometimes no implementation.

A coding agent should first prove that a gap exists before creating abstractions, helpers, middleware, or duplicate tests.

## 17.8 — Dangerous Actions and Permission Boundaries

The agent was asked to prepare for deployment verification without receiving permission to deploy.

It correctly separated read-only actions from state-changing actions.

Read-only actions included repository inspection, Git history inspection, workflow review, local verification, and read-only cloud queries when authorized.

Explicit approval remained required for staging, committing, pushing, workflow triggers or reruns, image publication, deployment, AWS mutations, secret changes, and ECS desired-count changes.

### Lesson

Preparation is not authorization.

In this repository, `git push origin main` is operationally significant because a successful push-based CI run can lead to automatic deployment.

## 17.9 — Intervention and Recovery

The agent correctly discovered that a requested logging regression was already covered, but then proposed an unnecessary extension to add another privacy sentinel.

The human reviewer rejected the extra scope while preserving the valid inspection work.

Verification-only execution then confirmed the current behavior.

### Lesson

Intervention does not mean restarting the task.

A good recovery process is:

```text
keep valid analysis
→ reject unnecessary expansion
→ restate scope
→ verify existing behavior
→ finish cleanly
```

## 17.10 — Subagents and Parallel Coordination

The agent evaluated whether deployment invariant analysis should be split across multiple workstreams.

It correctly concluded that one workstream was sufficient because the invariants depended on the same small set of CI and deployment files.

### Lesson

More agents do not automatically improve engineering.

Parallel work is justified only when subtasks are genuinely independent, ownership boundaries are clear, outputs are independently reviewable, and coordination cost is lower than the time saved.

## 17.11 — Tool Selection and Harness Awareness

The agent separated different evidence sources:

- Git for local repository state.
- Local Python for tests and lint.
- GitHub for CI and deployment workflow evidence.
- AWS for ECS runtime state.

It correctly refused to infer current GitHub or AWS state when authentication was unavailable.

### Harness model

```text
LLM = reasoning engine
Harness = tools + execution environment + permissions + context delivery
Sandbox = restricted execution boundary inside the harness
```

A capable model can still fail to verify a task if the harness cannot access the repository, interpreter, network, or external systems.

### Lesson

```text
could reason about it
≠
actually verified it
```

## 17.12 — Verification Depth and Evidence Hierarchy

DecisionAI uses cumulative evidence with separate claim boundaries.

### Evidence ladder

1. Static inspection
2. Focused unit or regression tests
3. Related integration or API tests
4. Full local test suite
5. Lint and static checks
6. CI on the exact commit SHA
7. Deployment workflow result
8. ECS configured state
9. Live runtime verification

Each level proves something different.

Examples:

```text
pytest passed
≠ safe to deploy

CI green
≠ runtime healthy

Deploy green
≠ ECS rollout verified

ECS configured
≠ application behavior verified
```

If ECS services intentionally use `desiredCount=0`, the correct claim is:

```text
Release configuration verified; live runtime verification not performed.
```

## 17.13 — Failure Classification and Escalation

Failures should be classified by the earliest boundary that demonstrably failed.

The operating categories used in DecisionAI are application code, regression test, local Python/test environment, coding-agent harness or sandbox, dependency or lockfile, CI, deployment workflow, AWS/ECS runtime, AI provider, and observability evidence gap.

### Core rule

```text
symptom
→ identify earliest failing boundary
→ gather evidence at that layer
→ act at that layer
→ escalate only when justified
```

Examples:

```text
environment problem ≠ application bug
CI failure ≠ AWS failure
AWS failure ≠ provider failure
provider failure ≠ retry everything
```

The repository intentionally does not retry provider 429 responses automatically.

## 17.14 — Confidence Calibration

The agent was required to separate its conclusions into:

### VERIFIED

Directly inspected or executed evidence.

### INFERRED

A reasonable conclusion supported by repository structure or design, but not directly proven in the current session.

### UNVERIFIED

A claim requiring additional access, credentials, tools, runtime execution, or fresh external evidence.

### Lesson

Confidence in source code is not the same as confidence in production state.

A branch can be locally healthy while deployment, ECS runtime health, provider availability, secrets, and cost-control state remain unverified.

## 17.15 — Final Coding-Agent Operating Model

The final operating model for DecisionAI is:

> Define the behavioral outcome, inspect the owning layer, make the smallest justified change, and verify each claim at the layer capable of establishing it.

### Task shaping

Define the trigger, current behavior, required behavior, affected boundary, acceptance criteria, non-goals, and forbidden actions.

### Repository inspection

Inspect `AGENTS.md`, the owning implementation, callers, contracts, adjacent tests, ADRs, and CI/deployment configuration when relevant.

Separate current source evidence, executed evidence, historical documentation, and inference.

### Planning

Prefer the existing owner of the behavior, minimal diffs, no new dependency without demonstrated need, no abstraction without a real repeated problem, and no parallelism without independent workstreams.

### Implementation

Preserve DecisionAI invariants:

- deterministic calculations remain in Python/SQL/analytics code;
- LLMs handle planning, orchestration, interpretation, and communication;
- provider SDKs stay at the provider boundary;
- tool execution remains bounded;
- grounding checks remain intact;
- privacy-safe logging remains intact;
- expected domain errors remain distinct from unexpected failures.

### Verification

Use increasing verification depth:

```text
focused tests
→ related tests
→ Ruff
→ full pytest suite
→ git diff --check
→ diff/status review
→ exact-SHA CI
→ deployment/runtime evidence when relevant
```

### Human intervention

Redirect the agent when it expands scope, proposes architecture changes without evidence, crosses permission boundaries, exposes sensitive information, repeatedly retries without learning, or cannot identify the failing layer.

Recovery should preserve valid work and revert only specifically identified invalid work.

## Permission Model

### Safe to inspect

- repository files;
- tests;
- workflows;
- Git history;
- status;
- diffs;
- non-secret configuration;
- authorized read-only external status.

### Requires explicit approval

- file edits when not already authorized;
- dependency changes;
- staging;
- commit;
- push;
- workflow trigger or rerun;
- Docker image publication;
- deployment;
- AWS resource mutation;
- secret retrieval or modification;
- ECS scaling or desired-count changes.

A request to implement code does not automatically authorize publication or deployment.

## Completion Model

A task is complete only when acceptance criteria are satisfied, required verification passes, the diff is scoped, unrelated work is preserved, forbidden actions were avoided, and material evidence gaps are disclosed.

Completion should distinguish:

```text
VERIFIED
INFERRED
UNVERIFIED
```

Local completion, CI verification, deployment completion, and runtime health are separate milestones.

## Reusable Coding-Agent Checklist

### Scope

- [ ] Define trigger, desired behavior, acceptance criteria, and non-goals.
- [ ] Record forbidden actions.
- [ ] Preserve unrelated existing work.

### Inspect

- [ ] Read repository guidance.
- [ ] Inspect the owning implementation and contracts.
- [ ] Inspect adjacent tests and callers.
- [ ] Check relevant ADRs and workflows.
- [ ] Separate direct evidence from inference and historical documentation.

### Plan

- [ ] Choose the smallest safe change.
- [ ] Confirm a real gap exists before adding code.
- [ ] Justify abstractions, dependencies, or parallel work.
- [ ] Identify what must not change.

### Implement

- [ ] Preserve architecture boundaries.
- [ ] Preserve privacy and failure semantics.
- [ ] Keep the diff minimal.
- [ ] Avoid speculative refactors.

### Verify

- [ ] Run focused tests.
- [ ] Run related regression/integration tests.
- [ ] Run `python -m ruff check .`.
- [ ] Run `python -m pytest -q`.
- [ ] Run `git diff --check`.
- [ ] Inspect `git status` and the final diff.
- [ ] Attribute CI evidence to the exact tested SHA.
- [ ] Verify deployment/runtime separately when required.

### Failures

- [ ] Identify the earliest failing boundary.
- [ ] Do not change another layer without evidence.
- [ ] Distinguish environment/harness failures from product failures.
- [ ] Preserve controlled provider and domain error semantics.

### Permissions

- [ ] Confirm authorization before staging or committing.
- [ ] Confirm authorization before pushing.
- [ ] Confirm authorization before workflows or deployment.
- [ ] Confirm authorization before AWS, secrets, or ECS desired-count changes.

### Complete

- [ ] Report the final outcome.
- [ ] Report verification evidence.
- [ ] Mark claims as VERIFIED, INFERRED, or UNVERIFIED.
- [ ] Disclose any remaining limitations.
- [ ] Claim “done” only within the agreed scope.

## Key Lessons

1. Inspect before editing.
2. Evidence beats plausibility.
3. Tests are contracts, not obstacles.
4. A clean design does not justify unnecessary abstraction.
5. The agent should stop when it cannot verify.
6. Human intervention should preserve valid work.
7. More agents are not automatically better.
8. Harness limitations constrain what the model can prove.
9. CI, deployment, and runtime health are different claims.
10. Permission to implement is not permission to publish or deploy.
11. Confidence should match the evidence available.
12. “Done” is a verified engineering state, not an agent declaration.

## Phase 17 Outcome

Phase 17 established a repeatable engineering workflow for using coding agents safely and effectively in DecisionAI.

The practical operating model is:

```text
SHAPE
→ INSPECT
→ PLAN
→ IMPLEMENT
→ VERIFY
→ CLASSIFY FAILURES
→ INTERVENE WHEN NEEDED
→ AUTHORIZE STATE CHANGES
→ REPORT EVIDENCE
```

The project can now move into Phase 18 with a stronger foundation for shaping ambiguous work, communicating technical trade-offs, and leading AI-assisted engineering execution.
