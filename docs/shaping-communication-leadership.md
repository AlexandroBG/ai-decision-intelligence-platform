# Phase 18 — Shaping, Communication & Technical Leadership

## Overview

Phase 18 developed the technical leadership skills needed to convert ambiguous product requests into evidence-based decisions, bounded plans, stakeholder communications, and explicit risk and release gates. The exercises were grounded in DecisionAI, a revenue-focused AI decision intelligence platform.

**Phase outcome:** Exercises 18.1–18.8 completed. A **CONDITIONAL GO** was recommended for entering **Phase 19 — Portfolio Release preparation**, not for public production use or automatic publication.

## Core principles

1. Define user outcomes before selecting features.
2. Distinguish **VERIFIED**, **INFERRED**, and **UNVERIFIED** claims.
3. Compare alternatives with common criteria and defend a recommendation.
4. Document decisions and the limits of their authorization.
5. Communicate the same facts appropriately to technical and business audiences.
6. Prioritize and delegate bounded, reversible work with human approval gates.
7. Track residual risks, owners, and escalation triggers.
8. Make release claims only at the level supported by fresh evidence.

---

## 18.1 — Problem Shaping

**Ambiguous request:** “Make DecisionAI better for business analysts.”

The exercise identified the primary intended user (Business Analyst), the revenue-investigation workflow, and three possible interpretations of “better”:

| Interpretation | Potential value | Principal limitation |
|---|---|---|
| Easier analysis requests | Less request/setup friction | Does not solve evidence verification |
| Easier verification | Better inspection of revenue numbers, contributor signals, and limitations | Can overwhelm users or create false reassurance |
| More analytical questions | Broader coverage | Expands data, contracts, tests, and evaluation scope |

**Recommended narrow problem hypothesis:** Help analysts verify a revenue comparison and its largest observed deteriorations so they can defend a next investigation step.

**Repository evidence:** Structured tool observations and grounded claims exist inside agent results; the public API/UI primarily present answers, counters, and evidence step numbers. **Unverified:** whether this is the most important analyst problem. No user study occurred.

**Non-goals:** Causal attribution, forecasting, autonomous actions, unrestricted ingestion, general dashboard redesign, provider migration, or multi-agent expansion.

**Lesson:** Shape the problem as an outcome and identify unknowns before prescribing a feature.

## 18.2 — Trade-off Framing & Decision Communication

**Decision considered:** How to improve analyst trust in revenue investigations.

| Option | Case for it | Trade-off | Recommendation |
|---|---|---|---|
| **A. Bounded evidence inspection** | Addresses a visible interface gap using existing deterministic evidence | UI/API projection, privacy review, cognitive load | **Investigate first** |
| **B. More tools and metrics** | Could address currently unsupported questions | Increased calculation, tooling, and evaluation surface | Defer until specific unmet needs are shown |
| **C. Second reviewer agent** | Might detect interpretation errors | Extra provider calls, latency, quotas, correlated errors, adjudication | Defer until comparative evaluation justifies it |

The recommended reversible next step was a disposable evidence prototype using verified synthetic outputs and a small formative analyst exercise—not immediate production implementation.

**Revisit the decision if:** analyst sessions reveal missing analytics as the primary bottleneck; inspection increases unsupported confidence; or a bounded reviewer proves measurable improvement over simpler controls.

**Lesson:** Recommend one option, explain rejected alternatives, and define what evidence would change the recommendation.

## 18.3 — Decision Records

**Document:** `docs/decisions/ADR-006-validate-evidence-inspection-before-expansion.md`
**Published commit:** `30f9196` — `Document proposed evidence inspection decision`
**ADR status:** **Proposed**

ADR-006 records context, alternative options, repository evidence, consequences, privacy and architecture boundaries, a reversible discovery proposal, exploratory success criteria, open questions, and revisit conditions.

**Authorization boundary:** Creating and publishing the ADR records a proposal. It does **not** authorize analyst discovery, production UI/API changes, additional model calls, Git publication of future work, deployment, cloud activation, or spending. The proposed three-person discovery study is formative, **not statistical validation**.

**Lesson:** An ADR is a record of reasoning, uncertainty, and decision rights—not an automatic implementation order.

## 18.4 — Stakeholder Communication

The same ADR-006 recommendation was communicated in two forms:

- **Engineering Lead:** Focus on Streamlit → HTTP → FastAPI → application-service architecture, bounded evidence contracts, deterministic calculations, provenance, tool failure semantics, privacy, tests, and approval gates.
- **Business Stakeholder:** Focus on the analyst's difficulty checking findings, potential benefit, effort, false-confidence risk, limitations, and the exact decision requested.

Both versions maintained unchanged facts: ADR-006 is Proposed; benefits are hypotheses; no analyst validation occurred; discovery and implementation each require separate approval.

