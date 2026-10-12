# ADR-006: Validate Evidence Inspection Before Expanding Analytics or Adding a Reviewer Agent

## Status

Proposed

## Context

DecisionAI's product specification identifies evidence inspection,
traceability, explicit limitations, and human review as requirements
for analyst decision support. The architecture likewise calls for
users to inspect supporting evidence before acting.

The current Streamlit UI displays the answer, execution counts, and
evidence observation numbers. The public API does not expose the
underlying observations or grounded claims, although the internal
agent result contains them. Analysts therefore cannot inspect
structured supporting evidence through the current interface.

**Hypothesis:** making a bounded set of evidence understandable and
inspectable may help analysts judge which conclusions to accept,
question, or investigate. Repository evaluations do not establish
this benefit, analyst demand, or usability.

## Decision

Prioritize discovery and validation of an evidence-inspection
experience for the existing revenue-comparison and
observed-deterioration workflow before expanding analytical
capabilities or adding a second reviewer agent.

The proposed experience would connect selected findings to
deterministic values, comparison periods, relevant contributor
evidence, and analytical limitations. It would distinguish
calculated facts from interpretation and investigation
recommendations.

**Approval boundary:** approval to create this proposed ADR authorizes
only recording the proposal. Approval of this ADR does not authorize
discovery execution, production implementation, deployment, or cloud
changes. The discovery exercise described below requires separate
human approval. Production implementation requires a further decision
based on discovery findings and a reviewed scope, including any
UI/API changes, persistence, or additional model calls.

This proposal supplements ADR-002 and ADR-005 without superseding them.

## Alternatives Considered

- **Expand analytical capabilities first.** Broader coverage may be
  valuable, but does not directly resolve inspection of existing
  conclusions.
- **Add a second reviewer agent.** Automated critique may help with
  measured reasoning failures, but introduces calls, latency, cost,
  and evaluation complexity. Its incremental value is unproven.
- **Retain the current answer and observation numbers.** Lowest
  effort, but leaves the structured evidence inaccessible through
  the interface.
- **Expose raw execution history.** Provides detail but risks
  unnecessary disclosure and cognitive load. Prefer a bounded,
  explicitly selected evidence view for validation.

## Evidence Supporting the Recommendation

**Verified repository evidence:**

- `docs/product-spec.md` includes an evidence-inspection user story,
  traceability requirements, human review, and communication of
  limitations. These are product intentions, not validated user
  outcomes.
- `docs/architecture.md`, sections 5.6-5.10, describes structured
  evidence, grounded interpretation, and human inspection.
- `app/api/contracts.py`, `app/api/service.py`, and
  `app/ui/streamlit_app.py` confirm that the public response and UI
  expose evidence step numbers without structured observations or
  grounded claims. `app/agent/contracts.py` retains those internally.
- `artifacts/phase11/revenue_decline_v1_qualitative_review.json`
  records an automated semantic pass alongside an unclear
  causal-language assessment and an unsuccessful qualitative review.
  Automated passing checks did not settle every interpretation
  concern.
- `artifacts/phase15/gemini/revenue_decline_v1_eval.json` records two
  quality-evaluated passes and one provider quota failure.
  `artifacts/phase15/gemini/revenue_comparison_only_v1_eval.json`
  records zero quality-evaluated runs because of quota exhaustion;
  `docs/PHASE_15_EVALUATION_SUMMARY.md` separately reports an earlier
  single-run pass.
- ADR-005 requires measured justification before introducing
  multi-agent complexity.

These findings support investigating evidence accessibility. They do
not prove that evidence inspection improves trust, reduces review
time, or outperforms a reviewer agent. The saved evaluations cover a
narrow workflow and are historical evidence, not fresh validation.
No analyst validation of the proposed experience has occurred.

## Consequences

Potential benefits to test include easier verification, clearer
separation of observation from inference, and more appropriately
calibrated reliance on recommendations. These are hypotheses, not
measured outcomes.

Costs and risks include discovery effort, delayed capability
expansion, additional reading burden, and a polished evidence view
creating unwarranted confidence. Inspection does not establish causal
correctness or guarantee that every narrative statement is supported.

Any later implementation may require a public evidence contract and
explicit provenance mapping. That design remains outside this approval.

## Privacy and Architecture Constraints

- Preserve the modular monolith and
  Streamlit -> HTTP -> FastAPI -> application-service boundary.
- Keep authoritative calculations in deterministic analytics code
  and provider SDK logic at the LLM boundary.
- Treat model-generated claims as interpretation requiring
  validation; an evidence reference alone does not prove correctness.
- Select only necessary evidence. Do not expose raw history,
  prompts, secrets, or unrestricted tool arguments and outputs.
- Preserve the prohibition on logging raw arguments, outputs,
  prompts, secrets, and unexpected exception text. Displaying
  approved evidence does not authorize logging it.
- Preserve controlled `ToolExecutionError` messages, sanitized
  unexpected ordinary failures, and propagation of
  `KeyboardInterrupt` and `SystemExit`.
- Use synthetic data for discovery. Any later real-data experience
  requires explicit access, disclosure, and retention decisions.
- Add no frameworks or dependencies.

## Smallest Reversible Validation Step

Subject to separate discovery approval, prepare a disposable static
prototype for one existing revenue-decline scenario using verified
synthetic tool outputs.

Compare the current answer presentation with a view showing:

- Comparison periods and deterministic revenue changes.
- Selected observed deterioration and its source reference.
- Interpretation and investigation priority separately.
- Explicit warnings about causality and overlapping dimensions.

Include a deliberately unsupported conclusion to test whether
participants challenge it. Label missing provenance or limitations
rather than inventing them.

Conduct a small moderated exercise with three intended analyst users,
subject to availability. This study is exploratory, not statistical
validation. Ask participants to locate supporting evidence, explain
what it establishes, identify the unsupported conclusion, and choose
what to investigate next. Record task outcomes and minimal anonymized
notes.

The prototype can be discarded without changing runtime behavior or
public contracts.

## Success and Failure Criteria

**Proposed discovery criteria, to agree before sessions:**

- At least two of three participants independently locate the
  supporting values and correct comparison periods.
- At least two distinguish observed deterioration from causality
  and recognize that contributions across overlapping dimensions
  cannot simply be added.
- At least two identify the unsupported conclusion.
- Compared with the current presentation, evidence inspection
  improves task correctness or reduces assistance needed, without
  increasing unsupported acceptance.
- No private payloads are exposed or logged.

Failure includes inability to find or interpret evidence, increased
unsupported confidence, no observable task benefit, or a need for
substantially broader functionality to complete the bounded task.

Insufficient participants or mixed findings are inconclusive. These
thresholds are exploratory decision aids, not statistical evidence of
effectiveness. This small exercise can justify a scoped next
experiment; it cannot establish general analyst validation or
production readiness.

## Revisit When

- Discovery indicates that evidence inspection is unhelpful or that
  missing analytical capability is the primary obstacle.
- Broader evaluations reveal persistent planning, evidence-coverage,
  or interpretation failures.
- A reviewer agent demonstrates measurable improvement over the
  simpler baseline, with acceptable cost, latency, and failure
  behavior.
- Real-data access, provenance, retention, or multi-user requirements
  change the feasible scope.

## Open Questions

- Which intended analysts can participate, and who owns the
  discovery decision?
- What evidence granularity helps users verify conclusions without
  overwhelming them?
- How should narrative findings map to grounded claims and
  deterministic outputs?
- Which provenance and limitations are currently available, and
  which are missing?
- What access and retention controls would a production evidence
  view require?
- What larger validation would justify implementation and release?
