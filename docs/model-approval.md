# Model Approval

A model may appear in the customer-facing selector only when it is approved,
has loaded required evidence, has an evaluation period, has a supported IDX
universe, has known limitations, and has traceability metadata.

MLflow may store model artifacts, metrics, runs, and registry metadata. SQLite
stores the customer-facing model catalogue and public-demo eligibility.

The system fails closed when MLflow and SQLite disagree on any of these fields:

- approval status;
- model version;
- artifact URI;
- supported universe;
- public-demo eligibility.

Fail-closed means:

- hide the model from the customer-facing list;
- block prediction;
- log a sanitized registry conflict;
- show a clear unavailable-model message.

Public-demo prediction additionally requires `model_origin=real`,
`public_demo_eligible=true`, current registry synchronization, loaded required
evidence, and approved non-sensitive data.

## Notebook-To-Live Workflow

Local notebooks should use MLflow to track experiment runs, parameters,
metrics, model artifacts, and comparison tables. A notebook run is experimental
by default and must not appear in the customer-facing app.

Local MLflow tracking should use the SQLite-backed tracking store:

```bash
export NUSANTARA_MLFLOW_TRACKING_URI="sqlite:///./.local/mlflow_tracking.sqlite"
```

This stores MLflow run metadata, params, metrics, and tags in a local database
instead of the deprecated filesystem tracking store.

Promotion is manual:

1. Run the local experiment notebook and log the candidate to MLflow.
2. Inspect the run metrics, per-stock metrics, evidence period, and artifact.
3. Promote the chosen run with an explicit approval command, for example:

   ```bash
   .venv/bin/python -m model_registry.promote_candidate \
     --run-id <mlflow-run-id> \
     --model-id idx-logistic-v2 \
     --model-version 2026.06 \
     --model-name "IDX Logistic Regression V2" \
     --supported-universe-id idx-approved-universe \
     --approve
   ```

4. The promotion command copies the MLflow artifact into the local model
   artifact path, writes SQLite catalogue/evidence records, stamps approval
   metadata into MLflow, and verifies that MLflow and SQLite agree.

If required metrics, evidence period, supported universe, model artifact, or
manual approval are missing, promotion fails and the model remains hidden.
