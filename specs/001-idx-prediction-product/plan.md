# Implementation Plan: Nusantara Alpha Customer Prediction Product

**Branch**: `001-idx-prediction-product` | **Date**: 2026-05-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-idx-prediction-product/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build Nusantara Alpha as a customer-facing educational Indonesian equity
prediction product. Users select a curated model, inspect evidence, choose one
or more supported IDX stocks, request a next-market-session prediction, and
interpret the output with confidence, context, limitations, timestamps,
traceability, and a clear educational/research disclaimer.

The first implementation prioritizes a working product skeleton with separated
Streamlit UI, FastAPI service, Python ML modules, SQLite metadata/logging, and
MLflow-backed model registry integration. Local development may use mock
catalogue/evidence data and dummy prediction outputs to build the flow, but the
public demo must use real approved models only. If a real approved model is not
available for the public demo, public prediction is blocked rather than falling
back to mock or dummy outputs.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Streamlit, FastAPI, Pydantic, Uvicorn, MLflow, Python
`sqlite3`, pandas, scikit-learn-compatible model interface, pytest, Docker or
Docker Compose where practical.

**Storage**: SQLite for model catalogue metadata, evidence metadata, supported
stock universe, data-availability state, registry sync status, prediction logs,
disclaimer versions, and aggregate unsupported-stock interest. MLflow stores
experiment runs, model artifacts, metrics, metadata, and approval status
references. Model artifacts remain separate from metadata and logs.

**Testing**: pytest for backend, domain, storage, ML-safety, validation,
contract, and deployment smoke tests. FastAPI tests use TestClient. Streamlit is
tested through app-facing client/service boundaries and manual quickstart smoke
checks.

**Target Platform**: Local developer environment for implementation and
experimentation; public review deployment on Oracle Cloud Free Tier Always Free
compute or another low-cost/free Linux server.

**Project Type**: Customer-facing web app plus API service and shared Python ML
modules.

**Performance Goals**: Demo catalogue/evidence views load in under 2 seconds in
local and public-demo environments. Valid prediction requests for up to 10
tickers return or clearly fail within 2 seconds for skeleton/mock flows and
within a documented model-specific budget for real models. A representative
reviewer can complete the main journey in under 3 minutes.

**Constraints**: No financial advice, no real-money execution, no brokerage
integration, no order placement, no position sizing, no portfolio allocation
advice, no guaranteed return claims, no private datasets or secrets in the
repository or public demo, no core ML logic in UI or API route handlers,
chronological integrity for all evidence and prediction workflows,
prediction outputs/logs must include data-as-of and feature-generation
timestamps, registry/catalogue conflicts fail closed, required evidence must be
loaded and valid before prediction, and public-demo predictions must come from
real approved models only.

**Scale/Scope**: Portfolio/demo product with a small curated model catalogue and
limited supported IDX universe. The first version avoids high availability,
paid production infrastructure, user accounts, broad market coverage, and
complex modelling until the core product, safety, and traceability flow works.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Document how this feature satisfies the Nusantara Alpha Constitution. Any
unchecked item MUST be resolved before implementation or recorded in Complexity
Tracking with rationale, mitigation, and follow-up work.

- [x] No Financial Advice: UI copy, API schemas, prediction outputs, evidence
      views, and tests use educational/research framing only. Forbidden terms
      such as buy/sell recommendations, guaranteed profit, position sizing, and
      allocation advice are blocked by copy review and automated phrase tests.
- [x] No Real-Money Execution: No brokerage connector, order route, execution
      workflow, or automated real-money decision path is included. Backtesting,
      paper-trading, and portfolio demonstration remain simulated and labelled.
- [x] Chronological Integrity: ML modules preserve time order in feature
      engineering, validation, backtesting, paper-trading evidence preparation,
      and prediction. Validators enforce data-as-of timestamp,
      feature-generation timestamp, prediction timestamp, and no
      future-information access. Missing or invalid feature timestamps block
      prediction with a clear error.
