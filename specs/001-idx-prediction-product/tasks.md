# Tasks: Nusantara Alpha Customer Prediction Product

**Input**: Design documents from `/specs/001-idx-prediction-product/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

**Tests**: Required for constitution-critical behaviour: no financial advice, no real-money execution, chronological integrity, market-data quality and bias controls, evidence-before-prediction, curated model selection, prediction output structure, feature timestamp traceability, data governance, public-demo release gates, and error handling.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after shared setup and foundation work.

## Phase 1: Setup

**Purpose**: Initialize the repository structure, dependency metadata, and local configuration files.

- [X] T001 Create planned directory placeholders in `app_streamlit/.gitkeep`, `backend/.gitkeep`, `ml/.gitkeep`, `storage/.gitkeep`, `model_registry/.gitkeep`, `data/sample/.gitkeep`, `docs/.gitkeep`, `deployment/.gitkeep`, and `tests/.gitkeep`
- [X] T002 Define Python project metadata and dependencies for Streamlit, FastAPI, Pydantic, Uvicorn, MLflow, pandas, scikit-learn-compatible interfaces, pytest, and PyYAML in `pyproject.toml`
- [X] T003 [P] Add repository ignore rules for virtual environments, SQLite databases, MLflow runs, private data, secrets, and local environment files in `.gitignore`
- [X] T004 [P] Add non-secret runtime configuration example for API URL, SQLite path, MLflow URI, runtime context, data paths, and public demo URL in `deployment/env.example`
- [X] T005 [P] Create package marker files in `app_streamlit/__init__.py`, `backend/__init__.py`, `backend/routers/__init__.py`, `backend/schemas/__init__.py`, `backend/services/__init__.py`, `ml/__init__.py`, `storage/__init__.py`, and `model_registry/__init__.py`
- [X] T006 [P] Document local-only sample/mock data rules and public-demo data restrictions in `data/README.md`
- [X] T007 [P] Create pytest package layout markers in `tests/unit/__init__.py`, `tests/integration/__init__.py`, `tests/contract/__init__.py`, `tests/ml_safety/__init__.py`, and `tests/deployment/__init__.py`

---

## Phase 2: Foundational

**Purpose**: Build shared contracts, storage, validation, registry, copy, and service foundations that block all user stories.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T008 Define runtime settings loader with environment variables and safe defaults in `backend/config.py`
- [X] T009 Define educational disclaimer text, disclaimer version, approved prediction vocabulary, and forbidden advice phrases in `app_streamlit/copy/disclaimers.py`
- [X] T010 [P] Define Pydantic schemas matching `contracts/openapi.yaml` for health, demo status, models, evidence, stocks, prediction requests, prediction outputs, blocked predictions, unsupported-stock interest, and errors in `backend/schemas/contracts.py`
- [X] T011 [P] Define SQLite schema for model catalogue, evidence metadata, supported stocks, data availability, registry sync state, registry conflicts, prediction logs, disclaimers, unsupported-stock interest, and deployable data assets in `storage/schema.sql`
- [X] T012 Implement SQLite connection, initialization, transaction, and row mapping helpers in `storage/database.py`
- [X] T013 Implement repository methods for catalogue, evidence, stock universe, data availability, disclaimers, prediction logs, unsupported-stock interest, registry conflicts, and deployable assets in `storage/repositories.py`
- [X] T014 Seed local-only catalogue, evidence, stock, data availability, disclaimer, and dummy prediction fixtures with public-demo eligibility disabled in `storage/seed_local_demo.py`
- [X] T015 [P] Implement MLflow metadata access wrapper for model run metadata, artifact URI, metrics, and registry metadata in `model_registry/mlflow_client.py`
- [X] T016 Implement fail-closed model approval reconciliation between SQLite and MLflow for approval status, model version, artifact URI, supported universe, and public-demo eligibility in `model_registry/approval.py`
- [X] T017 Implement conflict recording and sanitized user-facing unavailable-model messages in `model_registry/conflict_log.py`
- [X] T018 [P] Implement chronological validators for data-as-of timestamps, feature-generation timestamps, prediction timestamps, time-ordered splits, and future-information checks in `ml/validation/chronology.py`
- [X] T019 [P] Implement market-data quality and bias flag validation for stale data, missing sessions, corporate actions, delistings, trading halts, illiquidity, calendar alignment, ticker identity changes, and survivorship assumptions in `ml/validation/market_data.py`
- [X] T020 [P] Implement feature generation interface that returns feature payloads plus `feature_generation_timestamp` in `ml/features/generation.py`
- [X] T021 [P] Implement model loading interface that loads approved artifacts only through validated model metadata in `ml/loading/model_loader.py`
- [X] T022 Implement prediction engine interface that accepts loaded model, feature payload, timestamps, and ticker context without UI/API dependencies in `ml/prediction/engine.py`
- [X] T023 Implement thin FastAPI app construction, exception handling, and router registration in `backend/main.py`
- [X] T024 [P] Create router module stubs for health, demo, models, evidence, stocks, unsupported-stock interest, and predictions in `backend/routers/health.py`, `backend/routers/demo.py`, `backend/routers/models.py`, `backend/routers/evidence.py`, `backend/routers/stocks.py`, `backend/routers/unsupported_stock_interest.py`, and `backend/routers/predictions.py`
- [X] T025 [P] Create Streamlit API client shell for health, demo status, models, evidence, stocks, unsupported-stock interest, and predictions in `app_streamlit/clients/api.py`
- [X] T026 [P] Create reusable pytest fixtures for temporary SQLite databases, seeded local data, runtime contexts, and FastAPI TestClient in `tests/conftest.py`

**Checkpoint**: Shared contracts, storage, registry, validation, and routing foundations are ready.

---

## Phase 3: User Story 1 - Explore a Supported Prediction (Priority: P1) MVP

**Goal**: A user can see educational framing, choose an approved model, inspect evidence, choose supported IDX stocks, request a next-market-session prediction, and receive a structured output with confidence, limitations, timestamps, traceability, and disclaimer.

**Independent Test**: Complete the happy-path journey with one approved model and one supported IDX stock, then verify all required output fields are present and no financial-advice language appears.

### Tests for User Story 1

- [X] T027 [P] [US1] Add contract tests for `/models`, `/models/{model_id}/evidence`, `/models/{model_id}/stocks`, and `/predictions` happy-path schemas in `tests/contract/test_prediction_flow_contract.py`
- [X] T028 [P] [US1] Add integration test for the full approved-model evidence-stock-prediction journey through FastAPI services in `tests/integration/test_supported_prediction_flow.py`
- [X] T029 [P] [US1] Add copy-safety tests for disclaimer presence and forbidden advice phrases in model, evidence, prediction, and error text in `tests/unit/test_disclaimer_copy.py`
- [X] T030 [P] [US1] Add prediction output traceability tests for model identity, data-as-of timestamp, feature-generation timestamp, prediction timestamp, evidence reference, evaluation context, and disclaimer version in `tests/contract/test_prediction_traceability.py`
- [X] T031 [P] [US1] Add ML-safety tests that reject missing or future-dated feature-generation timestamps in `tests/ml_safety/test_feature_timestamp_validation.py`
- [X] T032 [P] [US1] Add prediction log tests for successful predictions storing selected tickers, model version, data-as-of timestamp, feature-generation timestamp, prediction timestamp, confidence, disclaimer version, and output summary in `tests/integration/test_prediction_logging.py`
- [X] T033 [P] [US1] Add Streamlit client boundary tests for model, evidence, stock, and prediction API calls in `tests/unit/test_streamlit_api_client.py`

### Implementation for User Story 1

- [X] T034 [P] [US1] Implement approved-model listing service with local-only mock filtering and public-demo eligibility checks in `backend/services/model_service.py`
- [X] T035 [P] [US1] Implement evidence retrieval service that returns loaded evidence summary before prediction in `backend/services/evidence_service.py`
- [X] T036 [P] [US1] Implement supported stock lookup service for a selected model universe in `backend/services/stock_service.py`
- [X] T037 [US1] Implement prediction orchestration service with model approval, evidence, stock, data, chronology, feature timestamp, and output-contract validation in `backend/services/prediction_service.py`
- [X] T038 [US1] Implement `/models` endpoint using the model service in `backend/routers/models.py`
- [X] T039 [US1] Implement `/models/{model_id}/evidence` endpoint using the evidence service in `backend/routers/evidence.py`
- [X] T040 [US1] Implement `/models/{model_id}/stocks` endpoint using the stock service in `backend/routers/stocks.py`
- [X] T041 [US1] Implement `/predictions` endpoint using the prediction service in `backend/routers/predictions.py`
- [X] T042 [P] [US1] Implement local-only dummy predictor adapter that cannot run in `public_demo` context in `ml/prediction/local_dummy.py`
- [X] T043 [US1] Implement prediction logging for successful, blocked, and failed attempts in `backend/services/prediction_logging_service.py`
- [X] T044 [P] [US1] Implement Streamlit disclaimer and product framing component in `app_streamlit/components/framing.py`
- [X] T045 [P] [US1] Implement Streamlit prediction result renderer with signal, confidence, context, limitations, timestamps, traceability, and disclaimer in `app_streamlit/components/prediction_result.py`
- [X] T046 [US1] Implement Streamlit main journey for model selection, evidence preview, stock selection, prediction request, and result display in `app_streamlit/app.py`
- [X] T047 [US1] Wire Streamlit API client methods for approved models, evidence, stocks, and predictions in `app_streamlit/clients/api.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Review Model Evidence and Limitations (Priority: P2)

