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

