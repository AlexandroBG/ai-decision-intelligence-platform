# DecisionAI - Software Architecture

## 1. Architecture Goals

DecisionAI should use an architecture that supports reliable analytical behavior, systematic evaluation, incremental development, and clear separation between deterministic computation and probabilistic AI behavior.

The initial architecture should remain simple enough for an MVP while establishing boundaries that allow the system to evolve as new requirements are validated.

### AG-001 - Separation of Concerns

The system should separate major responsibilities including:

- User interaction.
- API handling.
- Application orchestration.
- Data access and validation.
- Deterministic analytics.
- Machine learning.
- AI-model integration.
- Tool execution.
- Evaluation.
- Observability.
- Persistence.

Business and analytical logic should not be embedded directly inside the user-interface or transport layers.

### AG-002 - Deterministic Analytical Core

Calculations that require exact and reproducible behavior should be implemented using deterministic code such as Python or SQL.

The language model should not serve as the authoritative source for numerical calculations that can be performed reliably by deterministic tools.

### AG-003 - Testability

Core components should be testable independently whenever practical.

For example, analytical calculations should be testable without requiring:

- A user interface.
- A running API server.
- An external AI-model call.
- Network connectivity.

### AG-004 - Replaceable External Dependencies

External dependencies such as AI-model providers, persistence systems, or external services should be isolated behind clear interfaces where the additional abstraction is justified.

Provider-specific AI logic should not be distributed throughout the entire application.

### AG-005 - Evaluation and Observability

The architecture should make important execution steps visible enough to support:

- Automated testing.
- AI evaluation.
- Error analysis.
- Debugging.
- Tool-call inspection.
- Latency measurement.
- Model-usage measurement.
- Cost analysis.

The system should make it possible to determine where an incorrect or low-quality result originated.

### AG-006 - Simplicity Before Complexity

The MVP should prefer a simple modular architecture over distributed or highly complex infrastructure.

Architectural complexity should be introduced when requirements or measured limitations justify it.

The initial system may be implemented as a modular monolith with clear internal boundaries.

### AG-007 - Incremental Evolution

The architecture should support the gradual introduction of:

- Additional analytical tools.
- Machine-learning capabilities.
- AI grounding.
- Tool calling.
- Agentic workflows.
- Evaluation capabilities.
- Observability.
- More capable persistence.

Extensibility should come primarily from clear module boundaries rather than speculative infrastructure.

## 2. System Context

DecisionAI is an AI-assisted decision-support system that sits between business users, structured business data, deterministic analytical capabilities, and external AI-model services.

The initial system boundary includes the user interface, API, application orchestration, data processing, deterministic analytics, machine learning, AI integration, evaluation, observability, and persistence components required by the MVP.

### 2.1 Primary Actor

The primary actor is the Business Analyst.

The Business Analyst may:

- Provide or select supported business data.
- Ask supported analytical questions.
- Review calculated evidence.
- Review AI-assisted interpretations.
- Validate important findings.
- Decide what requires further investigation.

DecisionAI supports the analyst's workflow but does not replace human responsibility for important business decisions.

### 2.2 Secondary Actor

The secondary actor is the Operations Manager or business stakeholder.

This actor primarily consumes analytical findings and wants to understand:

- What changed.
- Which factors contributed most.
- What evidence supports the finding.
- Which area deserves further investigation.

### 2.3 External AI Provider

Gemini is an external dependency of DecisionAI.

DecisionAI controls the information sent to the AI provider and how model outputs are used, but it does not control the external model implementation or infrastructure.

The architecture should therefore account for:

- External-service failures.
- Latency.
- Model-output uncertainty.
- Usage cost.
- Provider-specific integration logic.

### 2.4 External Business Data

The MVP receives structured business data from external sources, initially represented as supported local datasets.

Initial datasets include:

- `orders.csv`
- `customers.csv`
- `products.csv`

External data should be treated as untrusted until validation has been completed.

### 2.5 System Boundary

The initial DecisionAI system boundary includes:

- User-interface logic.
- API handling.
- Application orchestration.
- Data ingestion and validation.
- Deterministic analytics.
- Machine-learning capabilities.
- AI-model integration.
- Tool execution.
- Evaluation.
- Observability.
- Persistence.

External AI providers and source business systems remain outside the DecisionAI system boundary.

### 2.6 Initial External Systems Outside Scope

The initial MVP does not depend directly on external enterprise systems such as:

- CRM platforms.
- ERP systems.
- Marketing platforms.
- Data warehouses.
- Messaging platforms.
- Autonomous browser systems.
- External business-action systems.

These integrations may be evaluated later if product requirements justify them.

### 2.7 Trust Boundaries

DecisionAI should explicitly recognize trust boundaries around:

- User input.
- Uploaded or imported business data.
- External AI-model responses.
- Future external tool integrations.

Information crossing a trust boundary should be validated before it is treated as trusted internal state.

AI-generated output should not automatically be treated as authoritative evidence.

## 3. Architectural Boundaries

DecisionAI should separate responsibilities into explicit architectural boundaries so that deterministic logic, external integrations, user interaction, and AI behavior can evolve and be evaluated independently.

### 3.1 Presentation Boundary

The presentation layer is responsible for:

- Receiving user input.
- Displaying application state.
- Displaying analytical evidence.
- Displaying AI-assisted interpretations.
- Communicating validation and error messages.

The presentation layer should not contain core analytical, machine-learning, or AI-provider logic.

### 3.2 Application Boundary

The application layer coordinates product use cases.

Responsibilities may include:

- Coordinating data access.
- Invoking analytical capabilities.
- Invoking AI capabilities when required.
- Combining intermediate results.
- Applying workflow-level decisions.
- Producing application-level outputs.

The application layer should orchestrate domain capabilities rather than implementing all underlying analytical logic itself.

### 3.3 Data Boundary

The data layer is responsible for:

- Data loading.
- Schema validation.
- Data-quality validation.
- Cleaning and normalization where appropriate.
- Persistence.
- Data retrieval.

The data layer should not contain AI interpretation or high-level analytical conclusions.

### 3.4 Analytics Boundary

The analytics layer is responsible for deterministic analytical logic such as:

- Revenue calculations.
- KPI comparisons.
- Growth calculations.
- Average-order-value calculations.
- Dimensional analysis.
- Contributor calculations and ranking.

Analytics should remain independent from the user interface and external AI provider whenever practical.