**Goal**: A reviewer can inspect model evidence, limitations, evaluation period, supported universe, data-quality caveats, and methodology context before interpreting prediction output.

**Independent Test**: Select each approved model and verify evidence, limitations, evaluation period, supported universe, historical-versus-future distinction, and data-quality notes are visible before prediction.

### Tests for User Story 2

- [X] T048 [P] [US2] Add contract tests for complete, weak, stale, data-limited, missing, unavailable, and not-loaded evidence responses in `tests/contract/test_model_evidence_contract.py`
- [X] T049 [P] [US2] Add integration test that prediction is blocked when required evidence is missing, stale, unavailable, or not loaded in `tests/integration/test_evidence_before_prediction.py`
- [X] T050 [P] [US2] Add evidence display tests for historical performance caveat, evaluation period, supported universe, limitations, and data-quality notes in `tests/unit/test_evidence_presentation.py`
- [X] T051 [P] [US2] Add paper-trading display tests that show paper-trading evidence separately when present and omit full paper-trading logic when absent in `tests/unit/test_paper_trading_evidence_display.py`
- [X] T052 [P] [US2] Add ML-safety tests that evidence generation and evidence timestamps do not use future information in `tests/ml_safety/test_evidence_chronology.py`

### Implementation for User Story 2

- [X] T053 [US2] Extend evidence repository queries for key metrics, performance summaries, limitations, data-quality notes, evidence status, evidence load status, evidence-as-of timestamp, and data source mode in `storage/repositories.py`
- [X] T054 [US2] Extend evidence service to distinguish complete, weak, data-limited, missing, stale, unavailable, and not-loaded evidence in `backend/services/evidence_service.py`
- [X] T055 [US2] Add service-level prediction gate requiring loaded required evidence before model invocation in `backend/services/prediction_service.py`
- [X] T056 [P] [US2] Implement Streamlit evidence panel with metrics, evaluation period, supported universe, limitations, data-quality notes, caveat, and evidence status labels in `app_streamlit/components/evidence_panel.py`
- [X] T057 [P] [US2] Implement separate paper-trading evidence display component without implementing paper-trading generation logic in `app_streamlit/components/paper_trading_evidence.py`
- [X] T058 [US2] Integrate evidence panel and evidence-before-prediction state into the main Streamlit flow in `app_streamlit/app.py`
- [X] T059 [P] [US2] Document methodology, evidence interpretation, historical-performance caveat, and limitations in `docs/methodology.md`
- [X] T060 [P] [US2] Document known model, data-quality, bias, and public-demo limitations in `docs/limitations.md`

