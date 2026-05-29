# Data Model: Nusantara Alpha Customer Prediction Product

## Entity: Curated Prediction Model

Represents a model that may appear in the customer-facing model selector when
approval and visibility rules are satisfied.

**Fields**
- `model_id`: Stable model identifier.
- `model_version`: Specific model version.
- `model_name`: User-facing model name.
- `description`: Plain-language description.
- `status`: One of `approved`, `hidden`, `experimental`, `deprecated`,
  `unavailable`.
- `model_origin`: One of `real`, `local_mock`, `demo_only`, `experimental`.
- `public_demo_eligible`: Boolean derived from approval and origin.
- `supported_universe_id`: Supported IDX stock universe reference.
- `evaluation_period_start`: First date in evaluation evidence.
- `evaluation_period_end`: Last date in evaluation evidence.
- `evidence_available`: Whether required evidence exists.
- `evidence_load_status`: One of `loaded`, `missing`, `stale`, `unavailable`,
  `not_loaded`.
- `limitations`: Known limitations shown to users.
- `mlflow_run_id`: Related MLflow run identifier when available.
- `mlflow_model_uri`: Related MLflow model artifact URI when available.
- `sqlite_catalogue_revision`: Customer-facing catalogue revision.
- `mlflow_registry_revision`: Registry metadata revision or run metadata
  reference.
- `registry_sync_status`: One of `current`, `stale`, `incomplete`, `conflict`.
- `registry_conflict_reason`: Conflict detail when sync fails.
- `created_at`: Catalogue creation timestamp.
- `updated_at`: Catalogue update timestamp.

**Validation Rules**
- Main customer flow shows only `status=approved` models.
- Approval requires display approval, historical evidence, evaluation period,
  supported universe, known limitations, and traceability metadata.
- Public demo predictions require `status=approved`,
  `model_origin=real`, `public_demo_eligible=true`, and
  `registry_sync_status=current`.
- Hidden, experimental, deprecated, unavailable, local mock, demo-only, or
  unapproved models cannot generate public-demo predictions.
- If SQLite and MLflow disagree on approval status, model version, artifact URI,
  supported universe, or public-demo eligibility, `registry_sync_status` becomes
  `conflict`; the model is hidden, prediction is blocked, and the conflict is
  logged.
- Stale or incomplete registry synchronization hides the model until resolved.

**State Transitions**
- `experimental` -> `approved`: Allowed only after evidence, supported universe,
  limitations, and traceability are complete.
- `approved` -> `hidden` or `deprecated`: Removes the model from the customer
  selector.
- `approved` -> `unavailable`: Blocks prediction and shows an unavailable state.

## Entity: Model Evidence

Represents the evidence users inspect before prediction.

**Fields**
- `evidence_id`: Stable evidence identifier.
- `model_id`: Associated model identifier.
- `model_version`: Associated model version.
- `evidence_type`: One of `backtest`, `paper_trading`, `validation_summary`.
- `evaluation_period_start`: Start of evidence period.
- `evaluation_period_end`: End of evidence period.
- `key_metrics`: Curated metrics for user/reviewer interpretation.
- `performance_summary`: Plain-language historical performance summary.
- `supported_universe_id`: Supported universe covered by evidence.
- `known_limitations`: Known limitations and caveats.
- `data_quality_notes`: Missing data, stale data, corporate actions,
  delistings, trading halts, illiquidity, exchange-calendar alignment, ticker
  identity changes, and survivorship-bias notes when material.
- `historical_performance_caveat`: Required caveat that historical performance
  may not generalize.
- `evidence_status`: One of `complete`, `weak`, `data_limited`, `missing`,
  `stale`.
- `evidence_load_status`: One of `loaded`, `missing`, `stale`, `unavailable`,
  `not_loaded`.
