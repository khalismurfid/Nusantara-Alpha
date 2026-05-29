# Research: Nusantara Alpha Customer Prediction Product

## Decision: Streamlit for the customer-facing interface

**Rationale**: Streamlit supports a polished portfolio/demo product quickly
without creating a large frontend build system. It is sufficient for the core
journey: model selection, evidence inspection, stock selection, prediction
request, result interpretation, disclaimers, and unavailable states.

**Alternatives considered**: A custom React frontend would offer more interface
control but adds complexity before the product and safety flow are proven. A
notebook interface is fast for experiments but would read as an internal
research artifact rather than a customer-facing product.

## Decision: Prediction-first Streamlit layout for the MVP UX revision

**Rationale**: The first local product review found the skeleton functionally
present but too internal, text-heavy, and awkwardly worded for retail-style
users or reviewers. The next iteration should keep the same safety gates while
making the selected ticker, model signal, confidence, key context, and
limitations the primary visible content after valid selections. Concise
evidence remains before or alongside interpretation, while detailed
methodology and traceability become secondary or expandable.

**Alternatives considered**: Keeping the evidence panel as the dominant first
screen would satisfy review traceability but fail the customer-facing clarity
criteria. Building a new custom frontend would improve layout control but adds
complexity before the current Streamlit product flow is polished. Adding more
model capability first would not address the blocking MVP feedback.

## Decision: FastAPI for the service layer

**Rationale**: FastAPI gives explicit request/response contracts, validation,
OpenAPI documentation, and a clean service boundary between Streamlit and the
domain/ML modules. Route handlers can remain thin and delegate to services.

**Alternatives considered**: Calling ML modules directly from Streamlit is
simpler but violates the separation between UI and model logic. A heavier
backend framework is unnecessary for the first portfolio/demo version.

## Decision: Separate Python modules for ML and validation logic

**Rationale**: Feature engineering, model loading, prediction, validation, and
backtesting logic need independent tests and clear ownership. Paper-trading
evidence display can be supported without implementing full paper-trading logic
in the first skeleton. Keeping this logic outside UI and route handlers reduces
leakage risk and makes chronological controls easier to verify.

**Alternatives considered**: Putting ML orchestration in API route handlers
would speed early prototyping but would mix application and model concerns.
Putting it in UI code would make testing and reuse weaker.

## Decision: SQLite for lightweight metadata and prediction logs

**Rationale**: SQLite is enough for model catalogue metadata, evidence metadata,
supported universe, prediction logs, disclaimers, data availability, and
unsupported-stock interest in a portfolio/demo product. It avoids adding a
database server before the product needs one.

**Alternatives considered**: PostgreSQL is stronger for multi-user production
deployments but is overkill for the first version. Flat files are simple but
weaker for queryability, referential integrity, and traceability.

## Decision: MLflow for experiment tracking and model approval metadata

**Rationale**: MLflow is appropriate for runs, metrics, artifacts, model
versions, and model metadata. It gives a credible model tracking path for
reviewers while the customer-facing flow only sees approved curated models.

**Alternatives considered**: A custom registry in SQLite only would be simpler
but less suitable for model artifact traceability. A managed registry adds cost
and deployment requirements that are unnecessary for the first version.

## Decision: Local mock/sample flow first, public demo real approved models only

**Rationale**: Mock catalogue/evidence data and dummy predictions are useful for
building and testing the local product skeleton. The approved specification,
however, requires the public demo to use real approved models only and to block
prediction when no real approved model is available.

**Alternatives considered**: Using dummy predictions in the public demo would
make deployment easier but undermines portfolio credibility and violates the
clarified specification. Requiring real models before any local skeleton exists
would slow UI/API/storage safety work.

## Decision: Explicit prediction contracts with Pydantic and OpenAPI

**Rationale**: The product requires consistent prediction outputs with ticker,
target, model signal, confidence, context, limitations, model identity,
timestamps, evidence reference, and disclaimer. Pydantic schemas and OpenAPI
contracts make this testable and clear across UI/API boundaries.

**Alternatives considered**: Free-form JSON or text would be faster initially
but would be harder to validate for traceability, disclaimers, and uncertainty.

## Decision: Chronological validation as first-class ML-safety behavior