**Checkpoint**: User Story 2 evidence review works independently and predictions are blocked when required evidence is not loaded and valid.

---

## Phase 5: User Story 3 - Handle Unsupported or Unavailable Prediction States (Priority: P3)

**Goal**: A user receives clear unavailable or error states for unavailable models, unsupported stocks, missing evidence, missing or stale data, registry conflicts, chronology violations, failed predictions, and invalid responses without receiving misleading prediction output.

**Independent Test**: Attempt each invalid request type and verify prediction is blocked, the reason is plain-language, next steps are shown when useful, and blocked attempts are logged safely.

### Tests for User Story 3

- [X] T061 [P] [US3] Add tests that no approved model hides unavailable, hidden, deprecated, experimental, demo-only, mock, or unapproved models from customer-facing lists in `tests/unit/test_model_filtering.py`
- [X] T062 [P] [US3] Add tests that MLflow/SQLite conflicts and stale or incomplete registry sync hide models, block prediction, log conflicts, and return unavailable-model messages in `tests/integration/test_registry_fail_closed.py`
- [X] T063 [P] [US3] Add tests that unsupported stock searches show unavailable reasons, block prediction until removed, and record aggregate non-personal interest in `tests/integration/test_unsupported_stock_handling.py`
- [X] T064 [P] [US3] Add tests that missing or stale data, invalid chronology, and material market-data risks block or withhold unreliable predictions in `tests/ml_safety/test_data_availability_and_quality.py`
- [X] T065 [P] [US3] Add contract tests for no model selected, no stock selected, unavailable model, failed prediction generation, empty prediction response, and invalid prediction response in `tests/contract/test_error_responses.py`
- [X] T066 [P] [US3] Add tests that error and unavailable messages preserve educational framing and avoid advice wording in `tests/unit/test_error_copy_safety.py`
- [X] T067 [P] [US3] Add tests that blocked and failed prediction logs omit secrets, credentials, private data, and personalized investment intent in `tests/integration/test_safe_failure_logging.py`