- `evidence_as_of`: Timestamp when evidence was generated or last reviewed.
- `data_source_mode`: One of `sample`, `mock`, `public`, `delayed`, `static`,
  `approved`, `live`, `unavailable`.

**Validation Rules**
- Evidence must be visible before prediction.
- Missing, stale, unavailable, or not-loaded required evidence blocks model
  approval or prediction.
- Weak, stale, or data-limited evidence may allow prediction only with prominent
  limitations when required evidence is present.
- Paper-trading evidence must be shown separately from backtest evidence.
- Public-demo evidence must be tied to a real approved model and approved
  non-sensitive data.

## Entity: Supported IDX Stock

Represents an IDX stock and its relationship to a selected model universe.

**Fields**
- `ticker`: IDX ticker displayed to users.
- `name`: Security name.
- `exchange`: Expected value `IDX`.
- `universe_id`: Supported model universe identifier.
- `support_status`: One of `supported`, `unsupported`,
  `temporarily_unavailable`.
- `unavailable_reason`: Plain-language unavailable reason.
- `data_as_of`: Latest usable data timestamp.
- `freshness_status`: One of `fresh`, `stale`, `missing`.
- `market_data_flags`: Material quality or bias flags.

**Validation Rules**
- Prediction requires at least one `supported` stock for the selected model.
- Unsupported stocks remain searchable but must be marked unavailable and block
  prediction until removed or replaced.
- Missing or stale required data blocks or withholds prediction.

## Entity: Data Availability State

Represents whether available data can support evidence or prediction for a
model/ticker pair.

**Fields**
- `model_id`: Selected model identifier.
- `ticker`: IDX stock ticker.
- `required_period_start`: Required data window start.
- `required_period_end`: Required data window end.
- `data_as_of`: Latest available data timestamp.
- `feature_generation_timestamp`: Timestamp when features were generated for
  prediction.
- `freshness_status`: One of `fresh`, `stale`, `missing`.
- `chronology_status`: One of `valid`, `invalid_future_information`.
- `quality_flags`: Material market-data quality and bias risks.
- `blocking_reason`: Reason prediction or evidence is blocked.

**Validation Rules**
- `data_as_of` must not be later than the prediction timestamp for historical
  or next-session predictions.
- `feature_generation_timestamp` must exist and must not be later than the
  relevant prediction timestamp.
- Missing or invalid `feature_generation_timestamp` blocks prediction with a
  clear error.
- Invalid chronology blocks evidence and prediction.
- Material quality risks must be disclosed and block prediction when the output
  would be unreliable or untraceable.

## Entity: Prediction Request

Represents a user-initiated request for next-market-session prediction.

**Fields**
- `request_id`: Stable request identifier.
- `model_id`: Selected model identifier.
- `model_version`: Selected model version.
- `tickers`: One or more selected tickers.
- `target`: Prediction target, such as `next_market_session_direction`.
- `requested_at`: Request timestamp.
- `runtime_context`: One of `local`, `test`, `public_demo`.
- `evidence_reference`: Evidence record used for interpretation.
- `evidence_load_status`: Evidence load status at request validation time.

**Validation Rules**
- Requires an approved model and at least one supported IDX stock.
- Public-demo runtime requires a real approved model and approved
  non-sensitive data.
- Request validation checks model status, registry sync consistency, stock
  support, required evidence availability/load status, data freshness,
  chronology, feature timestamp validity, and output contract requirements.
- Approved model plus supported ticker is insufficient; required evidence must
  be loaded and valid before prediction.

## Entity: Prediction Output

Represents one structured prediction result for one selected stock.