- [x] Market Data Integrity and Bias Control: Evidence and data-availability
      metadata capture stale data, missing sessions, corporate actions,
      delistings, trading halts, illiquidity, calendar alignment, ticker
      identity changes, and survivorship-bias assumptions when material.
- [x] Evidence Before Prediction: The Streamlit flow and API expose model
      evidence before prediction. Approved models require historical evidence,
      evaluation period, supported universe, known limitations, and traceability
      metadata. Prediction requests are blocked when required evidence is
      missing, stale, unavailable, or not loaded.
- [x] Honest Uncertainty: Prediction responses include Low/Medium/High
      confidence, plain-language uncertainty explanation, limitations, and
      evidence caveats. Weak or data-limited evidence is surfaced; missing
      required evidence blocks approval or prediction.
- [x] Curated Model Access: Customer-facing selectors read from an approved
      model catalogue backed by SQLite and MLflow metadata. If SQLite and
      MLflow disagree on approval status, model version, artifact URI,
      supported universe, or public-demo eligibility, the system fails closed:
      hide the model, block prediction, log the conflict, and show an
      unavailable-model message. Hidden, experimental, deprecated, unavailable,
      mock/demo-only, or unapproved models are blocked from the main flow and
      from public-demo predictions.
- [x] Reproducibility and Traceability: Prediction logs and outputs include
      model identifier/version, selected ticker, prediction target,
      data-as-of timestamp, feature-generation timestamp, prediction timestamp,
      disclaimer version, evidence reference, evaluation context, and
      success/failure status.
- [x] Separation of Concerns: Streamlit handles presentation only; FastAPI
      validates and orchestrates requests; shared modules own ML, validation,
      backtesting, paper trading, storage, registry, evidence, and governance
      logic. Route handlers do not contain core ML logic.
- [x] Testability: Planned tests cover model filtering, registry/catalogue
      conflict fail-closed behavior, unsupported stocks, prediction schemas,
      disclaimers, chronology/leakage utilities, missing or invalid feature
      timestamps, stale/missing/unavailable evidence, public-demo model
      restrictions, data governance, degraded public-demo release gates, and
      error handling.
- [x] User Clarity: The main journey remains choose model, inspect evidence,
      choose stock, request prediction, and understand risk. Technical details
      are available but secondary.
- [x] Data Governance: Secrets, credentials, private datasets, proprietary
      files, and unrestricted artifacts are excluded. Public demo uses real
      approved models with public, delayed, static, or otherwise approved
      non-sensitive data. Local mock/sample data is labelled and kept out of
      public predictions.
- [x] Simplicity Before Complexity: The first version uses a small set of
      modules, local SQLite, local MLflow, and optional Docker Compose. Oracle
      deployment is documented without high-availability production
      infrastructure. Paper-trading display support is planned, but full
      paper-trading logic is deferred until evidence exists and the core flow is
      stable.
- [x] Academic and Portfolio Integrity: Methodology, limitations, evidence
      periods, assumptions, data provenance, deployment limitations, and model
      approval criteria are documented and traceable.

## Recommended Architecture

```text
Reviewer/User
  -> Streamlit UI (`app_streamlit/`)
  -> FastAPI service (`backend/`)
  -> Application services and schemas
  -> Domain, validation, ML, storage, registry, evidence modules
  -> SQLite metadata/log store + MLflow model/artifact registry
```

### Component Responsibilities

- `app_streamlit/`: Customer-facing screens, disclaimers, evidence display,
  stock selection, prediction results, unavailable states, and API client code.
  It must not contain training, feature-engineering, backtesting, or prediction
  model logic.
- `backend/`: FastAPI app, route declarations, request/response schemas, and
  application services. Route handlers validate input and delegate to services.
