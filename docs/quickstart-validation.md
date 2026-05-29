# Quickstart Validation

Date: 2026-05-29

Automated smoke checks run in the current environment:

- Python compile checks passed for `app_streamlit/`, `backend/`, `ml/`,
  `model_registry/`, `storage/`, and `tests/`.
- In-memory seeded repository produced a valid supported prediction for `BBCA`.
- Unsupported ticker `GOTO` returned a blocked `unsupported_stock` result.
- Stale data returned a blocked `stale_data` result.
- Public-demo status returned `full` when gates were present.
- Public-demo status returned `degraded` when approved data assets were removed.

Manual browser validation remains pending until Streamlit and FastAPI runtime
dependencies are installed in the environment.