### 3.5 Machine-Learning Boundary

Machine-learning responsibilities should remain separate from basic deterministic analytics.

This boundary may later include:

- Feature preparation.
- Model training.
- Prediction.
- Model evaluation.
- Model persistence.

Machine-learning capabilities should be introduced only where they support a defined product requirement.

### 3.6 AI Boundary

The AI layer is responsible for interactions with external AI models.

Responsibilities may include:

- Prompt construction.
- Model configuration.
- Structured-output handling.
- Provider-specific integration.
- AI-response validation.
- AI-related error handling.

Provider-specific code should remain isolated from the rest of the application where practical.

### 3.7 Tool Boundary

AI tools should expose controlled application or analytical capabilities to the AI layer.

A tool wrapper should not unnecessarily duplicate underlying business or analytical logic.

Where practical, tools should call existing deterministic capabilities rather than reimplement them.

### 3.8 Evaluation Boundary

Evaluation logic should remain separate from normal production logic.

The evaluation layer may assess:

- Deterministic correctness.
- Tool selection.
- Structured output.
- Evidence consistency.
- AI interpretation.
- Regression behavior.

Evaluation should be able to inspect system behavior without becoming part of the business logic being evaluated.

### 3.9 Observability Boundary

Observability should capture important system behavior across multiple components without tightly coupling those components to a specific monitoring implementation.

Relevant signals may include:

- Request identifiers.
- Errors.
- Tool calls.
- AI-model calls.
- Latency.
- Token usage.
- Cost.
- Evaluation results.

### 3.10 Dependency Principle

Higher-level interaction and orchestration layers may depend on lower-level domain capabilities.

Core deterministic logic should avoid dependencies on user interfaces, transport frameworks, or external AI providers.

The architecture should preserve the ability to test core analytical behavior independently.

## 4. Component Responsibilities

The initial DecisionAI architecture should define components by responsibility rather than by framework or implementation detail.

The component model may evolve during implementation, but the responsibility boundaries should remain explicit.

### 4.1 Presentation Components

Presentation components are responsible for exposing DecisionAI capabilities to users or external clients.

Initial presentation technologies may include:

- Streamlit.
- FastAPI routes.

Responsibilities include:

- Receiving user requests.
- Presenting validation errors.
- Displaying analytical evidence.
- Displaying AI-assisted interpretations.
- Returning structured API responses.

Presentation components should not implement core analytical logic.

### 4.2 Application Orchestrator

The application orchestrator coordinates complete product use cases.

Responsibilities may include:

- Coordinating data access.
- Invoking validation.
- Invoking analytical capabilities.
- Invoking AI interpretation when required.
- Combining intermediate outputs.
- Applying workflow-level decisions.
- Producing an application-level result.

The orchestrator should coordinate specialized components rather than duplicate their internal logic.

### 4.3 Data Loader

The data loader is responsible for reading supported data sources into an internal representation.

The initial implementation may support local CSV files.

Future implementations may support additional persistence or external data sources without changing the analytical logic.

### 4.4 Data Validator

The data validator is responsible for determining whether input data is sufficiently valid for the requested analysis.

Validation may include:

- Required columns.
- Data types.
- Missing values.
- Duplicate identifiers.
- Invalid relationships.
- Impossible or unsupported values.

Validation should produce explicit errors or warnings rather than silently accepting unreliable data.

### 4.5 Analytics Engine

The analytics engine provides deterministic analytical capabilities.

Initial capabilities may include:

- Revenue calculation.
- Period comparison.
- Absolute and percentage change.
- Order volume.
- Average order value.
- Dimensional aggregation.
- Contributor analysis.
- Contributor ranking.

Analytical outputs should be structured so they can be tested, evaluated, stored, and interpreted independently from the user interface.

### 4.6 Machine-Learning Service

Machine-learning capabilities should be exposed through a separate service or module when predictive functionality is introduced.

Responsibilities may include:

- Feature preparation.
- Training.
- Prediction.
- Model evaluation.
- Loading and saving model artifacts.

Machine-learning implementation details should not leak unnecessarily into higher-level application logic.

### 4.7 AI Provider Client

The AI provider client is responsible for communicating with the external AI-model provider.

Responsibilities may include:

- Provider authentication.
- Request execution.
- Provider-specific configuration.
- Response retrieval.
- Provider error handling.
- Usage metadata collection.

The initial provider will be Gemini.

### 4.8 AI Interpretation Service

The AI interpretation service transforms structured analytical evidence into controlled AI-assisted interpretation tasks.

Responsibilities may include:

- Constructing model context.
- Defining interpretation instructions.
- Requesting structured AI output.
- Validating AI responses.
- Ensuring numerical claims remain consistent with analytical evidence.

This component should use analytical outputs as evidence rather than asking the model to recreate deterministic calculations.

### 4.9 Tool Registry

The tool registry exposes an explicitly approved set of capabilities that may be invoked by AI-driven workflows.

Responsibilities may include:

- Registering supported tools.
- Resolving tool identifiers.
- Validating tool arguments.
- Executing approved capabilities.
- Returning structured tool results.

The registry should not provide unrestricted code or operating-system execution.

### 4.10 Persistence Component

Persistence components are responsible for storing and retrieving application state or results where required.

The initial persistence implementation may use SQLite.

Possible stored information may later include:

- Analysis sessions.
- Structured analytical results.
- Evaluation runs.
- Execution metadata.

Persistence technology should remain separated from core analytical logic.

### 4.11 Evaluation Runner

The evaluation runner executes defined evaluation cases against DecisionAI capabilities and compares actual behavior with expected behavior.

Responsibilities may include:

- Loading evaluation cases.
- Executing system workflows.
- Comparing deterministic results.
- Evaluating AI output characteristics.
- Recording evaluation results.
- Supporting regression analysis.

### 4.12 Observability Component

Observability components collect structured information about system execution.

Relevant events and metrics may include:

- Request identifiers.
- Workflow steps.
- Tool calls.
- Model calls.
- Errors.
- Latency.
- Token usage.
- Cost estimates.
- Evaluation results.

Observability should support debugging and analysis without becoming part of the core business logic.

### 4.13 Component Design Principle

Components should have focused responsibilities and communicate through explicit inputs and outputs.

The architecture should avoid components that combine unrelated responsibilities merely for implementation convenience.

Conceptual components do not necessarily require one class or one source file each. Physical code organization should remain as simple as possible while preserving clear responsibility boundaries.