**Lesson:** Adjust the explanation to the audience without changing facts or inflating confidence.

## 18.5 — Prioritization & Sequencing

A repository-grounded product-learning sequence was recommended:

| Rank | Initiative | Why now or later |
|---|---|---|
| 1 | **A. Analyst evidence discovery** | Tests an important product hypothesis before building |
| 2 | **B. Expand revenue evaluation coverage** | Strengthens evidence for current supported workflows |
| 3 | **C. Runtime/demo verification** | Needed before claiming an external demonstration works |
| 4 | **D. Additional analytical tools** | Wait for a validated missing capability |
| 5 | **E. Reviewer agent** | Wait for measured value over simpler orchestration |

**Context changes the order:** If a technical demo is imminent, C can move ahead of A and B. This reordering is justified by a different near-term goal rather than a contradiction.

**Lesson:** Prioritization means specifying what comes next, what waits, and what new evidence changes the sequence.

## 18.6 — Execution Planning & Delegation

The initiative selected for planning was a small extension of revenue-investigation evaluation coverage.

| Milestone | Deliverable | Authorization |
|---|---|---|
| **M1 — Specify** | Candidate question, tool expectations, numeric ground truth, coverage inventory, missing test proposal | **Completed read-only** |
| **M2 — Implement** | One additional versioned case and a bounded offline integration regression | **Not authorized** |
| **M3 — Verify** | Focused/related tests, Ruff, pytest, diff/status review, evidence report | Conditional on M2 approval |

### M1 result

**Proposed ID:** `revenue_investigation_observed_deterioration_v1`

**Proposed question:**

> How did total revenue change between July 2025 and August 2025? Identify the largest observed deteriorations and recommend what to investigate first.

The specification reused existing requirements for `analyze_revenue`, `analyze_revenue_drivers`, optional `detect_revenue_anomalies`, and a recommendation. Codex reported a separate raw-CSV calculation using Python's standard library and `Decimal`:

| Metric | Reported independent value |
|---|---:|
| July 2025 revenue | 1,773,419.930216 |
| August 2025 revenue | 1,275,769.945404 |
| Absolute change | -497,649.984812 |
| Percentage change | Approximately -28.06% |

The separate calculation supported the observed **Computing** deterioration and avoided treating overlapping dimensions as additive explanations. These were **Codex-reported checks**, not a fresh independent recalculation for this document.

M1 also found that premature-final recovery and numeric rejection already had coverage. The proposed implementation was reduced to **one new phrasing case and one offline integration test** rather than duplicate scenarios.

**Evidence boundary:** Scripted offline orchestration can verify integration of the existing components; it cannot establish that a live LLM interprets a new phrasing accurately or reliably. Registering a case may expand future live evaluation cost.

**Lesson:** Delegate a specification first, reduce redundant implementation, and retain human control over business relevance, test scope, provider spend, and publication.

## 18.7 — Risk Management & Engineering Escalation

The read-only risk exercise considered analyst usability, answer quality, provider quotas, provenance, privacy, CI/deployment, runtime/cost, evaluation evidence, observability, and coding-agent permissions.

### Highest-attention risks

| Risk | Current evidence or controls | Proportionate response |
|---|---|---|
| Analyst cannot inspect evidence | Interface gap confirmed; impact on actual analysts unknown | Seek separate approval for synthetic discovery |
| Unsupported interpretation | Deterministic tools and grounding checks exist, but references do not prove narrative correctness | Justified qualitative/claim-to-evidence regression cases |
| Overstated evaluation reliability | Two registered business cases; limited historical live runs | Report requested/attempted/evaluated/passed counts honestly |
| Provider interruption | Historical quota failures; 429 deliberately not retried | Bounded rehearsal and clearly labeled fallback |
| Demo runtime/cost | Deployment configuration exists; current AWS readiness unverified; ECS may intentionally be stopped | Authorized preflight, cost boundary, runtime verification, shutdown owner |

**Security boundary:** A controlled synthetic portfolio demo is different from unrestricted public use or real business data. Public operation would require reviewed access/abuse controls, transport, data governance, spending, and monitoring.

**Calibration correction:** The technical evidence-inspection gap is confirmed; its *frequency or magnitude of harm to analysts* is not established. Do not confuse certainty about an implementation gap with certainty about user impact.

**Lesson:** Record risk cause, possible consequence, supporting evidence, early warning, owner, mitigation, residual risk, and escalation condition.

## 18.8 — Technical Leadership Review

**Readiness decision:** **CONDITIONAL GO to Phase 19 — Portfolio Release preparation**.

### Demonstrable engineering foundations