**Fields**
- `prediction_id`: Stable prediction identifier.
- `request_id`: Parent request identifier.
- `ticker`: Selected IDX ticker.
- `prediction_target`: Prediction target.
- `model_signal`: Predicted direction or model signal.
- `confidence_category`: `Low`, `Medium`, or `High`.
- `numeric_confidence`: Optional numeric confidence detail.
- `confidence_explanation`: Plain-language uncertainty explanation.
- `context_summary`: Short context summary.
- `limitation_summary`: Key limitation summary.
- `model_name`: Selected model display name.
- `model_id`: Selected model identifier.
- `model_version`: Selected model version.
- `data_as_of_timestamp`: Input data availability timestamp.
- `feature_generation_timestamp`: Timestamp when input features were generated.
- `prediction_timestamp`: Prediction generation timestamp.
- `evaluation_context`: Evaluation period and evidence context.
- `evidence_reference`: Evidence identifier/reference.
- `disclaimer_text`: Educational/research disclaimer.
- `disclaimer_version`: Disclaimer version identifier.

**Validation Rules**
- Must include all required output fields before display.
- Must not include financial advice, buy/sell guidance, guaranteed returns,
  position sizing, allocation advice, or personalized guidance.
- Must be traceable to model version, ticker, data-as-of timestamp,
  feature-generation timestamp, prediction timestamp, and evidence context.
- `feature_generation_timestamp` must be present and must not be later than the
  relevant prediction timestamp.
- Public-demo outputs must not come from mock/demo-only models or dummy
  prediction generators.

## Entity: Prediction Log

Stores traceability and audit metadata for prediction attempts.

**Fields**
- `log_id`: Stable log identifier.
- `request_id`: Prediction request identifier.
- `prediction_id`: Prediction output identifier when successful.
- `model_id`: Selected model identifier.
- `model_version`: Selected model version.
- `tickers`: Selected ticker or tickers.
- `data_as_of_timestamp`: Input data timestamp.
- `feature_generation_timestamp`: Feature generation timestamp.
- `prediction_timestamp`: Prediction timestamp.
- `prediction_output`: Stored structured output summary.
- `confidence`: Confidence category or score.
- `disclaimer_version`: Disclaimer version shown.
- `status`: One of `success`, `blocked`, `failed`.
- `error_message`: Failure or blocking explanation when applicable.
- `runtime_context`: One of `local`, `test`, `public_demo`.

**Validation Rules**
- Logs must support reviewer traceability.
- Logs must store data-as-of timestamp, feature-generation timestamp, and
  prediction timestamp for every successful prediction and every blocked request
  where those values are available.
- Logs must not include secrets, credentials, private datasets, or personalized
  investment intent.
- Public-demo logs must not contain dummy prediction outputs.

## Entity: Unsupported Stock Interest Signal

Represents aggregate, non-personal feedback from unsupported stock searches.

**Fields**
- `ticker`: Unsupported ticker searched or entered.
- `model_id`: Selected model when available.
- `reason`: Unsupported reason shown to the user.
- `count`: Aggregate count.
- `first_seen_at`: First aggregate observation timestamp.
- `last_seen_at`: Latest aggregate observation timestamp.

**Validation Rules**
- Interest is aggregate and non-personal.
- Interest is not investment intent or financial advice.
- Interest is used only for future support planning.

## Entity: Educational Disclaimer

Represents advice-boundary language shown in screens and outputs.

**Fields**
- `disclaimer_id`: Stable disclaimer identifier.
- `version`: Disclaimer version.
- `text`: User-facing disclaimer text.
- `placement`: Screen or output location.
- `effective_date`: Date the disclaimer became active.

**Validation Rules**
- Disclaimer must appear before or during the prediction flow and in each
  prediction output.
- Disclaimer must state that outputs are educational research and not financial
  advice, buy/sell guidance, guaranteed profit, personalized guidance, position
  sizing, allocation advice, or trade execution.

## Entity: Public Demo Runtime

Represents public review deployment state.

**Fields**
- `environment_name`: One of `local`, `public_demo`, `review`.
- `public_demo_url`: Public URL when available.
- `app_status`: One of `available`, `degraded`, `unavailable`.
- `api_status`: One of `available`, `degraded`, `unavailable`.
- `public_predictions_available`: Whether public prediction is available.
- `release_status`: One of `full`, `degraded`, `unavailable`.
- `real_approved_model_available`: Whether at least one real approved model is
  available and registry-synced.