## 5. Data Flow

DecisionAI should transform user requests into evidence-backed analytical responses through an explicit sequence of validation, deterministic analysis, AI-assisted interpretation, and output validation.

The data flow should preserve traceability between user requests, analytical evidence, AI interpretation, and the final response.

### 5.1 User Request

A supported analysis begins with a user request received through a presentation component such as Streamlit or FastAPI.

The request may contain:

- A natural-language analytical question.
- Analysis parameters.
- Dataset references.
- Time periods.
- Requested metrics or dimensions.

### 5.2 Request Validation

The system should determine whether the request is sufficiently specified and supported by the MVP.

Unsupported or incomplete requests should produce an explicit response rather than triggering unsupported analytical behavior.

### 5.3 Data Acquisition

The application orchestrator requests the required data through the data layer.

The initial data source may consist of local CSV datasets.

The data-loading component should retrieve the data without performing business interpretation.

### 5.4 Data Validation

Loaded data should pass through the data-validation boundary before it is used by analytical components.

Critical validation failures should prevent unreliable analysis.

Warnings that do not prevent execution should remain available for later inclusion in the final result.

### 5.5 Deterministic Analysis

Validated data is passed to deterministic analytical capabilities.

The analytical workflow may calculate:

- Revenue.
- Revenue change.
- Percentage change.
- Order volume.
- Average order value.
- Dimensional aggregations.
- Contributor rankings.

These calculations should produce structured results.

### 5.6 Structured Evidence

Analytical outputs should be transformed into a structured evidence representation.

Structured evidence may include:

- Metric values.
- Comparison periods.
- Absolute and percentage changes.
- Contributor rankings.
- Data-quality warnings.
- Analytical limitations.
- Execution metadata.

This representation forms a contract between deterministic analysis and downstream AI interpretation.

### 5.7 AI Interpretation

When AI interpretation is required, the AI layer receives:

- The user's supported question.
- Structured analytical evidence.
- Controlled interpretation instructions.

The language model should use the supplied analytical evidence rather than independently reconstructing deterministic calculations.

### 5.8 AI Output Validation

AI-generated interpretations should be validated before they are treated as application output.

Validation may include checks for:

- Required output structure.
- Unsupported numerical claims.
- Contradictions with analytical evidence.
- Unsupported causal claims.
- Missing limitations.

### 5.9 Final Response Assembly

The application layer combines deterministic and AI-generated information into the final product response.

A response may include:

- Analysis summary.
- Main contributors.
- Supporting evidence.
- AI-assisted interpretation.
- Recommended investigation priorities.
- Data or analytical limitations.

### 5.10 Human Review

Important findings remain subject to human review.

The user should be able to inspect the evidence supporting the AI-assisted interpretation before acting on the result.

### 5.11 Observability Flow

Observability should capture important events across the end-to-end workflow.

Relevant events may include:

- Request received.
- Data loaded.
- Validation completed.
- Analysis executed.
- Tool invoked.
- AI model called.
- AI output validated.
- Final response produced.
- Error encountered.

### 5.12 Failure Flow

The application should fail explicitly when reliable analysis cannot continue.

Examples include:

- Invalid required data.
- Unsupported analytical requests.
- Failed deterministic calculations.
- Invalid AI output.
- External AI-provider failure.

Where appropriate, the system should degrade gracefully.

For example, if deterministic analysis succeeds but AI interpretation is temporarily unavailable, the application may still return the validated analytical evidence with an explicit notice that AI interpretation could not be produced.

### 5.13 Data-Flow Principle

Analytical evidence should become progressively more trusted as it passes through validation and deterministic processing.

External input and AI-generated output should not become trusted application state without appropriate validation.

## 6. Layering and Dependency Rules

DecisionAI should use explicit dependency rules so that module boundaries remain meaningful during implementation.

Code organization alone does not create modularity. Components should also control which other components they are allowed to depend on.

### 6.1 Presentation Dependencies

Presentation components may depend on application-level capabilities and shared request or response schemas.

Presentation components should not directly implement or tightly couple themselves to:

- Deterministic analytical logic.
- Data persistence details.
- Machine-learning implementations.
- AI-provider SDKs.

### 6.2 Application Dependencies

The application layer may coordinate:

- Data capabilities.
- Analytics.
- Machine learning.
- AI interpretation.
- Tools.
- Persistence.
- Observability.

Application components should focus on workflow coordination and avoid duplicating the specialized logic of lower-level components.

### 6.3 Analytics Dependencies

The deterministic analytics layer should remain independent from:

- Streamlit.
- FastAPI.
- External AI providers.
- AI prompting logic.
- Presentation-specific behavior.

Analytics should depend only on the data structures and utilities required to perform reproducible calculations.

### 6.4 Data Dependencies

The data layer may depend on:

- Data schemas.
- Validation utilities.
- Persistence implementations.
- Supported data-processing libraries.

Basic data validation should not require an external AI model when the validation rule can be expressed deterministically.

### 6.5 AI Dependencies

The AI layer should depend on explicit analytical evidence and application contracts rather than uncontrolled access to the entire system.

Provider-specific SDK usage should remain isolated inside AI integration components.

### 6.6 Tool Dependencies

Tools should expose existing application or analytical capabilities to AI-driven workflows.

Tools should not unnecessarily duplicate deterministic business or analytical logic.

### 6.7 Machine-Learning Dependencies

Machine-learning components may depend on validated data, defined feature representations, and approved ML libraries.

Higher-level application components should interact with ML through defined capabilities rather than depending on specific model implementations throughout the codebase.

### 6.8 Evaluation Dependencies

Evaluation components may depend on the application and lower-level capabilities being evaluated.

Production components should not depend on evaluation-specific logic.

This follows the same general principle that tests depend on production code, while production code should not depend on tests.

### 6.9 Observability Dependencies

Observability is a cross-cutting concern and may receive execution information from multiple components.

Core components should avoid becoming tightly coupled to a specific observability vendor or external monitoring implementation.

### 6.10 External Framework Principle

Frameworks and provider SDKs should remain close to the edges of the architecture where practical.

Examples include:

- Streamlit.
- FastAPI.
- Gemini SDKs.
- Database drivers.
- Monitoring vendors.

Core analytical and product logic should not require unnecessary knowledge of these external implementation details.

### 6.11 Dependency Inversion Principle