### Implementation for User Story 3

- [X] T068 [P] [US3] Implement data availability service for freshness, missing data, chronology status, and material quality flags in `backend/services/data_availability_service.py`
- [X] T069 [P] [US3] Implement unsupported-stock interest service that stores aggregate non-personal counts only in `backend/services/unsupported_stock_interest_service.py`
- [X] T070 [US3] Implement `/unsupported-stock-interest` endpoint using the aggregate interest service in `backend/routers/unsupported_stock_interest.py`
- [X] T071 [US3] Implement fail-closed catalogue synchronization service that compares MLflow and SQLite and writes sanitized conflicts in `model_registry/catalogue_sync.py`
- [X] T072 [US3] Extend prediction service with explicit blocked reasons for unsupported stock, stale data, missing data, missing evidence, stale evidence, unavailable evidence, evidence not loaded, chronology violation, missing feature timestamp, invalid feature timestamp, unreliable or untraceable output, unavailable model, registry conflict, stale sync, incomplete sync, public-demo gate failure, public-demo model unavailable, mock model blocked, and invalid prediction response in `backend/services/prediction_service.py`
- [X] T073 [P] [US3] Implement Streamlit unavailable/error state component with reason and next-step text in `app_streamlit/components/unavailable_state.py`
- [X] T074 [US3] Extend Streamlit stock search and selection to show unsupported or temporarily unavailable stocks, record aggregate interest, and block prediction until invalid stocks are removed in `app_streamlit/app.py`
- [X] T075 [US3] Extend prediction logging to record blocked and failed attempts with sanitized error messages and available traceability timestamps in `backend/services/prediction_logging_service.py`
- [X] T076 [US3] Extend storage seed data with unsupported stock, stale data, missing data, registry conflict, stale sync, incomplete sync, and invalid response fixtures in `storage/seed_local_demo.py`

