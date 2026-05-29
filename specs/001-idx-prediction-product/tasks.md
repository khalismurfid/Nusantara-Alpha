# Tasks: Nusantara Alpha Customer Prediction Product

**Input**: Design documents from `/specs/001-idx-prediction-product/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

**Tests**: Required for constitution-critical behavior and the MVP UX revision:
no financial advice, evidence-before-prediction, honest uncertainty,
traceability, curated model access, unsupported-state handling, public-demo
data governance, prediction-first presentation order, plain product language,
and readable limitations.

**Organization**: Tasks are grouped by user story so the prediction-first MVP
revision can be implemented and tested incrementally on top of the existing
working skeleton.

## Phase 1: Setup

**Purpose**: Add small shared UI/copy foundations for the next UX increment.

- [ ] T001 [P] Create shared product-language constants for primary labels, section titles, and banned awkward UI phrases in `app_streamlit/copy/product_language.py`
- [ ] T002 [P] Create shared Streamlit layout/style helpers for prediction-first sections and secondary detail containers in `app_streamlit/components/ui_shell.py`
- [ ] T003 [P] Create reusable UI fixture builders for prediction, evidence, stock, and demo-status dictionaries in `tests/unit/ui_fixtures.py`

---

## Phase 2: Foundational

**Purpose**: Prepare shared presentation seams that block the user-story work.

**Critical**: Complete this phase before changing the main Streamlit flow.

- [ ] T004 Define a prediction view formatter contract with primary, supporting, and secondary sections in `app_streamlit/components/prediction_result.py`
- [ ] T005 Add copy-safety helpers for awkward prediction action labels and raw limitation fragments in `app_streamlit/copy/disclaimers.py`
- [ ] T006 Add dependency-free app state helper functions for selected model, loaded evidence, supported ticker, and prediction eligibility in `app_streamlit/app.py`
- [ ] T007 [P] Rewrite local seed model, evidence, stock, and limitation copy into calmer product language in `storage/seed_local_demo.py`
- [ ] T008 [P] Update MVP UX validation notes for prediction-first behavior in `docs/quickstart-validation.md`

**Checkpoint**: Shared copy, formatting, state, and fixture seams are ready.

---

## Phase 3: User Story 1 - Explore a Supported Prediction (Priority: P1) MVP

**Goal**: A user selects an approved model and supported IDX ticker, then
quickly sees a readable prediction-first view centered on ticker, model signal,
confidence, context, and limitations.

**Independent Test**: Complete the flow with one approved model and one
supported IDX stock, then verify the prediction is primary, wording is natural,
required fields remain present, and no financial-advice framing appears.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add prediction view formatter tests for primary display order and secondary traceability placement in `tests/unit/test_prediction_view_presentation.py`
- [ ] T010 [P] [US1] Add tests rejecting `Request educational prediction` and accepting automatic prediction or `Predict` in `tests/unit/test_prediction_action_copy.py`
- [ ] T011 [P] [US1] Add app state helper tests for automatic prediction eligibility after approved model, loaded evidence, and supported ticker selection in `tests/unit/test_streamlit_prediction_flow.py`
- [ ] T012 [P] [US1] Extend disclaimer copy tests for prediction-first labels, confidence copy, and no-advice framing in `tests/unit/test_disclaimer_copy.py`
- [ ] T013 [P] [US1] Add API-client flow tests proving the UI still requests predictions through FastAPI rather than local model logic in `tests/unit/test_streamlit_api_client.py`

### Implementation for User Story 1

- [ ] T014 [US1] Refactor the main Streamlit journey so valid model and ticker selection triggers automatic prediction or a lightweight `Predict` action in `app_streamlit/app.py`
- [ ] T015 [US1] Rebuild prediction rendering around sections for prediction, confidence, why this signal appeared, key limitations, concise evidence, and traceability details in `app_streamlit/components/prediction_result.py`
- [ ] T016 [P] [US1] Apply prediction-first layout helpers to keep the main result visually dominant and traceability secondary in `app_streamlit/components/ui_shell.py`
- [ ] T017 [P] [US1] Rewrite product framing copy to sound customer-facing while preserving the educational disclaimer in `app_streamlit/components/framing.py`
- [ ] T018 [US1] Render blocked prediction messages in the same prediction-first area without showing partial results as valid predictions in `app_streamlit/app.py`
- [ ] T019 [US1] Update reviewer checklist items for the prediction-first happy path in `docs/reviewer-checklist.md`

**Checkpoint**: User Story 1 delivers the revised MVP experience and is
independently testable.

---

## Phase 4: User Story 2 - Review Model Evidence and Limitations (Priority: P2)

**Goal**: A reviewer can still inspect evidence, limitations, evaluation
period, supported stocks, data-quality caveats, and methodology context without
the main screen feeling text-heavy or internal.

**Independent Test**: Select each approved model and verify a concise evidence
summary appears before or alongside prediction interpretation, while detailed
methodology and traceability remain secondary.

### Tests for User Story 2

- [ ] T020 [P] [US2] Extend evidence presentation tests for concise summary fields, secondary detail grouping, and historical-performance caveat in `tests/unit/test_evidence_presentation.py`
- [ ] T021 [P] [US2] Add limitation readability tests that reject raw metadata, cell-like text, and standalone `Limited universe` copy in `tests/unit/test_limitation_copy_readability.py`
- [ ] T022 [P] [US2] Extend paper-trading display tests to keep paper-trading evidence secondary and separate from backtest evidence in `tests/unit/test_paper_trading_evidence_display.py`

### Implementation for User Story 2

- [ ] T023 [US2] Refactor evidence formatting into concise summary and detailed methodology sections in `app_streamlit/components/evidence_panel.py`
- [ ] T024 [US2] Replace warning/tag-style limitation rendering with readable guidance paragraphs in `app_streamlit/components/evidence_panel.py`
- [ ] T025 [P] [US2] Keep paper-trading evidence visually secondary and clearly separated from backtest evidence in `app_streamlit/components/paper_trading_evidence.py`
- [ ] T026 [US2] Integrate concise evidence summary into the main prediction journey before or alongside interpretation in `app_streamlit/app.py`
- [ ] T027 [P] [US2] Update methodology and limitations documentation with the new concise evidence and limitation wording in `docs/methodology.md` and `docs/limitations.md`

**Checkpoint**: User Story 2 preserves evidence-before-prediction without
overwhelming the main product experience.

---

## Phase 5: User Story 3 - Handle Unsupported or Unavailable Prediction States (Priority: P3)

**Goal**: Users see clear, calm unavailable states for unsupported stocks,
unavailable models, missing evidence, stale data, and failed predictions without
receiving misleading output.

**Independent Test**: Attempt each invalid state and verify the product blocks
prediction, explains the reason in plain language, gives a useful next step
when possible, and avoids financial-advice framing.

### Tests for User Story 3

- [ ] T028 [P] [US3] Add unavailable-state copy tests for plain messages, next steps, and hidden internal reason codes in `tests/unit/test_unavailable_state_copy.py`
- [ ] T029 [P] [US3] Extend unsupported stock handling tests for customer-facing unavailable copy and aggregate non-personal interest tracking in `tests/integration/test_unsupported_stock_handling.py`
- [ ] T030 [P] [US3] Extend error copy safety tests for unsupported stock, stale data, missing evidence, registry conflict, and invalid prediction states in `tests/unit/test_error_copy_safety.py`

### Implementation for User Story 3

- [ ] T031 [US3] Rewrite unavailable-state formatting and rendering so users see clear product guidance instead of raw status labels in `app_streamlit/components/unavailable_state.py`
- [ ] T032 [US3] Refactor stock search and selection to separate supported choices from unavailable tickers and block prediction until invalid selections are removed in `app_streamlit/app.py`
- [ ] T033 [US3] Rewrite unsupported-stock and blocked-prediction service messages into plain product language in `backend/services/stock_service.py` and `backend/services/prediction_service.py`
- [ ] T034 [US3] Update local unsupported, stale-data, and registry-conflict fixtures with user-facing unavailable reasons in `storage/seed_local_demo.py`

**Checkpoint**: User Story 3 invalid-state handling remains safe and reads like
a customer-facing product.

---

## Phase 6: User Story 4 - Access a Public Portfolio Demo (Priority: P4)

**Goal**: A reviewer opening the public demo sees the same polished product
language, public-demo limitations, and no-financial-advice framing as local
users.

**Independent Test**: Run in `public_demo` context and verify the banner,
degraded states, real-model gate messages, data-as-of limitations, and copy
safety remain clear and do not expose mock predictions or restricted data.

### Tests for User Story 4

- [ ] T035 [P] [US4] Extend degraded demo behavior tests for polished banner copy and no false claim of full prediction availability in `tests/deployment/test_degraded_demo_behavior.py`
- [ ] T036 [P] [US4] Extend public-demo model restriction tests for prediction-first UI states that block mock or dummy outputs in `tests/deployment/test_public_demo_model_restrictions.py`

### Implementation for User Story 4

- [ ] T037 [US4] Rewrite full, degraded, and unavailable demo banner presentation in `app_streamlit/components/demo_banner.py`
- [ ] T038 [US4] Integrate public-demo unavailable prediction states into the prediction-first main flow in `app_streamlit/app.py`
- [ ] T039 [P] [US4] Update Oracle deployment notes with prediction-first public demo validation steps in `deployment/oracle-cloud-free-tier.md`

**Checkpoint**: User Story 4 public-demo behavior remains safe and reviewer
friendly.

---

## Phase 7: Polish and Cross-Cutting Concerns

**Purpose**: Validate the UX revision across copy, tests, documentation, and
manual review.

- [ ] T040 [P] Update README product-flow description to reflect prediction-first UX and lightweight prediction interaction in `README.md`
- [ ] T041 Run focused UI/copy tests for prediction presentation, action wording, evidence readability, unavailable states, and demo banner behavior and record results in `docs/test-report.md`
- [ ] T042 Run full pytest suite for `tests/unit/`, `tests/contract/`, `tests/integration/`, `tests/ml_safety/`, and `tests/deployment/` and record results in `docs/test-report.md`
- [ ] T043 Run forbidden-phrase and awkward-copy audit across `app_streamlit/`, `backend/`, `storage/seed_local_demo.py`, and `docs/`, then record findings in `docs/copy-safety-audit.md`
- [ ] T044 Run the manual quickstart validation flow for the local app and record prediction-first UX pass/fail notes in `docs/quickstart-validation.md`

---

## Dependencies and Execution Order

### Phase Dependencies

- Phase 1 Setup has no dependencies.
- Phase 2 Foundational depends on Phase 1 and blocks the user-story phases.
- Phase 3 User Story 1 depends on Phase 2 and is the MVP for this iteration.
- Phase 4 User Story 2 depends on Phase 2 and can run after or alongside User Story 1 once shared formatters exist.
- Phase 5 User Story 3 depends on Phase 2 and can run after or alongside User Story 1 once app state helpers exist.
- Phase 6 User Story 4 depends on Phase 2 and can run after demo-status copy rules are available.
- Phase 7 Polish depends on the desired user-story phases.

### User Story Dependencies

- User Story 1: Start after Phase 2; delivers the main prediction-first MVP.
- User Story 2: Start after Phase 2; integrates with User Story 1 but remains independently testable through evidence components.
- User Story 3: Start after Phase 2; integrates with User Story 1 blocked states but remains independently testable through invalid requests.
- User Story 4: Start after Phase 2; full public-demo validation depends on User Stories 1 and 3 presentation states.

### Within Each User Story

- Write tests for constitution-critical and UX-critical behavior before implementation tasks.
- Keep UI presentation changes in `app_streamlit/`.
- Keep service-message changes in `backend/services/`.
- Do not move model, feature, or prediction logic into Streamlit code.
- Validate each story independently before starting lower-priority work when working sequentially.

## Parallel Opportunities

- Setup tasks T001 through T003 can run in parallel.
- Foundational tasks T007 and T008 can run in parallel with formatter work after T001 exists.
- User Story 1 tests T009 through T013 can run in parallel.
- User Story 1 implementation tasks T016 and T017 can run in parallel with T015 after T004 exists.
- User Story 2 tests T020 through T022 can run in parallel.
- User Story 2 implementation tasks T025 and T027 can run in parallel with T023.
- User Story 3 tests T028 through T030 can run in parallel.
- User Story 4 tests T035 and T036 can run in parallel.
- Polish documentation tasks T040 and T043 can run in parallel after implementation stabilizes.

## Parallel Example: User Story 1

```text
Task: "T009 [P] [US1] Add prediction view formatter tests in tests/unit/test_prediction_view_presentation.py"
Task: "T010 [P] [US1] Add action label tests in tests/unit/test_prediction_action_copy.py"
Task: "T011 [P] [US1] Add app state helper tests in tests/unit/test_streamlit_prediction_flow.py"
Task: "T012 [P] [US1] Extend disclaimer copy tests in tests/unit/test_disclaimer_copy.py"
Task: "T013 [P] [US1] Add API-client boundary tests in tests/unit/test_streamlit_api_client.py"
```

## Parallel Example: User Story 2

```text
Task: "T020 [P] [US2] Extend evidence presentation tests in tests/unit/test_evidence_presentation.py"
Task: "T021 [P] [US2] Add limitation readability tests in tests/unit/test_limitation_copy_readability.py"
Task: "T022 [P] [US2] Extend paper-trading display tests in tests/unit/test_paper_trading_evidence_display.py"
```

## Parallel Example: User Story 3

```text
Task: "T028 [P] [US3] Add unavailable-state copy tests in tests/unit/test_unavailable_state_copy.py"
Task: "T029 [P] [US3] Extend unsupported stock tests in tests/integration/test_unsupported_stock_handling.py"
Task: "T030 [P] [US3] Extend error copy safety tests in tests/unit/test_error_copy_safety.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 User Story 1.
4. Stop and validate the local MVP: model selection, supported ticker
   selection, prediction-first view, confidence, key limitations, concise
   evidence, traceability details, and no-advice copy.

### Incremental Delivery

1. Add User Story 1 for the prediction-first MVP.
2. Add User Story 2 to improve evidence readability and limitation copy.
3. Add User Story 3 to improve invalid-state language and unsupported-stock
   handling.
4. Add User Story 4 to polish public-demo messaging.
5. Run Phase 7 validation before committing the implementation.

### Suggested MVP Scope

For the immediate MVP feedback loop, complete Phase 1, Phase 2, and Phase 3
first. That directly addresses the main complaint: the current UI hides the
prediction behind awkward wording and dense internal-style content.
