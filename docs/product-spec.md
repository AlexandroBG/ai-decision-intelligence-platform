# DecisionAI - Product Specification

## 1. Product Overview

DecisionAI is an AI-powered decision intelligence platform that combines structured business data, deterministic analytics, machine learning, and controlled AI workflows to turn raw data into evidence-backed decisions.

The initial MVP focuses on revenue-performance investigation rather than broad autonomous business decision-making.

Core product question:

> What is affecting revenue performance, and what should I investigate first?

The product should support analysts by combining reproducible calculations with AI-assisted interpretation while preserving human review for important conclusions.

## 2. Target User

### Primary User

The primary user is a Business Analyst who needs to investigate business-performance changes efficiently.

The analyst should be able to:

- Load or select supported structured datasets.
- Ask supported revenue-performance questions.
- Inspect calculated metrics.
- Review major observed contributors.
- Understand the evidence supporting the analysis.
- Receive AI-assisted interpretation.
- Decide what deserves further investigation.

### Secondary User

A secondary user is an Operations Manager or business stakeholder who needs a concise, evidence-backed explanation of what changed and what should be investigated.

## 3. User Problem

Business users frequently have access to structured data but still spend significant time:

- Preparing datasets.
- Calculating KPIs.
- Comparing periods.
- Segmenting results.
- Identifying relevant contributors.
- Converting numerical findings into understandable explanations.
- Verifying whether an AI-generated answer is actually supported by evidence.

General-purpose LLMs can produce plausible explanations but may invent numbers, misinterpret business data, or overstate causality.

DecisionAI should reduce time-to-insight while preserving deterministic evidence and explicit analytical limitations.

## 4. Business Context

The initial product assumes a business with transaction, customer, and product data.

The MVP should support questions related to revenue performance across dimensions such as:

- Time period.
- Region.
- Customer segment.
- Product.
- Product category.
- Sales channel.
- Discount behavior.

The initial environment uses synthetic business data so that expected patterns can be controlled and evaluated.

## 5. Core Question

The MVP should primarily answer:

> What is affecting revenue performance, and what should I investigate first?

The system should decompose this into analytical subquestions such as:

- Did revenue increase or decrease?
- By how much?
- Which dimensions contributed most to the change?
- Which contributors deserve investigation?
- What evidence supports each finding?
- What limitations prevent stronger conclusions?

## 6. Value Proposition

DecisionAI should help analysts move from raw data to structured investigation more quickly.

The product should provide:

- Reproducible calculations.
- Evidence-backed contributor analysis.
- Clear analytical explanations.
- Controlled AI interpretation.
- Explicit limitations.
- Human-review support.
- A repeatable evaluation framework for system quality.

The objective is not to automate every business decision.

The objective is to improve analytical productivity and consistency while preserving human judgment.

## 7. User Stories

### US-001

As a Business Analyst, I want to load supported business datasets so that I can analyze revenue performance.

### US-002

As a Business Analyst, I want DecisionAI to validate my data before analysis so that I do not rely on invalid results.

### US-003

As a Business Analyst, I want to compare revenue between two periods so that I can understand performance changes.

### US-004

As a Business Analyst, I want to see the absolute and percentage revenue change so that I can quantify the performance difference.

### US-005

As a Business Analyst, I want to identify the dimensions that contributed most to the change so that I know where to investigate.

### US-006

As a Business Analyst, I want to inspect supporting evidence so that I can verify the system's conclusions.

### US-007

As a Business Analyst, I want to ask supported questions in natural language so that I do not need to manually select every analytical operation.

### US-008

As a Business Analyst, I want AI-assisted interpretation grounded in calculated evidence so that results are easier to understand.

### US-009

As a Business Analyst, I want the system to communicate limitations and uncertainty so that I do not confuse observed contribution with causality.

### US-010

As a stakeholder, I want a concise summary of what changed and what deserves investigation so that I can act on the analysis efficiently.

## 8. MVP Scope

The MVP includes:

- Supported CSV ingestion.
- Data validation.
- Revenue calculation.
- Period comparison.
- Order-volume analysis.
- Average-order-value analysis.
- Dimensional aggregation.
- Contributor analysis.
- Contributor ranking.
- Evidence generation.
- Natural-language analytical requests.
- AI-assisted interpretation grounded in deterministic evidence.
- Evaluation of deterministic and AI behavior.
- Human review.
- Basic persistence where justified.
- Basic observability.

The MVP should remain focused on revenue-performance investigation.

## 9. Functional Requirements

### Data Ingestion and Validation