**Checkpoint**: User Story 3 invalid-state handling is independently testable without exposing misleading predictions.

---

## Phase 6: User Story 4 - Access a Public Portfolio Demo (Priority: P4)

**Goal**: A reviewer can open a public URL and use the core journey with a real approved model and approved non-sensitive data, or see a clearly labelled degraded demo when release gates are not satisfied.

**Independent Test**: Run the app in `public_demo` context and verify real approved model/data gates, disclaimer persistence, data-as-of/demo limitation display, no mock/dummy public predictions, and no restricted data exposure.

### Tests for User Story 4

- [X] T077 [P] [US4] Add contract tests for `/demo/status` full, degraded, and unavailable responses in `tests/contract/test_demo_status_contract.py`
- [X] T078 [P] [US4] Add deployment tests for public-demo release gate requiring one real approved model, current registry sync, loaded evidence, and one approved non-sensitive data source in `tests/deployment/test_public_demo_release_gate.py`
- [X] T079 [P] [US4] Add tests that public-demo mode blocks local mock models, demo-only models, experimental models, and dummy prediction outputs in `tests/deployment/test_public_demo_model_restrictions.py`
- [X] T080 [P] [US4] Add tests that degraded demo labels and unavailable prediction states are shown when release gates fail in `tests/deployment/test_degraded_demo_behavior.py`
- [X] T081 [P] [US4] Add data-governance tests that public-demo responses, logs, examples, and downloadable content do not expose secrets, credentials, private datasets, proprietary files, restricted source data, or unrestricted artifacts in `tests/deployment/test_public_demo_data_governance.py`
- [X] T082 [P] [US4] Add public-demo smoke test for the reviewer journey through deployed service boundaries in `tests/deployment/test_public_demo_smoke.py`

### Implementation for User Story 4

- [X] T083 [US4] Implement demo status service that evaluates app status, API status, public prediction availability, release status, real approved model availability, approved data source availability, data-as-of timestamp, demo limitations, and release-gate reasons in `backend/services/demo_status_service.py`
- [X] T084 [US4] Implement `/demo/status` endpoint using the demo status service in `backend/routers/demo.py`
- [X] T085 [US4] Implement deployable data asset repository queries and public-demo allowed classification checks in `storage/repositories.py`
- [X] T086 [P] [US4] Implement Streamlit public-demo banner with full, degraded, and unavailable demo limitation labels in `app_streamlit/components/demo_banner.py`
- [X] T087 [US4] Integrate demo status banner and public-demo unavailable prediction state into the main Streamlit app in `app_streamlit/app.py`
- [X] T088 [P] [US4] Create backend container definition with non-root runtime, environment variable configuration, and no bundled private data in `deployment/Dockerfile.backend`
- [X] T089 [P] [US4] Create Streamlit container definition with environment variable configuration and no bundled private data in `deployment/Dockerfile.streamlit`
- [X] T090 [US4] Create Docker Compose stack for FastAPI, Streamlit, SQLite path mounts, MLflow tracking URI, and runtime context in `deployment/compose.yaml`
- [X] T091 [P] [US4] Document Oracle Cloud Free Tier deployment steps, firewall ports, environment setup, release gate checks, degraded-demo behavior, and rollback notes in `deployment/oracle-cloud-free-tier.md`
- [X] T092 [P] [US4] Document approved public-demo data inventory, allowed asset classifications, and excluded restricted assets in `docs/deployment-oracle.md`