- Deterministic revenue analytics and observed-deterioration analysis.
- ML/statistical anomaly detection.
- Gemini/OpenAI integration boundaries, without assumed automatic failover.
- Bounded single-agent tool orchestration and internal evidence references.
- Numeric, semantic, and qualitative evaluation machinery.
- FastAPI + Streamlit application layers.
- Privacy-aware logging/error handling and tests.
- Dependency locks, Docker/CI configuration, OIDC, tested-SHA deployment configuration, and ECS desired-count preservation.
- Coding-agent task shaping, evidence discipline, review, and permission practices.

### Limits not to overclaim

- No validated analyst productivity, trust benefit, or adoption.
- No demonstrated causal root-cause discovery or broad reliability.
- Limited registered business evaluation cases and small historical live samples.
- Narrative correctness not guaranteed by evidence IDs or phrase-based checks.
- Full analyst-facing evidence inspection remains a proposal.
- Fresh Ruff/pytest did not complete in the Codex readiness session due to interpreter environment problems.
- Current GitHub CI/Deploy run success, AWS runtime health, secrets, provider availability, and cloud spending were not verified in that review.
- Public production authentication, abuse controls, monitoring, and operational readiness were not demonstrated.
- README/documentation reconciliation and licensing review were identified as portfolio-release tasks.

### Conditions for Phase 19 publication

1. Agree the supported demo scope and claims.
2. Obtain fresh lint/tests and exact-release-SHA CI evidence.
3. Verify a reproducible **synthetic** demonstration and review answer/evidence alignment.
4. Update README, limitations, historical results, screenshots/recording, and license/publication details.
5. Review public artifacts for secrets and unintended disclosure.
6. Obtain explicit human approval before publishing.
7. If AWS runtime is included, separately authorize budget/window, startup, verification, and shutdown.

**Not approved:** Unrestricted public production use, automatic ECS scaling, paid provider evaluations, ADR-006 discovery, or any subsequent feature implementation merely by entering Phase 19.

---

## Reusable Technical Leadership Operating Model

```text
SHAPE USER PROBLEM
→ INSPECT CURRENT REALITY
→ SEPARATE EVIDENCE FROM INFERENCE
→ COMPARE OPTIONS AND TRADE-OFFS
→ RECORD A REVISABLE DECISION
→ COMMUNICATE TO THE AUDIENCE
→ PRIORITIZE WORK
→ DELEGATE BOUNDED MILESTONES
→ MANAGE RISK AND PERMISSIONS
→ VERIFY CLAIMS
→ MAKE AN EXPLICIT READINESS DECISION
```

## Reusable Checklist

### Shape and decide

- [ ] Name the user, workflow, problem, and measurable outcome.
- [ ] Separate verified implementation facts from unvalidated benefits.
- [ ] Compare alternatives and document non-goals.
- [ ] Explain why the recommended option wins and when to reconsider.
- [ ] Record approval boundaries in an ADR or decision memo.

### Communicate and sequence

- [ ] Match vocabulary to the stakeholder while preserving facts.
- [ ] End with one explicit decision request.
- [ ] Prioritize by evidence, value, effort, risk, dependencies, and reversibility.
- [ ] Define triggers for reprioritization.

### Delegate and manage risk

- [ ] Break work into reviewable milestones and acceptance criteria.
- [ ] Check existing coverage before ordering new tests or abstractions.
- [ ] Keep implementation, live evaluation, cloud operations, and Git publication separately authorized.
- [ ] Assign risk owners and escalation conditions.
- [ ] Preserve privacy, deterministic authority, OIDC, exact tested-SHA deployment, and ECS cost controls.

### Validate release claims

- [ ] Report VERIFIED / INFERRED / UNVERIFIED evidence.
- [ ] Run appropriate focused/full tests, Ruff, and diff review for authorized changes.
- [ ] Tie CI and deployment evidence to the exact SHA.
- [ ] Distinguish configured deployment from live runtime health.
- [ ] Separate portfolio demonstration from public production readiness.
- [ ] Obtain human publication approval.

---

## Phase 18 Closure and Transition

**Phase 18 exercises 18.1–18.8:** Completed as planning, leadership, and communication exercises.

**Repository decision recorded:** ADR-006, status **Proposed**, published in commit `30f9196`.

**Prepared but not executed:** ADR-006 analyst discovery; evaluation expansion M2/M3; new UI evidence feature; paid provider evaluation; cloud demo activation; unrestricted production launch.

**Next phase:** **Phase 19 — Portfolio Release preparation**, under a **CONDITIONAL GO**. Its publication gates are fresh validation evidence, a repeatable synthetic demo, accurate documentation and limitations, privacy/licensing review, and human approval.

This document records historical learning and decisions. It does not itself authorize changes to the repository, workflows, providers, cloud, or publication state.