**FR-001** DecisionAI shall load supported transaction data from `orders.csv`.

**FR-002** DecisionAI shall load supported customer data from `customers.csv`.

**FR-003** DecisionAI shall load supported product data from `products.csv`.

**FR-004** DecisionAI shall verify required columns before analytical execution.

**FR-005** DecisionAI shall validate supported data types and required values.

**FR-006** DecisionAI shall detect duplicate primary identifiers where uniqueness is required.

**FR-007** DecisionAI shall validate supported business rules such as quantity, price, discount, and date constraints.

**FR-008** DecisionAI shall validate customer and product references used by orders.

### Deterministic Analytics

**FR-009** DecisionAI shall calculate revenue using deterministic code.

**FR-010** DecisionAI shall support comparison between a baseline period and a comparison period.

**FR-011** DecisionAI shall calculate absolute revenue change.

**FR-012** DecisionAI shall calculate percentage revenue change when the baseline supports a meaningful percentage comparison.

**FR-013** DecisionAI shall calculate order volume for supported periods.

**FR-014** DecisionAI shall calculate average order value using a documented definition.

**FR-015** DecisionAI shall aggregate revenue by supported analytical dimensions.

**FR-016** DecisionAI shall calculate observed contribution to revenue change by supported dimensions.

**FR-017** DecisionAI shall rank major observed contributors using deterministic evidence.

**FR-018** Contributor outputs shall avoid presenting association or contribution as established causality.

### Natural Language and AI Interpretation

**FR-019** DecisionAI shall accept supported analytical questions expressed in natural language.

**FR-020** DecisionAI shall map supported questions to controlled analytical capabilities.

**FR-021** DecisionAI shall provide AI interpretation using structured analytical evidence rather than relying on the model to recreate authoritative calculations.

**FR-022** AI-generated application output shall be validated against required output structure.

**FR-023** DecisionAI shall detect or prevent unsupported numerical claims where practical.

**FR-024** DecisionAI shall communicate important analytical limitations and uncertainty.

### Final Output and Human Control

**FR-025** DecisionAI shall provide a final response containing deterministic findings, evidence, major contributors, interpretation, and limitations where available.

**FR-026** DecisionAI shall preserve human review before important business decisions or high-impact external actions.

## 10. Non-Functional Requirements

**NFR-001 Reliability:** Deterministic calculations should be reproducible for the same validated input.

**NFR-002 Testability:** Core analytical capabilities should be testable without requiring UI, network, or live AI-provider access.

**NFR-003 Traceability:** Important conclusions should be traceable to structured analytical evidence.

**NFR-004 Graceful Degradation:** If optional AI interpretation fails after successful deterministic analysis, the system should be able to return reliable analytical evidence with an explicit notice.

**NFR-005 Explicit Failure:** Critical data or analytical failures should not be silently ignored.

**NFR-006 Separation of Concerns:** Presentation, analytics, AI integration, persistence, and evaluation responsibilities should remain separated.

**NFR-007 Replaceability:** External AI-provider integration should be isolated enough to permit future evolution when justified.

**NFR-008 Security:** Secrets must not be committed to source control or exposed unnecessarily.

**NFR-009 Least Privilege:** Components should receive only the capabilities and permissions required for their responsibilities.

**NFR-010 Input Validation:** User input, datasets, AI output, and tool requests should be validated at relevant trust boundaries.

**NFR-011 Observability:** Important workflow steps, failures, latency, model usage, and tool activity should become observable where practical.

**NFR-012 Evaluation:** AI behavior should be measurable using versioned evaluation cases.

**NFR-013 Regression Protection:** Important discovered failures should become tests or evaluation cases when practical.

**NFR-014 Maintainability:** The initial architecture should favor clear modules and limited coupling over speculative complexity.

**NFR-015 Simplicity:** The MVP should avoid distributed infrastructure or agentic complexity unless requirements or measured evidence justify it.

**NFR-016 Cost Awareness:** AI-model usage should be designed with token usage, latency, and cost in mind.

**NFR-017 Performance:** Interactive MVP operations should complete within reasonable analyst-facing latency for supported local datasets.

**NFR-018 Privacy:** The system should minimize unnecessary exposure, logging, or persistence of business data.

**NFR-019 Human Review:** Important findings and recommendations should remain reviewable by a human.

**NFR-020 Documentation:** Product behavior, analytical definitions, limitations, and important architectural decisions should be documented.

## 11. Input Data

The initial MVP uses three structured datasets.

### `orders.csv`

Required fields:

- `order_id`
- `customer_id`
- `product_id`
- `order_date`
- `quantity`
- `unit_price`
- `discount`
- `sales_channel`

### `customers.csv`

Required fields:

- `customer_id`
- `signup_date`
- `segment`
- `region`
- `acquisition_channel`

### `products.csv`

Required fields:

- `product_id`
- `product_name`
- `category`
- `unit_cost`

An optional future dataset may include marketing or acquisition-spend information if justified by a later product question.

## 12. Expected Output

A successful analysis should be capable of producing:

### Deterministic Summary

- Baseline revenue.
- Comparison-period revenue.
- Absolute change.
- Percentage change where meaningful.
- Order volume.
- Average order value.

### Contributor Analysis

- Supported analytical dimension.
- Dimension value.
- Baseline metric.
- Comparison metric.
- Absolute contribution or change.
- Contributor ranking.

### Evidence

The final result should expose enough structured evidence for a user or evaluation workflow to inspect the basis of the conclusion.

### AI Interpretation

AI-assisted output may include:

- Concise summary.
- Important investigation priorities.
- Explanation of observed evidence.
- Limitations.
- Uncertainty notes.

### Final Response

The final response should clearly separate calculated facts from AI-assisted interpretation.

## 13. Success Metrics

Product success should be evaluated using measurable hypotheses rather than only subjective impressions.

Potential metrics include:

- Numerical correctness of deterministic analytics.
- Percentage of evaluation cases with correct major contributor identification.
- Rate of unsupported numerical claims in AI output.
- Rate of unsupported causal claims.
- Human usefulness ratings.
- Time required to answer the core analytical question.
- Latency per analysis.
- AI-model cost per analysis.
- Regression failure rate.
- Percentage of results with traceable supporting evidence.

Initial targets may evolve after baseline measurements exist.

## 14. Evaluation Strategy

DecisionAI should use evaluation-driven development.

The evaluation strategy should combine:

### Deterministic Evaluation

Use exact or tolerance-based comparisons for:

- Revenue calculations.
- KPI changes.
- Aggregations.
- Contributor values.
- Validation outcomes.
- Structured contracts.

### AI Behavioral Evaluation

Evaluate:

- Consistency with evidence.
- Unsupported numerical claims.
- Unsupported causal claims.
- Relevance.
- Investigation prioritization.
- Clarity.
- Appropriate limitations.

### LLM-as-a-Judge

Model-based evaluation may be used for qualitative criteria that are difficult to score deterministically.

LLM judges should be periodically calibrated against human review.

### Human Evaluation

Human reviewers may assess:

- Usefulness.
- Clarity.
- Trustworthiness.
- Relevance.
- Investigation quality.

### Versioned Evaluation Dataset

Evaluation cases should be reproducible and version controlled.

Important discovered failures should become regression cases.

## 15. Risks

### Hallucination Risk

The AI model may produce unsupported claims or numbers.

Mitigation:

- Ground interpretation in structured evidence.
- Validate structured output.
- Use deterministic calculations as the numerical source of truth.
- Add regression cases for discovered failures.

### Numerical Error Risk

Incorrect calculations could mislead users.

Mitigation:

- Deterministic implementation.
- Unit tests.
- Controlled evaluation datasets.

### Data-Quality Risk

Invalid or incomplete data may create unreliable analysis.

Mitigation:

- Schema validation.
- Business-rule validation.
- Referential-integrity checks.
- Explicit errors and warnings.

### Causality Risk

Observed contributors may be interpreted incorrectly as causal effects.

Mitigation:

- Use contribution and association language.
- Communicate limitations.
- Avoid causal claims without appropriate causal methodology.

### Prompt-Injection and Tool-Misuse Risk

Untrusted content may attempt to influence AI behavior or trigger unsafe actions.

Mitigation:

- Separate instructions from data.
- Tool allowlists.
- Argument validation.
- Least privilege.
- No unrestricted shell or database execution.

### External-Service Risk

AI providers may fail, change behavior, or become unavailable.

Mitigation:

- Provider isolation.
- Error classification.
- Timeouts and selective retries.
- Graceful degradation when reliable deterministic results remain.

### Cost and Latency Risk

Uncontrolled AI workflows may become slow or expensive.

Mitigation:

- Measure token usage and latency.
- Prefer minimal useful context.
- Add complexity only when evaluation demonstrates value.

### Privacy Risk

Business data may contain sensitive information.

Mitigation:

- Data minimization.
- Secret isolation.
- Controlled logging.
- Avoid unnecessary persistence.

### Overautomation Risk

Users may over-trust AI recommendations.

Mitigation:

- Human review.
- Evidence visibility.
- Explicit limitations.
- Decision-support positioning.

### Scope-Creep Risk

The project may expand into unrelated AI or enterprise capabilities.

Mitigation:

- Keep the MVP focused on the core revenue-performance question.
- Use explicit out-of-scope boundaries.
- Require evidence before adding architectural complexity.

## 16. Constraints

The initial project has the following constraints:

- Revenue-performance analysis is the MVP focus.
- Initial data is synthetic.
- Python is the primary implementation language.
- Gemini is the initial AI provider.
- Gemini-specific behavior should remain isolated behind an AI boundary.
- Development should remain budget conscious.
- The initial environment is Windows with PowerShell, VS Code, Git, and GitHub.
- The project is developed by one human engineer with AI assistance.
- The project is intentionally learning-oriented and should expose engineering reasoning rather than hiding it behind excessive automation.
- The initial deployment should avoid unnecessary distributed infrastructure.
- Multi-agent behavior is not required for the initial MVP.

## 17. Security and Privacy

DecisionAI should treat the following as untrusted until validated:

- User input.
- Uploaded or imported datasets.
- AI-model output.
- AI-generated tool requests.
- Future external integrations.

Security principles include:

- Least privilege.
- Explicit validation.
- Secrets outside source control.
- Tool allowlists.
- No unrestricted OS execution from the model.
- Controlled database access.
- Controlled filesystem access.
- Parameterized database queries where relevant.
- Sensitive-log minimization.
- Human control over high-impact actions.

Real sensitive business data should not be introduced until appropriate retention, deletion, governance, and access policies exist.

## 18. Out of Scope

The initial MVP does not include:

- Autonomous external business actions.
- Autonomous purchasing, pricing, staffing, or financial decisions.
- Advanced causal inference.
- Enterprise-grade identity and access management.
- Kubernetes.
- Distributed microservices.
- Complex multi-agent systems without demonstrated need.
- Fine-tuning foundation models.
- Large RAG infrastructure without a defined requirement.
- Voice interfaces.
- General computer-use automation.
- Arbitrary business domains.
- Advanced churn modeling as a core MVP capability.
- Advanced forecasting as a core MVP capability.
- Direct integrations with CRM, ERP, data warehouses, messaging, or external action systems.

These capabilities may be reconsidered only when product or evaluation evidence justifies them.

## 19. Trade-offs

### Simplicity vs Capacity

The MVP favors simple local architecture over maximum production scale.

### Deterministic Logic vs LLM Flexibility

Deterministic code is preferred for exact calculations.

LLMs are preferred for language understanding, orchestration, and interpretation where their flexibility adds value.

### Single Workflow vs Multi-Agent

The initial design favors simple orchestration.

Multi-agent systems should require measured evidence that simpler approaches are insufficient.

### SQLite vs PostgreSQL

SQLite reduces operational complexity for the local MVP.

PostgreSQL may become appropriate if concurrency, deployment, or production requirements justify it.

### Quality vs Cost vs Latency

AI-model changes should be evaluated across all three dimensions rather than optimizing only output quality.

### Raw Context vs Structured Evidence

The system should prefer the minimum useful structured evidence over sending large raw datasets to the model.

### Development Speed vs Production Hardening

The MVP should move incrementally while preserving important boundaries, tests, and security practices.

### Autonomy vs Human Control

DecisionAI favors decision support and evidence over autonomous high-impact actions.

### Breadth vs Evaluation Depth

The initial product should support fewer capabilities with strong evaluation rather than many weakly tested features.

## 20. User Feedback Plan

User feedback should be collected through several mechanisms.

### Interviews

Talk with target users about:

- Current revenue-analysis workflow.
- Main sources of analytical friction.
- Trust requirements.
- Evidence requirements.
- Preferred output format.

### Task-Based Testing

Ask users to perform defined analytical tasks using DecisionAI and observe:

- Time to insight.
- Confusion points.
- Missing information.
- Trust behavior.

### Manual vs DecisionAI Comparison

Compare:

- Time required.
- Findings identified.
- Evidence quality.
- User confidence.

### Output Feedback

Collect explicit feedback such as:

- Useful / not useful.
- Correct / questionable.
- Missing evidence.
- Too verbose / too brief.
- Wrong investigation priority.

### Behavioral Signals

Future signals may include:

- Which findings users inspect.
- Which investigation priorities they accept or reject.
- Whether users request additional evidence.
- Whether they repeat analyses.

### Feedback Prioritization

Feedback should be prioritized according to:

- Frequency.
- User impact.
- Product alignment.
- Implementation effort.
- Reliability or security risk.
- Supporting evidence.

## 21. Business Value

Potential business value should be treated as a hypothesis to validate.

Candidate benefits include:

- Reduced analyst time spent on repetitive KPI investigation.
- Faster time-to-insight.
- More consistent analytical workflows.
- Better traceability of AI-assisted conclusions.
- Better reuse of analytical knowledge.
- Reduced dependence on ad-hoc manual analysis.

Potential costs include:

- AI-model usage.
- Engineering and maintenance.
- Evaluation.
- Infrastructure.
- Data preparation.
- Human review.

Future unit-economics analysis may consider:

- Cost per analysis.
- Analyst time saved.
- AI cost per successful analytical task.
- Infrastructure cost.
- User adoption and repeated usage.

Business-value claims should be validated with actual user behavior and measured outcomes.

## 22. MVP Acceptance Criteria

The MVP should not be considered complete merely because a UI can produce an answer.

### Data

- Supported datasets can be loaded.
- Required schemas are validated.
- Important business rules are validated.
- Referential-integrity errors are detected.
- Invalid required data prevents unreliable analysis.

### Deterministic Analytics

- Revenue is calculated from documented inputs.
- Baseline and comparison periods can be compared.
- Absolute and percentage changes are produced correctly.
- Supported dimensional aggregations are reproducible.
- Contributor analysis is deterministic and tested.

### Core Question

The system can produce an evidence-backed response to:

> What is affecting revenue performance, and what should I investigate first?

### Evidence

- Important findings are traceable to structured evidence.
- Contributor values are available for inspection.
- Warnings and limitations are preserved.

### AI Behavior

- AI interpretation is grounded in deterministic evidence.
- Gemini is not the numerical source of truth.
- AI output follows a structured contract where practical.
- Unsupported numerical and causal claims are evaluated.

### Evaluation

- A versioned evaluation dataset exists.
- Deterministic evaluation cases exist.
- AI behavioral evaluation exists.
- Important regressions can be detected.

### Security

- Real secrets are not committed to Git.
- Tool access is controlled.
- Untrusted inputs cross validation boundaries.
- AI output is not blindly trusted.

### Observability

- Important workflow failures are visible.
- AI-model calls can be measured where practical.
- Latency and relevant usage metadata can be inspected.

### Documentation

- Product behavior is documented.
- Data definitions are documented.
- Architecture is documented.
- Important decisions are documented using ADRs.

### Human Review

- Final outputs preserve human responsibility for important decisions.
- The system does not autonomously execute high-impact business actions.

## 23. Open Questions

The following questions remain intentionally open until implementation or evaluation produces enough evidence.

### Product

- Which exact response format is most useful to analysts?
- How much explanation should the default response include?
- Which supported analytical questions should be added after the core revenue question?

### Data

- What dataset size should define the initial supported local operating range?
- Which missing-value behaviors should be warnings versus errors?
- Which real-world data-quality issues should be simulated after the clean baseline is stable?

### Analytics

- What exact contributor methodology should be used for the first implementation?
- How should contribution be normalized or ranked across dimensions?
- How should zero-baseline percentage changes be communicated?
- Which dimensions should be supported in the first release?

### AI

- Which Gemini model configuration provides the best quality, latency, and cost trade-off?
- What structured-output contract should the first interpreter use?
- Which AI tasks should remain outside the MVP?

### Grounding

- How much evidence is necessary for reliable interpretation?
- Should raw rows ever be provided to the model, or only aggregated evidence?
- Which context-selection strategy performs best in evaluation?

### Tools and Agents

- Which deterministic capabilities should become AI-callable tools?
- When does dynamic tool selection outperform deterministic orchestration?
- Does a critic or reviewer agent provide measurable value?
- Does multi-agent coordination justify its additional cost and complexity?

### Evaluation

- What minimum number of evaluation cases is required for the first meaningful baseline?
- Which evaluation dimensions can be scored deterministically?
- Which dimensions require LLM-as-a-judge?
- How often should human calibration be performed?
- What failure rate is acceptable for release?

### System

- When should persistence move from SQLite to PostgreSQL?
- When should asynchronous execution be introduced?
- What observability tooling is justified after local development?
- What production deployment target should be used first?

### Business

- How much analyst time does DecisionAI actually save?
- Which findings are most valuable to users?
- What usage pattern would justify continued investment?
- What unit economics would support production deployment?

Open questions should be resolved through implementation evidence, evaluation results, user feedback, or operational requirements rather than speculation.