Higher-level application logic should depend on capabilities or contracts rather than unnecessarily depending on specific external implementations.

For example, application logic may require an AI-interpretation capability while a Gemini-specific implementation provides that capability.

This separation can improve:

- Replaceability.
- Testability.
- Failure isolation.
- Maintainability.

Abstractions should be introduced only where they provide clear value and should not create unnecessary complexity.

### 6.12 Circular Dependency Rule

Circular module dependencies should be avoided.

For example, if module A depends on module B, module B should not normally require module A in order to perform its own core responsibility.

Circular dependencies often indicate that responsibilities or interfaces need to be reconsidered.

### 6.13 Shared Models

Data structures that represent genuinely shared contracts may be defined in a common schema or model layer.

Potential examples include:

- AnalysisRequest.
- AnalysisResult.
- ValidationResult.
- ContributorResult.
- Error representations.

Shared modules should remain focused and should not become a general location for unrelated logic.

### 6.14 Dependency Principle

Dependencies should generally point from interaction and orchestration layers toward stable core capabilities.

The architecture should minimize coupling from deterministic business logic toward external frameworks, user interfaces, and AI-provider implementations.

## 7. Python Package Architecture

The physical Python package structure should reflect the architectural responsibilities defined in this document.

Packages should be created when they represent a real responsibility in the system rather than being added only to anticipate possible future complexity.

### 7.1 Target Package Structure

The target DecisionAI application structure may evolve toward:

```text
app/
├── api/
├── application/
├── data/
├── analytics/
├── ml/
├── ai/
├── tools/
├── evaluation/
└── observability/
```

### 7.2 Incremental Package Creation

The target package structure is conceptual.

Packages should be added only when implementation introduces a real responsibility.

The architecture should not create empty package trees purely to make the repository appear complete.

### 7.3 Initial Physical Structure

At the current stage, the repository only requires:

```text
app/
├── __init__.py
├── analytics/
│   └── __init__.py
└── data/
    └── __init__.py
```

The `data` package is justified by the upcoming data-foundation work.

The `analytics` package is justified by the upcoming deterministic-analytics phase.

### 7.4 Agent Package Decision

An `agents/` package should not be created during the initial architecture phase.

Agentic components should only be introduced after controlled orchestration and tool-use capabilities exist and evaluation demonstrates that additional agentic complexity is useful.

### 7.5 Shared Utility Principle

The project should avoid creating broad generic `utils` modules that collect unrelated functionality.

Shared helpers should remain close to the responsibility they support unless they become genuinely cross-cutting.

### 7.6 Package Architecture Principle

Physical structure should follow demonstrated responsibilities.

The project should preserve modularity without confusing architecture quality with file count.

## 8. Configuration and Environment

DecisionAI should separate application configuration from application logic.

Values that vary between development environments, machines, or deployments should not be hardcoded throughout the codebase.

### 8.1 Configuration Sources

Initial configuration may be provided through:

- Environment variables.
- Local `.env` files for development.
- Deployment-specific secret or configuration systems in later environments.

The repository should provide documentation for required configuration without exposing real secrets.

### 8.2 Secret Management

Sensitive configuration such as API keys must not be committed to source control.

Examples include:

- Gemini API keys.
- Database credentials.
- External-service access tokens.

Local secrets may be stored in a `.env` file that remains excluded from Git.

A `.env.example` file may document required variable names using empty or non-sensitive example values.

### 8.3 Centralized Settings

Application configuration should be loaded and validated in a centralized settings component rather than being retrieved independently throughout unrelated modules.

Conceptually:

```text
Environment Variables
        ↓
Validated Settings
        ↓
Application Components
```

### 8.4 Required and Optional Configuration

Configuration should distinguish between:

- Required values.
- Optional values.
- Values with safe defaults.

Missing required configuration should fail explicitly during startup or capability initialization.

### 8.5 Environment Separation

The application should support clear environment concepts such as:

- Development.
- Test.
- Production.

Configuration differences should not require editing source code.

### 8.6 Paths

Machine-specific absolute paths should not be embedded in application logic.

Data and persistence paths should be configurable or resolved relative to controlled project locations.

### 8.7 Test Configuration

Deterministic unit tests should not require production credentials or live AI services.

Tests should use controlled configuration and replaceable external dependencies where practical.

### 8.8 Configuration Ownership

Core analytics should not read environment variables directly.

Infrastructure-facing or initialization components should obtain configuration and provide validated values to lower-level capabilities where needed.

### 8.9 Initial Configuration Variables

Initial configuration may include:

- `GEMINI_API_KEY`
- `APP_ENV`
- `LOG_LEVEL`
- `DATABASE_URL`
- `DATA_DIR`

Not every variable needs to be implemented immediately.

### 8.10 Configuration Principle

Configuration should be explicit, validated, environment-aware, and separated from core analytical behavior.

## 9. Error Handling Strategy

DecisionAI should classify and handle failures explicitly rather than treating every failure as the same type of error.

The error-handling strategy should preserve reliability, debuggability, observability, and useful user-facing behavior.

### 9.1 Expected Failures and Software Bugs

The system should distinguish between expected operational failures and unexpected software defects.

Expected failures may include:

- Invalid input data.
- Unsupported user requests.
- Missing configuration.
- Insufficient data.
- External-service failures.
- Persistence failures.

Unexpected exceptions that indicate software defects should not be silently converted into normal application behavior.

### 9.2 Validation Errors

Invalid required input should produce explicit validation errors before analytical execution begins.

Examples include:

- Missing required columns.
- Invalid data types.
- Invalid date values.
- Broken dataset relationships.
- Unsupported values.

Critical validation errors should stop the affected analysis.

### 9.3 Unsupported Requests

Requests outside the supported product scope should be classified explicitly rather than being sent through an unsupported analytical workflow.

The user should receive a clear explanation that the requested capability is not supported by the current system.

### 9.4 Insufficient Data

When valid data is present but insufficient to produce a reliable result, the system should report that condition explicitly.

Examples may include:

- No observations for a requested period.
- Insufficient samples for a predictive capability.
- Missing dimensions required by the requested analysis.

The system should not invent results when evidence is insufficient.

### 9.5 External-Service Failures

External dependencies may fail because of:

- Timeouts.
- Network problems.
- Provider outages.
- Rate limits.
- Authentication failures.
- Invalid provider responses.

These failures should be translated into explicit application error categories.