- `ml/`: Feature engineering, model loading, prediction, validation, and
  backtesting utilities. These modules own chronological safety and leakage
  prevention behavior. Full paper-trading logic is deferred; the first version
  only supports display of paper-trading evidence when available.
- `storage/`: SQLite schema setup, repositories, and query helpers for model
  metadata, evidence metadata, stock universe, prediction logs, disclaimers, and
  unsupported-stock interest.
- `model_registry/`: MLflow integration and model approval/catalogue sync.
  Public-demo eligibility is derived from real approved model metadata, not
  mock or demo-only entries. Registry sync conflicts or stale/incomplete sync
  states fail closed.
- `data/`: Small local sample/mock data for development and tests only. Public
  demo data must be public, delayed, static, or otherwise approved
  non-sensitive data.
- `docs/`: Architecture, methodology, limitations, model approval process,
  evaluation notes, and deployment documentation.
- `deployment/`: Docker/Docker Compose assets, environment variable examples,
  Oracle Cloud Free Tier setup notes, and public-demo smoke-check instructions.

## Data And Model Flow

1. Model artifacts, metrics, and registry metadata are tracked in MLflow.
   Customer-facing catalogue records and public-demo eligibility are stored in
   SQLite.
2. Registry sync compares MLflow and SQLite for approval status, model version,
   artifact URI, supported universe, and public-demo eligibility. Any conflict,
   stale sync, or incomplete sync fails closed: hide the model, block
   prediction, log the conflict, and show a clear unavailable-model message.
3. The API lists only approved curated models for the customer-facing flow.
   Public-demo mode additionally requires `model_origin=real`, a current
   registry sync status, and approved public-demo eligibility.
4. Evidence retrieval returns historical metrics, evaluation period, supported
   universe, limitations, data-quality notes, paper-trading evidence when
   available, evidence-as-of timestamp, load status, and
   historical-performance caveat.
5. Stock selection checks the selected model's supported universe and data
   availability. Unsupported stocks are shown as unavailable, block prediction
   until removed or replaced, and are tracked only as aggregate non-personal
   support-interest signals.
6. Prediction requests validate model approval, registry sync consistency,
   public-demo eligibility, stock support, required evidence availability,
   evidence freshness/load status, data freshness, chronology, and output schema
   requirements before invoking prediction services. Approved model plus
   supported ticker is not enough; required evidence must also be available and
   loaded.
7. ML modules load the selected model artifact, construct features using only
   information available at the data-as-of timestamp, produce a
   feature-generation timestamp, generate the model signal, and return
   confidence/uncertainty and limitations. Missing or invalid feature timestamp
   fails prediction with a clear error.
8. The API wraps model output in the required prediction contract, adds
   disclaimer text, traceability metadata, evidence reference, data-as-of
   timestamp, feature-generation timestamp, prediction timestamp, and logs
   success or failure to SQLite.
9. Streamlit renders the result in plain language and keeps the disclaimer,
   confidence explanation, context, limitations, timestamps, and traceability
   visible.

## Public Demo Release Gate

Public demo success requires at least one real approved model, current
registry/catalogue sync, required model evidence, and one approved
non-sensitive data source. If any release gate is missing, the deployed app may
run only as a degraded demo. A degraded demo may show the product flow,
evidence-unavailable states, stock selection behavior, and explanatory
limitations, but it must not claim full prediction availability or expose mock
models, dummy outputs, private datasets, credentials, proprietary files, or
unrestricted artifacts.

## Project Structure

### Documentation (this feature)

```text
specs/001-idx-prediction-product/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md             # Phase 2 output from /speckit-tasks
```

### Source Code (repository root)