**Rationale**: Equity prediction workflows are invalid if feature engineering,
validation, backtesting, paper trading, or prediction uses future information.
Dedicated validators should check data-as-of timestamps, prediction timestamps,
time-ordered splits, and no preprocessing fit on validation/test/future data.

**Alternatives considered**: Relying on developer discipline or model internals
would leave the highest-risk behavior under-tested and difficult to review.

## Decision: Public/demo data governance through approved data modes

**Rationale**: Public deployment must avoid secrets, credentials, private
datasets, proprietary files, and unrestricted internal artifacts. Public demo
predictions may use public, delayed, static, or otherwise approved
non-sensitive data with a real approved model, and must show data-as-of and
limitations.

**Alternatives considered**: Shipping private/raw data would create legal and
ethical risk. Hiding data limitations would violate honest uncertainty and
academic integrity.

## Decision: Fail-closed model approval authority across MLflow and SQLite

**Rationale**: MLflow is the source for model artifacts, metrics, run metadata,
and registry metadata, while SQLite is the customer-facing catalogue and
public-demo eligibility store. If they disagree on approval status, model
version, artifact URI, supported universe, or public-demo eligibility, the
customer-facing surface must fail closed by hiding the model, blocking
prediction, logging the conflict, and showing an unavailable-model message.

**Alternatives considered**: Trusting either MLflow or SQLite unconditionally
would create accidental model exposure risk. Showing a warning while still
allowing prediction would weaken curated model access and public-demo safety.

## Decision: Feature timestamp is required for prediction traceability

**Rationale**: Data-as-of timestamps alone do not prove that feature generation
preserved time order. Prediction outputs and logs must include a
feature-generation timestamp, and validation must block missing or future-dated
feature timestamps.

**Alternatives considered**: Inferring feature timing from data-as-of would be
simpler but less auditable. Keeping feature timestamps only in internal logs
would weaken reviewer traceability.

## Decision: Required evidence must be loaded before prediction

**Rationale**: Approved model and supported ticker checks are insufficient if
required evidence is missing, stale, unavailable, or not loaded in the service.
Prediction requests should fail before model invocation when evidence cannot be
shown and traced.

**Alternatives considered**: Letting prediction proceed while evidence loads
later would violate evidence-before-prediction. Relying only on UI flow order
would leave direct API calls under-protected.

## Decision: Public demo has full and degraded release modes

**Rationale**: Public-demo success requires at least one real approved model and
one approved non-sensitive data source. When those gates are unavailable, the
app may still be deployed for review as a degraded demo showing the flow and
unavailable states, but it must not claim full prediction availability.

**Alternatives considered**: Blocking deployment entirely would reduce review
access to the product flow. Claiming full availability without real approved
model/data gates would violate the clarified specification.

## Decision: Full paper-trading logic is deferred

**Rationale**: The specification requires paper-trading evidence to be displayed
separately when available, but the first skeleton should focus on model
catalogue, evidence metadata, prediction contracts, logging, disclaimers, and
safety behavior. Full paper-trading logic should wait until evidence exists and
the core flow is stable.

**Alternatives considered**: Building paper-trading logic in the first skeleton
would increase complexity before the core product journey is reliable. Removing
paper-trading display entirely would miss an optional evidence path required by
the specification when evidence exists.

## Decision: Docker Compose where practical and Oracle Cloud Free Tier as preferred public target

**Rationale**: Docker Compose gives repeatable local/server startup for the
Streamlit app and FastAPI service without Kubernetes or production
orchestration. Oracle Cloud Free Tier can host a small public demo URL for
reviewers at low or no cost.

**Alternatives considered**: Manual process setup on a VM is simpler at first
but more fragile for reviewers and future setup. Kubernetes, load balancers,
autoscaling, and paid production infrastructure are outside first-version
scope.

## Decision: pytest across backend, storage, contracts, ML-safety, and deployment smoke checks

**Rationale**: pytest can cover the critical product and governance behaviors:
model filtering, public-demo model restrictions, unsupported stocks, stale or
missing evidence, prediction schema, disclaimers, data leakage prevention,
traceability, and no secret/private data exposure.

**Alternatives considered**: Manual QA alone would not satisfy the constitution.
Browser-only testing would miss ML-safety and validation logic.