### 9.6 Retry Policy

Retries should be limited to failures that are reasonably expected to be temporary.

Retry behavior should eventually consider:

- Maximum retry count.
- Timeouts.
- Backoff.
- Cost.
- End-to-end latency.

Non-retryable failures such as invalid data or missing required configuration should fail without unnecessary retry attempts.

### 9.7 Graceful Degradation

The system should preserve useful functionality when an optional capability fails and reliable results remain available.

For example, if deterministic analysis succeeds but AI interpretation is unavailable, the application may return the validated analytical evidence with an explicit notice that the AI-assisted interpretation could not be generated.

Failures in core evidence generation should not be hidden through graceful degradation.

### 9.8 Error Propagation

Lower-level components should expose meaningful error categories rather than silently returning ambiguous values such as `None` for every failure.

Workflow-level components should decide whether a classified failure should:

- Stop execution.
- Trigger a retry.
- Use a fallback.
- Degrade functionality.
- Return a user-facing error.

### 9.9 Internal and User-Facing Errors

Technical error details should remain available for debugging and observability while user-facing responses should remain clear and appropriate for the product context.

User-facing errors should not expose:

- Secrets.
- Credentials.
- Internal stack traces.
- Unnecessary infrastructure details.

### 9.10 Exception Handling Principle

Broad exception handling should not silently hide unexpected software defects.

Components should catch specific exceptions when they know how to handle them.

Unexpected exceptions may be captured at appropriate system boundaries for logging and controlled error responses, but the underlying failure should remain observable.

### 9.11 Initial Error Taxonomy

The architecture may use an application-level error hierarchy similar to:

```text
DecisionAIError
├── ConfigurationError
├── ValidationError
├── UnsupportedRequestError
├── InsufficientDataError
├── AnalyticsError
├── ExternalServiceError
│   └── AIProviderError
├── PersistenceError
└── OutputValidationError
```

### 9.12 Fail-Fast Principle

Failures that invalidate core assumptions should be detected as early as practical.

The system should not continue with knowingly invalid evidence merely to produce an output.

### 9.13 Error-Handling Principle

DecisionAI should fail explicitly, retry selectively, and degrade only when the remaining result remains trustworthy and useful.

## 10. Interfaces and Contracts

DecisionAI components should communicate through explicit interfaces and structured data contracts where those boundaries provide meaningful architectural value.

Contracts should reduce ambiguity between components and make important inputs and outputs easier to validate, test, evaluate, and evolve.

### 10.1 Interface Principle

An interface defines a capability that another component may use.

Examples may include:

- Data-loading capabilities.
- Analytical capabilities.
- AI-interpretation capabilities.
- Persistence capabilities.
- Tool-execution capabilities.

Higher-level components should depend on clearly defined capabilities rather than unnecessary implementation details.

### 10.2 Data Contract Principle

A data contract defines the expected structure, types, and meaning of information exchanged between components.

Important cross-boundary data should avoid relying on ambiguous or undocumented dictionaries where a stable structured model would provide clearer behavior.

### 10.3 Analysis Request

An `AnalysisRequest` contract may represent a supported analytical request.

Potential fields include:

- User question.
- Metric.
- Current period.
- Comparison period.
- Requested dimensions.
- Dataset references.

The exact fields should be refined when implementation begins.

### 10.4 Validation Result

A `ValidationResult` contract may communicate data-quality validation outcomes.

Potential fields include:

- Validity status.
- Errors.
- Warnings.
- Validation metadata.

Validation results should provide enough information for the application layer to determine whether execution may continue.

### 10.5 Metric Comparison

A metric-comparison contract may represent deterministic KPI comparison results.

Potential fields include:

- Metric name.
- Previous value.
- Current value.
- Absolute change.
- Percentage change.

### 10.6 Contributor Result

A `ContributorResult` contract may represent an observed contributor to a KPI change.

Potential fields include:

- Dimension.
- Dimension value.
- Previous metric value.
- Current metric value.
- Absolute change.
- Estimated contribution.

The contract should avoid implying causal interpretation when the analysis only establishes observed contribution.

### 10.7 Analysis Result

An `AnalysisResult` contract should provide the structured evidence produced by deterministic analysis.

Potential content includes:

- Metric summary.
- Comparison results.
- Contributor results.
- Supporting evidence.
- Data-quality warnings.
- Analytical limitations.
- Relevant execution metadata.

This contract may become the primary boundary between deterministic analytics and AI interpretation.

### 10.8 AI Interpretation

AI-assisted interpretation should use a structured output contract where practical.

Potential fields may include:

- Summary.
- Investigation priorities.
- Limitations.
- Uncertainty or confidence notes.

AI-generated structured output should be validated before it is treated as trusted application state.

### 10.9 Final Response

A final application response may combine:

- Deterministic analysis.
- AI-assisted interpretation.
- Supporting evidence.
- Warnings.
- Limitations.
- Application metadata.

Presentation components should consume this application response rather than reconstructing analytical logic themselves.

### 10.10 DataFrame Boundary

Pandas DataFrames may be used internally for data loading and analytical computation.

Important architectural boundaries should prefer explicit structured contracts when doing so improves clarity, validation, and stability.

### 10.11 Internal and External Models

Internal application contracts and external API schemas may be shared when appropriate but should not be assumed to remain identical forever.

External interfaces should expose only information that belongs in the public product contract.

### 10.12 Contract Validation

Structured contracts should be validated when crossing important boundaries.

Pydantic may be used for contracts where runtime validation, serialization, or schema generation provides value.

### 10.13 AI Output Contracts

AI-generated structured data should be treated as untrusted until it passes the required contract validation.

Invalid AI output may produce an `OutputValidationError` or trigger an explicitly defined retry or fallback strategy.

### 10.14 Tool Contracts

AI tools should expose explicit input and output schemas.

Tool arguments should be validated before execution, and tool results should use structured output where practical.

### 10.15 Contract Evolution

Contracts should evolve deliberately.

Changes to stable cross-component contracts should consider the impact on:

- Callers.
- Tests.
- AI prompts.
- Tool schemas.
- API responses.
- Evaluation cases.
- Persistence.

### 10.16 Contract Principle

Important boundaries should exchange structured, validated, and well-defined information.

Contracts should improve clarity and reliability without introducing unnecessary abstraction for trivial internal operations.

## 11. Initial Persistence Architecture