- `approved_data_source_available`: Whether at least one approved non-sensitive
  data source is available.
- `release_gate_reason`: Explanation when public demo is degraded or
  unavailable.
- `unavailable_reason`: Reason public prediction is blocked.
- `data_source_mode`: One of `public`, `delayed`, `static`, `approved`,
  `live`, `unavailable`.
- `data_as_of`: Latest data timestamp/date shown in public demo.
- `demo_limitations`: Public-demo limitations.
- `deployed_at`: Last deployment timestamp.

**Validation Rules**
- Public demo must show the disclaimer and demo limitations.
- Public prediction is available only with at least one real approved model, a
  current registry sync, required evidence, and at least one approved
  non-sensitive data source.
- If a release gate is missing, `release_status=degraded` or `unavailable`; the
  UI may show flow and unavailable states but must not claim full prediction
  availability.
- If no real approved model is available, public prediction is blocked instead
  of falling back to mock or dummy outputs.

## Entity: Registry Sync Conflict

Represents fail-closed mismatch records between MLflow and SQLite.

**Fields**
- `conflict_id`: Stable conflict identifier.
- `model_id`: Affected model identifier.
- `model_version`: Affected model version.
- `conflict_type`: One of `approval_status`, `model_version`, `artifact_uri`,
  `supported_universe`, `public_demo_eligibility`, `sync_stale`,
  `sync_incomplete`.
- `sqlite_value`: Value recorded in SQLite when safe to store.
- `mlflow_value`: Value recorded in MLflow when safe to store.
- `detected_at`: Conflict detection timestamp.
- `resolution_status`: One of `open`, `resolved`, `ignored_after_review`.
- `user_message`: Clear unavailable-model message for customer-facing flows.

**Validation Rules**
- Any open conflict hides the affected model and blocks prediction.
- Conflict logs must not expose secrets, credentials, private paths, or
  proprietary payloads.
- Resolved conflicts require a fresh registry synchronization before the model
  can reappear.

## Entity: Deployable Data Asset

Represents a data/artifact source and whether it may be used in public demo.

**Fields**
- `asset_id`: Stable asset identifier.
- `asset_type`: One of `public_data`, `delayed_data`, `static_data`,
  `approved_artifact`, `sample_data`, `mock_data`, `private_dataset`,
  `credential`, `proprietary_file`, `internal_artifact`.
- `classification`: One of `public_demo_allowed`, `local_only`, `restricted`,
  `secret`, `private`, `proprietary`.
- `data_as_of`: Data timestamp/date when applicable.
- `limitations`: User-facing limitation text.
- `approval_reference`: Evidence that the asset is approved for use.

**Validation Rules**
- Public demo may use only `public_demo_allowed` assets.
- Sample/mock assets are local-only unless explicitly approved as
  non-sensitive data and not used as mock model or dummy prediction output.
- Secrets, credentials, private datasets, proprietary files, and unrestricted
  internal artifacts must not be deployed or exposed.

## Entity Relationships

- `Curated Prediction Model` has many `Model Evidence` records.
- `Curated Prediction Model` has one supported stock universe containing many
  `Supported IDX Stock` records.
- `Prediction Request` references one selected `Curated Prediction Model` and
  one or more `Supported IDX Stock` records.
- `Prediction Output` belongs to one `Prediction Request` and references one
  `Model Evidence` record.
- `Prediction Log` records each successful, blocked, or failed prediction
  attempt.
- `Public Demo Runtime` constrains which `Curated Prediction Model` and
  `Deployable Data Asset` records can support public prediction.
- `Registry Sync Conflict` belongs to one `Curated Prediction Model` and blocks
  that model from display and prediction while open.