```text
app_streamlit/
├── app.py
├── pages/
├── components/
├── clients/
└── copy/

backend/
├── main.py
├── routers/
├── schemas/
├── services/
└── dependencies.py

ml/
├── features/
├── prediction/
├── validation/
├── backtesting/
└── loading/

storage/
├── schema.sql
├── database.py
├── repositories.py
└── seed_local_demo.py

model_registry/
├── mlflow_client.py
├── catalogue_sync.py
├── approval.py
└── conflict_log.py

data/
├── sample/
└── README.md

docs/
├── architecture.md
├── methodology.md
├── limitations.md
├── model-approval.md
└── deployment-oracle.md

deployment/
├── Dockerfile.backend
├── Dockerfile.streamlit
├── compose.yaml
├── env.example
└── oracle-cloud-free-tier.md

tests/
├── unit/
├── integration/
├── contract/
├── ml_safety/
└── deployment/
```

**Structure Decision**: Use a small Python monorepo with explicit UI, API, ML,
storage, registry, data, docs, deployment, and tests boundaries. This keeps
responsibilities separate without introducing microservices, queues, distributed
training infrastructure, production orchestration, or paid cloud dependencies
for the first version.

## Implementation Phases

### Phase 1: Product Skeleton

- Create the project structure.
- Create the Streamlit flow for model selection, evidence, stock selection,
  prediction result, disclaimer, and unavailable states.
- Create the FastAPI app skeleton with health, models, evidence, stocks, and
  prediction routes.
- Use local-only mock model catalogue, mock evidence catalogue, and dummy
  prediction output to exercise the flow.
- Label local mock/dummy outputs as development-only and prevent them from being
  public-demo eligible.
- Focus on model catalogue, evidence metadata, prediction contract, prediction
  logging, and disclaimer behavior. Do not implement full paper-trading logic in
  this phase.

### Phase 2: Contracts And Storage

- Define Pydantic request/response schemas and OpenAPI contract.
- Add SQLite tables for model catalogue, evidence metadata, supported stocks,
  prediction logs, disclaimers, data availability, registry sync status,
  registry conflict logs, and unsupported-stock interest.
- Connect Streamlit to FastAPI through client functions.
- Add validation for approved models, registry/catalogue consistency,
  supported tickers, required evidence availability/load status, feature
  timestamp validity, and prediction output shape.
- Add prediction logging and traceability metadata, including data-as-of
  timestamp, feature-generation timestamp, and prediction timestamp.

### Phase 3: Tests And Safety Checks

- Test approved-only model filtering.
- Test fail-closed behavior when MLflow and SQLite disagree on approval status,
  model version, artifact URI, supported universe, or public-demo eligibility.
- Test stale or incomplete registry synchronization hides the model and blocks
  prediction.
- Test public-demo blocking for mock/demo-only/dummy models.
- Test unsupported ticker handling.
- Test prediction response structure and disclaimer presence.
- Test prediction blocked when required evidence is missing, stale, unavailable,
  or not loaded.
- Test chronological/leakage-safety utilities, including no future features and
  no preprocessing fit on validation/test/future data.
- Test missing or invalid feature-generation timestamp fails prediction with a
  clear error.
- Test public-demo data governance, release gate behavior, degraded demo labels,
  and unavailable states.

### Phase 4: MLflow And Real Model Integration

- Add MLflow metadata/artifact integration.
- Load approved model metadata and artifacts through `model_registry/`.
- Implement fail-closed reconciliation between MLflow registry metadata and the
  SQLite customer-facing catalogue.
- Connect prediction service to real approved model artifacts.
- Keep feature generation, validation, and prediction testable outside API route
  handlers and UI code.
- Remove dummy fallback from any public-demo path. Keep dummy prediction only for
  local development tests if still useful.

### Phase 5: Evidence And Paper-Trading Display

- Show real or approved evidence, including backtest metrics, evaluation period,
  supported universe, limitations, and data-quality notes.
- Show paper-trading evidence separately when available.
- Defer full paper-trading module implementation until paper-trading evidence
  exists and the core product flow is stable.
- Make weak, stale, missing, or data-limited evidence visible and actionable.
- Add plain-language limitation summaries for non-expert users.