DecisionAI should introduce persistence only for information that provides value beyond the lifetime of a single execution.

The initial persistence architecture should remain simple while preserving a boundary between application logic and database-specific implementation details.

### 11.1 Persistence Scope

Potential persistent information may include:

- Analysis sessions.
- Structured analytical results.
- Evaluation runs.
- Execution metadata.
- User feedback in future versions.

Intermediate values that are only required during a single analysis should not automatically be persisted.

### 11.2 Initial Database Choice

SQLite is the initial persistence technology for the local MVP.

This choice is based on:

- Low operational complexity.
- No separate database server requirement.
- Strong local-development support.
- Easy project portability.
- Sufficient capability for the expected initial scale.

SQLite should not be treated as a permanent architectural requirement.

### 11.3 Persistence Boundary

Application and analytical logic should avoid direct dependency on SQLite-specific implementation details.

Conceptually:

```text
Application
    ↓
Repository Capability
    ↓
SQLite Repository
    ↓
SQLite
```

This separation allows persistence technology to evolve with future requirements.

### 11.4 Repository Responsibilities

Repository components may provide capabilities such as:

- Saving an analysis.
- Retrieving an analysis.
- Listing stored analyses.
- Recording evaluation runs.
- Storing execution metadata.

Repository interfaces should represent application needs rather than exposing arbitrary database operations throughout the codebase.

### 11.5 Initial Persistent Models

Potential persistent concepts may include:

- AnalysisSession.
- AnalysisResult.
- EvaluationRun.

The exact database schema should be defined when implementation requirements are clearer.

### 11.6 Structured Data vs Flexible Payloads

Some structured analytical results may initially be stored using a flexible serialized representation where doing so reduces unnecessary schema complexity.

More normalized relational structures should be introduced when querying, integrity, or product requirements justify them.

### 11.7 Transactions

Operations that must remain consistent together should use transactions where appropriate.

For example, if an analysis record and its associated result must be created as one logical operation, the persistence layer should avoid leaving partially written state.

### 11.8 Concurrency

The initial system assumes limited local concurrency.

If future usage introduces multiple simultaneous users or significant concurrent writes, the database architecture should be reevaluated.

A more capable database such as PostgreSQL may become appropriate when concurrency or operational requirements justify the change.

### 11.9 Schema Evolution

Database schema changes should be versioned and applied deliberately.

A migration strategy should be introduced when schema evolution becomes frequent enough to justify dedicated migration tooling.

### 11.10 Persistence Errors

Database-specific failures should be translated into meaningful application-level persistence errors where appropriate.

Higher-level application logic should not require detailed knowledge of SQLite driver exceptions.

### 11.11 Persistence Testing

Persistence behavior should support isolated testing.

Application workflows should be testable using controlled or replaceable repository implementations where practical.

Integration tests may verify the real SQLite implementation separately.

### 11.12 Privacy and Retention

Persistence should follow data-minimization principles.

DecisionAI should avoid storing:

- Secrets.
- Unnecessary sensitive raw data.
- Information without a defined product or operational purpose.

Data-retention and deletion policies should be defined before real sensitive business data is introduced.

### 11.13 Persistence Principle

DecisionAI should persist information deliberately rather than automatically.

The initial design should optimize for simplicity while keeping database-specific implementation details behind an explicit persistence boundary.

## 12. AI Boundary

DecisionAI should treat external AI models as probabilistic capabilities operating behind an explicit architectural boundary.

AI models should provide flexibility where language understanding, planning, interpretation, or communication adds value while deterministic components remain responsible for reproducible analytical evidence.

### 12.1 AI Responsibilities

The AI layer may support capabilities such as:

- Natural-language intent understanding.
- Analysis planning.
- Tool selection.
- Interpretation of structured analytical evidence.
- Prioritization of investigation areas.
- Natural-language explanation.
- Structured AI-assisted output.

### 12.2 Deterministic Responsibilities

The AI model should not be the authoritative implementation for operations that can be performed reliably through deterministic code.

Examples include:

- Revenue calculations.
- Percentage changes.
- Basic KPI calculations.
- Schema validation.
- Deterministic business rules.

These capabilities should remain in Python, SQL, or other deterministic components.

### 12.3 External Provider Boundary

Gemini is an external dependency.

DecisionAI does not control the provider's internal model, infrastructure, availability, or model updates.

The integration should therefore account for:

- Timeouts.
- Provider errors.
- Rate limits.
- Latency.
- Usage cost.
- Output uncertainty.

### 12.4 Provider Client

Provider-specific communication should remain isolated in an AI provider client.

Responsibilities may include:

- Authentication.
- Provider requests.
- Provider-specific configuration.
- Response retrieval.
- Provider error translation.
- Usage metadata collection.

Application-level analytical meaning should not be unnecessarily embedded in the provider client.

### 12.5 AI Interpretation Capability

Application-level AI capabilities should remain separate from provider-specific communication where practical.

For example, an analysis-interpretation capability may define:

- The structured evidence required.
- Interpretation instructions.
- Expected structured output.
- Output-validation requirements.

A Gemini-specific implementation may then provide the external model execution required by that capability.

### 12.6 Context Boundary

The AI model should receive the minimum context required to perform its task reliably.

Where practical, raw business data should first be transformed into validated and structured analytical evidence.

This approach may improve:

- Privacy.
- Traceability.
- Cost.
- Latency.
- Context quality.

### 12.7 Prompt Separation

Trusted application instructions, user input, and analytical evidence should remain conceptually separated.

Content supplied through user input or business data should not automatically be treated as trusted model instructions.

### 12.8 Grounding

AI interpretation should be grounded in structured evidence produced by validated analytical processes.

Grounding does not require a specific retrieval technology.

The initial grounding strategy may rely primarily on structured analytical results.

### 12.9 Structured AI Output

AI-generated application data should use structured output contracts where practical.

Potential structured fields may include:

- Summary.
- Investigation priorities.
- Limitations.
- Uncertainty notes.

AI output should be validated before becoming trusted application state.

### 12.10 Tool Calling

When tool calling is introduced, the AI model should request capabilities through the approved tool boundary.

Conceptually:

```text
AI Model
    ↓
Tool Request
    ↓
Tool Registry
    ↓
Argument Validation
    ↓
Approved Capability
    ↓
Structured Tool Result
    ↓
AI Model
```

The model should not receive unrestricted execution access.

### 12.11 Tool Allowlist

