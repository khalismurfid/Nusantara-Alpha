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
  next-session open-to-close target chronology, yfinance ingestion CLI parsing,
  market ranking, action wording, evidence readability, unavailable-state copy,
  and public-demo banner behavior.
- Full generated pytest suite passed.

Focused UI/copy command:

```bash
.venv/bin/python -m pytest tests/unit/test_market_data_cli.py tests/unit/test_market_data_ingestion.py tests/ml_safety/test_realistic_model_chronology.py tests/integration/test_market_ranking.py tests/contract/test_ranking_contract.py tests/integration/test_supported_prediction_flow.py tests/unit/test_streamlit_api_client.py
```

Result:

```text
10 passed
```

Full suite command:

```bash
.venv/bin/python -m pytest
```

Result:

```text
68 passed
```
