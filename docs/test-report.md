# Test Report

Date: 2026-05-29

Status: Passed.

Validation completed:

- Python compile checks passed for `app_streamlit/`, `backend/`, `ml/`,
  `model_registry/`, `storage/`, and `tests/`.
- Service-level smoke checks passed for supported prediction, unsupported stock,
  stale data, and public-demo full/degraded states.
- Focused tests passed for top-of-page client-facing explanation,
  prediction-first presentation, native Streamlit rendering without raw HTML,
  realistic pooled-model prediction, yfinance ingestion normalization,
  triple-barrier target chronology, persisted baseline model artifacts,
  yfinance ingestion CLI parsing, market ranking, action wording, evidence
  readability, unavailable-state copy, and public-demo banner behavior.
- Full generated pytest suite passed.

Focused UI/copy command:

```bash
.venv/bin/python -m pytest tests/ml_safety/test_realistic_model_chronology.py tests/contract/test_model_evidence_contract.py tests/contract/test_prediction_flow_contract.py tests/unit/test_evidence_presentation.py tests/unit/test_prediction_view_presentation.py tests/unit/test_streamlit_api_client.py tests/integration/test_supported_prediction_flow.py tests/unit/test_model_artifact_persistence.py
```

Result:

```text
20 passed
```

Full suite command:

```bash
.venv/bin/python -m pytest
```

Result:

```text
74 passed
```