Only explicitly registered tools should be available to AI-driven workflows.

Requests for unknown or unauthorized capabilities should be rejected.

### 12.12 Model Configuration

Model configuration should be centralized rather than scattered throughout application code.

Relevant configuration may include:

- Provider model identifier.
- Temperature or sampling settings.
- Output constraints.
- Structured-output configuration.
- Timeout settings.

### 12.13 Model Selection

Model selection should be treated as an engineering trade-off between:

- Quality.
- Cost.
- Latency.
- Reliability.

The architecture should allow model choices to evolve without requiring changes to deterministic analytical logic.

### 12.14 AI Observability

AI requests should provide sufficient metadata for debugging, evaluation, and cost analysis.

Relevant metadata may include:

- Model identifier.
- Request identifier.
- Latency.
- Usage information.
- Provider errors.
- Retry behavior.

Sensitive prompt or business data should not be logged unnecessarily.

### 12.15 AI Failure Handling

AI-provider failures should be translated into explicit application-level errors.

Workflow-level application logic should decide whether to:

- Retry.
- Use a fallback.
- Degrade gracefully.
- Return deterministic results without AI interpretation.
- Stop execution.

### 12.16 AI Testability

Application components that use AI capabilities should be testable without requiring a real model call for every unit test.

Replaceable or controlled AI implementations may be used in unit testing.

Real model calls should be reserved for appropriate integration tests and evaluation workflows.

### 12.17 AI Evaluation

AI behavior should be evaluated independently from deterministic analytical correctness where practical.

Relevant evaluation dimensions may include:

- Consistency with evidence.
- Unsupported numerical claims.
- Unsupported causal claims.
- Relevance.
- Clarity.
- Appropriate communication of limitations.

### 12.18 AI Boundary Principle

DecisionAI should treat AI models as powerful but probabilistic external capabilities.

The system should ground AI behavior in validated evidence, constrain model access through explicit interfaces and tools, validate AI-generated outputs, and preserve deterministic components as the source of reproducible analytical truth.

## 13. Evaluation Boundary

DecisionAI should treat evaluation as a dedicated architectural capability rather than embedding evaluation logic inside normal production behavior.

Evaluation should measure deterministic correctness, AI-system behavior, regression risk, and user-relevant quality.

### 13.1 Software Tests and AI Evaluations

DecisionAI should distinguish between software tests and AI evaluations.

Software tests primarily verify deterministic implementation behavior.

Examples include:

- Revenue calculation.
- Percentage change.
- Data validation.
- Repository behavior.
- Contract validation.

AI evaluations assess probabilistic or system-level behavior.

Examples include:

- Evidence consistency.
- Tool selection.
- Investigation prioritization.
- Unsupported claims.
- Causal overclaiming.
- Communication of limitations.

Both are required.

### 13.2 Evaluation Dependency

Evaluation components may depend on production components in order to exercise and measure them.

Production components should not depend on evaluation-specific logic.

Conceptually:

```text
Evaluation
    ↓
Production System
```

### 13.3 Deterministic Evaluation

When expected outcomes are objective, evaluation should prefer deterministic comparison.

Examples include:

- Expected revenue.
- Expected KPI changes.
- Expected validation failures.
- Expected contributor values.
- Required structured fields.
- Supported tool selections where the expected tool is known.

### 13.4 AI Behavioral Evaluation

AI-generated behavior may require evaluation across dimensions such as:

- Consistency with analytical evidence.
- Unsupported numerical claims.
- Unsupported causal claims.
- Relevance.
- Investigation prioritization.
- Clarity.
- Appropriate limitations.

A combination of deterministic checks, model-based evaluation, and human review may be used.

### 13.5 LLM-as-a-Judge

LLM-based evaluators may be used for qualitative characteristics that are difficult to score deterministically.

LLM judges should not be treated as an unquestionable source of truth.

Their judgments should be periodically compared with human evaluation where the evaluation dimension is important.

### 13.6 Human Evaluation

Human review may evaluate qualities such as:

- Usefulness.
- Clarity.
- Trust.
- Relevance.
- Investigation quality.

Human feedback should complement rather than replace automated evaluation.

### 13.7 Evaluation Dataset

Evaluation cases should be versioned and reproducible.

An evaluation case may include:

- Case identifier.
- User question.
- Input scenario.
- Expected workflow.
- Expected tools.
- Expected facts.
- Expected contributors.
- Expected limitations.
- Evaluation criteria.

### 13.8 Synthetic Ground Truth

Synthetic datasets may be used to create scenarios with known expected outcomes.

This supports reproducible evaluation of:

- Numerical correctness.
- Contributor detection.
- Tool behavior.
- Evidence consistency.

### 13.9 Regression Evaluation

Important failures discovered during development should be converted into regression evaluation cases when practical.

A failure that has been fixed should not silently return in future versions.

### 13.10 Error Analysis

Evaluation failures should be classified and investigated before changes are made.

Potential error categories may include:

- Data errors.
- Analytical errors.
- Tool-selection errors.
- Tool-execution errors.
- Context errors.
- AI-interpretation errors.
- Hallucinations.
- Unsupported causal claims.
- Output-format errors.

Error analysis should connect observed failures to targeted engineering changes.

### 13.11 Failure Severity

Evaluation results may distinguish between different levels of failure severity.

For example:

- Critical.
- Major.
- Minor.

A single aggregate score should not hide severe reliability failures.

### 13.12 Evaluation Runner

An evaluation runner should execute versioned evaluation cases against DecisionAI capabilities.

Conceptually:

```text
Evaluation Dataset
        ↓
Evaluation Runner
        ↓
DecisionAI
        ↓
Actual Output
        ↓
Scorers / Judges
        ↓
Evaluation Result
```

### 13.13 Evaluation Results

Evaluation results should contain enough information to support comparison, regression analysis, and error investigation.

Potential information may include:

- Case identifier.
- Pass or fail status.
- Scores.
- Failure details.
- Error category.
- Failure severity.
- Execution metadata.

### 13.14 Experiment Comparison

The evaluation architecture should support controlled comparison of system variants.

Potential experiments include:

- Prompt A vs Prompt B.
- Model configuration A vs B.
- Simple workflow vs agentic workflow.
- Different context strategies.

Variants should be compared using the same evaluation cases where practical.

### 13.15 Quality, Cost, and Latency

Evaluation of AI-system changes should consider more than quality alone.