### Phase 6: Public Demo Deployment

- Containerize where practical with Docker or Docker Compose.
- Prepare Oracle Cloud Free Tier deployment guide.
- Add environment variable documentation for paths, model registry, SQLite,
  MLflow tracking, public-demo mode, and external credentials if ever needed.
- Use real approved model artifacts and public/delayed/static/approved
  non-sensitive data only.
- Verify at least one real approved model and one approved non-sensitive data
  source before claiming full public prediction availability.
- If no real approved model or approved data source is available, deploy only a
  degraded demo with clear limitations and unavailable prediction state rather
  than mock or dummy predictions.
- Verify a reviewer can open the public URL and complete the core flow with a
  real approved model.

## Testing Strategy

- Unit tests: domain rules, disclaimer copy, model approval decisions,
  fail-closed registry decisions, confidence labels, data availability, feature
  timestamp validation, and unsupported stock handling.
- Contract tests: FastAPI response schemas for models, evidence, stocks,
  predictions, health, and demo status, including data-as-of and
  feature-generation timestamps.
- Integration tests: Streamlit client to API service flow, SQLite repositories,
  MLflow catalogue sync, conflict logging, and prediction logging.
- ML-safety tests: chronological split preservation, feature timestamp checks,
  no future labels/features, no preprocessing fit on validation/test/future
  data, stale/missing data blocking, and evidence/prediction traceability.
- Deployment tests: container health checks, environment variable validation,
  public-demo model restrictions, degraded demo release gates, no
  secrets/private data in demo responses, and core flow smoke test.

## Deployment Strategy

- Local development runs Streamlit and FastAPI separately.
- Docker Compose is used where practical for repeatable local and server demo
  startup.
- Oracle Cloud Free Tier Always Free compute is the preferred public demo
  target; another low-cost/free Linux server is acceptable if Oracle capacity or
  account access blocks deployment.
- Runtime configuration uses environment variables and `deployment/env.example`.
- Full public prediction availability requires at least one real approved model,
  current registry sync, required evidence, and one approved non-sensitive data
  source. Otherwise the app may run only as a degraded demo with visible
  limitations.
- Public demo must not include private datasets, API keys, proprietary files,
  unrestricted artifacts, or dummy prediction outputs.
- Public demo may use public, delayed, static, or otherwise approved
  non-sensitive data with a real approved model and visible data-as-of/demo
  limitations.
- High availability, autoscaling, paid production deployment, user accounts, and
  enterprise infrastructure are out of scope for the first version.

## Key Risks And Mitigations

- Financial-advice wording risk: centralize disclaimer/copy constants, test
  forbidden phrases, and avoid buy/sell/recommendation language.
- Data leakage risk: require timestamped feature inputs, time-ordered
  validation helpers, feature-generation timestamp checks, and ML-safety tests
  before model outputs become approved.
- Registry mismatch risk: compare SQLite catalogue and MLflow metadata before
  display or prediction; fail closed and log conflicts.
- Evidence-gating risk: require service-level evidence availability/load checks
  before prediction; supported ticker alone is insufficient.
- Public-demo mock leakage risk: add public-demo eligibility checks and tests
  that block mock/demo-only/dummy models.
- Weak evidence overstatement risk: require evidence status, limitation
  summaries, data-quality notes, and historical-performance caveats before
  prediction.
- Data governance risk: keep approved data inventory in docs, use env vars for
  secrets/paths, and test that demo responses do not expose restricted content.
- Over-engineering risk: keep first version to one Streamlit app, one FastAPI
  service, local SQLite, local MLflow, simple deployment docs, and deferred
  paper-trading logic.

## Complexity Tracking

No constitution violations are planned. The separated directories are required
to enforce UI/API/ML/storage/registry boundaries and test leakage-sensitive
behavior. Docker/Compose and Oracle deployment documentation are included only
to support public portfolio review, not to introduce high-availability
production infrastructure.
