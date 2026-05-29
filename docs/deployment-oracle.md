# Public Demo Data Inventory

Public demo prediction availability requires:

- at least one real approved model;
- current MLflow and SQLite registry synchronization;
- loaded required evidence;
- at least one approved non-sensitive data source.

Allowed public-demo asset classifications:

- `public_demo_allowed`
- `public_data`
- `delayed_data`
- `static_data`
- `approved_artifact`

Excluded from public deployment:

- secrets;
- credentials;
- private datasets;
- proprietary files;
- restricted source data;
- unrestricted internal artifacts;
- mock/demo-only models;
- dummy prediction outputs.

If any release gate fails, the app may run only as a degraded demo and must not
claim full public prediction availability.