Relevant measurements may include:

- Output quality.
- Latency.
- Token usage.
- Model cost.
- Failure rate.

A more complex or expensive workflow should demonstrate enough measured value to justify its additional cost.

### 13.16 Offline and Online Evaluation

The initial system should primarily use reproducible offline evaluation with controlled scenarios.

Future production versions may additionally use online signals such as:

- Real user feedback.
- Production error rates.
- Accepted or rejected findings.
- Real task completion.
- Production latency and cost.

### 13.17 Evaluation Observability

Evaluation workflows should be able to inspect relevant system behavior such as:

- Tools selected.
- Tool results.
- Model calls.
- Structured evidence.
- Final output.
- Latency.
- Errors.

This information should support root-cause analysis when an evaluation fails.

### 13.18 Evaluation Principle

Evaluation should guide development rather than merely certify a finished system.

The DecisionAI development loop should follow:

```text
Build
  ↓
Evaluate
  ↓
Inspect
  ↓
Classify Errors
  ↓
Improve
  ↓
Re-evaluate
```

Measured failures should drive targeted changes and regression coverage.

## 14. Security Boundaries

DecisionAI should treat external input, external model output, tool requests, and external data sources as untrusted until they cross explicit validation and authorization boundaries.

Security controls should minimize the permissions and system access available to each component.

### 14.1 User-Input Boundary

User input should be treated as untrusted.

Requests should be validated before they are converted into supported application operations.

Validation may include:

- Supported request type.
- Required parameters.
- Input size.
- Expected formats.
- Supported analytical scope.

### 14.2 Data-Ingestion Boundary

Uploaded or imported business data should be validated before it becomes trusted analytical input.

Validation may include:

- File type.
- File size.
- Schema.
- Data types.
- Required fields.
- Data relationships.
- Unexpected or malformed content.

### 14.3 AI-Output Boundary

AI-model output should remain untrusted until it passes required contract and evidence validation.

Validation may include:

- Structured-output validation.
- Required fields.
- Numerical consistency.
- Evidence consistency.
- Unsupported causal claims.
- Unsupported tool or action requests.

### 14.4 Tool-Execution Boundary

AI-generated tool requests should pass through an explicit authorization and validation boundary.

Conceptually:

```text
AI Tool Request
       ↓
Tool Registry
       ↓
Tool Authorization
       ↓
Argument Validation
       ↓
Approved Execution
```

The AI model should not receive unrestricted code, operating-system, database, or filesystem execution privileges.

### 14.5 Least-Privilege Principle

Each component should receive only the permissions and configuration required to perform its defined responsibility.

For example:

- The AI provider client may require the Gemini API key.
- Deterministic analytics should not require access to that key.
- Analytical tools should not receive arbitrary filesystem or operating-system permissions.
- Read-only capabilities should be preferred where write access is unnecessary.

### 14.6 Blast-Radius Reduction

The architecture should reduce the maximum impact of component failure or misuse.

AI-driven workflows should operate through narrowly scoped capabilities instead of broad system access.

The initial product should favor analysis and recommendation over autonomous business actions.

### 14.7 Database Boundary

Database access should remain behind persistence or repository components.

The AI model should not directly execute unrestricted SQL.

Database operations should use controlled queries and parameterized values where appropriate.

### 14.8 Filesystem Boundary

User-provided paths or file references should be validated before filesystem access.

The system should prevent arbitrary access to application secrets, configuration files, or unrelated filesystem locations.

### 14.9 Secret Boundary

Secrets should only be made available to components that require them.

Secrets should not be:

- Committed to Git.
- Included in application output.
- Exposed to the AI model without necessity.
- Written to logs.

### 14.10 Logging Boundary

Logging and tracing should provide sufficient information for debugging and security investigation without unnecessarily capturing sensitive information.

Sensitive values should be omitted, masked, or redacted where appropriate.

### 14.11 Prompt-Injection Boundary

Content received from users, datasets, or retrieved sources should be treated as untrusted data.

Trusted system instructions should remain distinguishable from:

- User instructions.
- Uploaded content.
- Retrieved business data.
- Tool results.

Untrusted data should not automatically gain instruction-level authority.

### 14.12 Resource Limits

External inputs should eventually be subject to reasonable resource limits.

Potential controls include:

- Maximum file size.
- Maximum row count.
- Request-size limits.
- Execution timeouts.
- Model-call limits.

These controls help reduce accidental or malicious resource exhaustion.

### 14.13 Rate Limiting

Production-facing interfaces may require rate limiting to protect:

- System availability.
- External-service quotas.
- AI-model cost.
- Infrastructure resources.

Rate limiting should be introduced when the deployment model requires it.

### 14.14 Security Observability

Security-relevant events should be observable where practical.

Examples may include:

- Rejected tool requests.
- Invalid uploaded files.
- Repeated authentication or provider failures.
- Input-validation failures.
- Unauthorized capability requests.

Logs should provide enough context for investigation without exposing sensitive information.

### 14.15 Security Testing

Important security boundaries should eventually be covered by automated tests or evaluation cases.

Potential scenarios include:

- Unknown tool invocation.
- Invalid tool arguments.
- Unsafe file paths.
- Missing required authorization.
- Invalid AI output.
- Oversized or malformed input.
- Secret leakage prevention.

### 14.16 Security Principle

DecisionAI should assume that external inputs and probabilistic AI outputs may be incorrect, malformed, or adversarial.

The system should minimize privileges, validate boundary crossings, restrict AI-driven execution, and preserve human control over high-impact actions.

## 15. Architecture Decision Records

Important architectural choices should be documented using Architecture Decision Records (ADRs).

An ADR should capture:

- The context of the decision.
- The selected option.
- Reasonable alternatives considered.
- Positive and negative consequences.
- Conditions that should trigger reconsideration.

The initial DecisionAI ADRs are:

- ADR-001: Use a Modular Monolith for the Initial MVP.
- ADR-002: Use Deterministic Analytics as the Numerical Source of Truth.
- ADR-003: Isolate Gemini Behind an AI Boundary.
- ADR-004: Use SQLite for Initial Persistence.
- ADR-005: Prefer Simple Orchestration Before Multi-Agent Architecture.

Architecture decisions should be treated as explicit, reviewable engineering choices rather than permanent universal rules.

Decisions should be revisited when new product requirements, evaluation results, operational constraints, or measured system limitations invalidate their original assumptions.