**Checkpoint**: User Story 4 public-demo behavior is independently testable in local public-demo mode and ready for server deployment once real approved assets exist.

---

## Phase 7: Polish and Cross-Cutting Concerns

**Purpose**: Final documentation, audit, cleanup, and validation across all stories.

- [X] T093 [P] Add architecture documentation for UI/API/ML/storage/registry boundaries and request flow in `docs/architecture.md`
- [X] T094 [P] Add model approval process documentation covering MLflow metadata, SQLite catalogue status, fail-closed conflicts, and public-demo eligibility in `docs/model-approval.md`
- [X] T095 [P] Add public reviewer validation checklist and evidence traceability checklist in `docs/reviewer-checklist.md`
- [X] T096 [P] Add project overview, local setup summary, and no-financial-advice scope statement in `README.md`
- [X] T097 Run forbidden-phrase and disclaimer audit across `app_streamlit/`, `backend/`, `docs/`, and `tests/` and record results in `docs/copy-safety-audit.md`
- [X] T098 Run data-governance audit for secrets, private paths, private datasets, proprietary files, and unrestricted artifacts across `data/`, `deployment/`, `docs/`, and `storage/` and record results in `docs/data-governance-audit.md`
- [X] T099 Run chronological and feature timestamp validation review across `ml/`, `backend/services/`, and `tests/ml_safety/` and record results in `docs/ml-safety-review.md`
- [X] T100 Run quickstart manual validation flow and record pass/fail notes in `docs/quickstart-validation.md`
- [X] T101 Run full pytest suite for `tests/unit/`, `tests/contract/`, `tests/integration/`, `tests/ml_safety/`, and `tests/deployment/` and record final results in `docs/test-report.md`

---

## Dependencies and Execution Order

### Phase Dependencies

- Phase 1 Setup has no dependencies.
- Phase 2 Foundational depends on Phase 1 completion and blocks every user story.
- Phase 3 User Story 1 depends on Phase 2 and is the MVP.
- Phase 4 User Story 2 depends on Phase 2 and may run alongside User Story 1 after shared foundations exist.
- Phase 5 User Story 3 depends on Phase 2 and may run alongside User Stories 1 and 2 after shared foundations exist.
- Phase 6 User Story 4 depends on Phase 2, but full public-demo prediction availability also depends on User Stories 1, 2, and 3 behaviours being available.
- Phase 7 Polish depends on all desired user stories.

### User Story Dependencies

- User Story 1: Can start after Phase 2 and provides the MVP product flow.
- User Story 2: Can start after Phase 2; integrates with User Story 1 prediction gating but evidence review remains independently testable.
- User Story 3: Can start after Phase 2; extends all flows with invalid-state protection and fail-closed behavior.
- User Story 4: Can start after Phase 2; full release-gate validation depends on User Story 1 prediction flow, User Story 2 evidence availability, and User Story 3 blocked-state behavior.

### Within Each User Story

- Write tests for constitution-critical behavior before implementation tasks in that story.
- Implement domain/storage/service logic before API endpoint wiring.
- Implement API endpoint behavior before Streamlit integration.
- Validate each story independently before starting lower-priority story work when working sequentially.

## Parallel Opportunities

- Setup tasks T003 through T007 can run in parallel after T001 begins.
- Foundational schema, validation, ML interface, MLflow wrapper, router stub, client shell, and test fixture tasks marked `[P]` can run in parallel.
- User Story 1 tests T027 through T033 can run in parallel, and implementation tasks T034, T035, T036, T042, T044, and T045 can run in parallel after shared foundations exist.
- User Story 2 tests T048 through T052 can run in parallel, and implementation tasks T056, T057, T059, and T060 can run in parallel.
- User Story 3 tests T061 through T067 can run in parallel, and implementation tasks T068, T069, and T073 can run in parallel.
- User Story 4 tests T077 through T082 can run in parallel, and implementation tasks T086, T088, T089, T091, and T092 can run in parallel.

