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
- MVP UX review now requires the selected ticker prediction to be the primary
  visible content after valid model, evidence, and ticker selection.
- Evidence must appear as a concise summary before or alongside interpretation,
  while detailed methodology and traceability remain secondary.
- Primary prediction action text must be automatic or use `Predict`; the app
  must not show `Request educational prediction`.
- Limitation copy must read like product guidance rather than raw metadata,
  isolated tags, or cell-style labels.
- Local FastAPI server started on `127.0.0.1:8000` and returned `200` for
  `/health`.
- Local Streamlit server started on `127.0.0.1:8501` and returned `200`.
- Local API prediction smoke check for `idx-direction-baseline` + `BBCA`
  returned a structured prediction with no blocked items.
- SQLite prediction logging was updated to commit write operations so the
  automatic prediction flow does not leave the local database locked.

Browser screenshot validation could not be completed in this Codex session
because the in-app browser backend was unavailable. HTTP and API smoke checks
passed against the running local services.