## Parallel Example: User Story 1

```text
Task: "T027 [P] [US1] Add contract tests for happy-path schemas in tests/contract/test_prediction_flow_contract.py"
Task: "T028 [P] [US1] Add integration test for full approved-model journey in tests/integration/test_supported_prediction_flow.py"
Task: "T029 [P] [US1] Add copy-safety tests in tests/unit/test_disclaimer_copy.py"
Task: "T030 [P] [US1] Add traceability tests in tests/contract/test_prediction_traceability.py"
Task: "T031 [P] [US1] Add feature timestamp tests in tests/ml_safety/test_feature_timestamp_validation.py"
Task: "T032 [P] [US1] Add prediction log tests in tests/integration/test_prediction_logging.py"
Task: "T033 [P] [US1] Add Streamlit client boundary tests in tests/unit/test_streamlit_api_client.py"
```

## Parallel Example: User Story 2

```text
Task: "T048 [P] [US2] Add evidence contract tests in tests/contract/test_model_evidence_contract.py"
Task: "T049 [P] [US2] Add evidence-before-prediction integration tests in tests/integration/test_evidence_before_prediction.py"
Task: "T050 [P] [US2] Add evidence presentation tests in tests/unit/test_evidence_presentation.py"
Task: "T051 [P] [US2] Add paper-trading evidence display tests in tests/unit/test_paper_trading_evidence_display.py"
Task: "T052 [P] [US2] Add evidence chronology tests in tests/ml_safety/test_evidence_chronology.py"
```

## Parallel Example: User Story 3

```text
Task: "T061 [P] [US3] Add model filtering tests in tests/unit/test_model_filtering.py"
Task: "T062 [P] [US3] Add fail-closed registry tests in tests/integration/test_registry_fail_closed.py"
Task: "T063 [P] [US3] Add unsupported stock tests in tests/integration/test_unsupported_stock_handling.py"
Task: "T064 [P] [US3] Add data availability and quality tests in tests/ml_safety/test_data_availability_and_quality.py"
Task: "T065 [P] [US3] Add error response contract tests in tests/contract/test_error_responses.py"
Task: "T066 [P] [US3] Add error copy-safety tests in tests/unit/test_error_copy_safety.py"
Task: "T067 [P] [US3] Add safe failure logging tests in tests/integration/test_safe_failure_logging.py"
```

## Parallel Example: User Story 4

```text
Task: "T077 [P] [US4] Add demo status contract tests in tests/contract/test_demo_status_contract.py"
Task: "T078 [P] [US4] Add public-demo release gate tests in tests/deployment/test_public_demo_release_gate.py"
Task: "T079 [P] [US4] Add public-demo model restriction tests in tests/deployment/test_public_demo_model_restrictions.py"
Task: "T080 [P] [US4] Add degraded demo behavior tests in tests/deployment/test_degraded_demo_behavior.py"
Task: "T081 [P] [US4] Add public-demo data governance tests in tests/deployment/test_public_demo_data_governance.py"
Task: "T082 [P] [US4] Add public-demo smoke test in tests/deployment/test_public_demo_smoke.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 User Story 1.
4. Stop and validate the approved-model evidence-stock-prediction journey.

### Incremental Delivery

1. Add User Story 1 for the local MVP prediction journey.
2. Add User Story 2 to strengthen evidence review and evidence-before-prediction.
3. Add User Story 3 to harden unavailable states, fail-closed model access, data quality, and error handling.
4. Add User Story 4 for public-demo deployment and release-gate behavior.
5. Complete Phase 7 audits and validation before public review.

### TDD Order

For each story, implement tests first for constitution-critical behavior, confirm they fail, then implement the minimum source changes needed to pass them.
