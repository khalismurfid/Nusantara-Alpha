# Quickstart: Nusantara Alpha Customer Prediction Product

This quickstart describes the planned first implementation path. It does not
implement code yet.

## Local Development Prerequisites

- Python 3.11+
- Local virtual environment
- Docker or Docker Compose where practical
- No private datasets, credentials, API keys, brokerage credentials, or
  proprietary data committed to the repository

## Local Product Skeleton

1. Create and activate a Python virtual environment.
2. Install project dependencies for Streamlit, FastAPI, MLflow, pandas,
   scikit-learn-compatible model interfaces, pytest, and development tooling.
3. Create `deployment/env.example` with non-secret defaults for:
   - FastAPI base URL
   - SQLite database path
   - MLflow tracking URI
   - local data path
   - runtime context (`local` or `public_demo`)
   - public demo URL when available
4. Initialize SQLite tables for model catalogue, evidence metadata, supported
   stocks, data availability, registry sync status, registry conflict logs,
   prediction logs, disclaimers, and unsupported stock interest.
5. Seed local-only mock catalogue, mock evidence, and dummy prediction fixtures
   for skeleton development.
6. Ensure local-only mock/dummy fixtures are not public-demo eligible.

## Run Locally

1. Start the FastAPI service.
2. Start the Streamlit customer-facing app.
3. Open the Streamlit URL in a browser.
4. Complete the local flow:
   - choose model
   - inspect concise evidence
   - choose supported IDX stock
   - immediately understand the prediction-first view
   - inspect confidence, why the signal appeared, key limitations, timestamps,
     traceability, and disclaimer
   - open detailed evidence or methodology only when more review context is
     needed

## Public Demo Precondition

The public demo must use a real approved model. Mock models, demo-only models,
experimental models, and dummy prediction outputs are allowed only for local
development or tests.

Before public deployment, verify:

1. At least one real approved model exists in the model catalogue.
2. The model has loaded, current required evidence, evaluation period,
   supported universe, known limitations, and traceability metadata.
3. The model is linked to approved MLflow metadata/artifacts and SQLite
   catalogue metadata.
4. MLflow and SQLite agree on approval status, model version, artifact URI,
   supported universe, and public-demo eligibility.
5. Public demo data is public, delayed, static, or otherwise approved
   non-sensitive data.
6. Data-as-of timestamp, feature-generation timestamp, and demo limitations are
   available for display.
7. If no real approved model, current registry sync, required evidence, or
   approved data source is available, public prediction is blocked with a clear
   degraded-demo or unavailable message.

## Containerized Demo

When deployment assets are implemented, run the local containerized stack with:

```bash
docker compose -f deployment/compose.yaml --env-file deployment/env.example up --build
```

The containerized stack must preserve the same boundaries:

- Streamlit calls FastAPI.
- FastAPI delegates to services and shared modules.
- Core ML logic remains outside route handlers.
- Mock/dummy prediction outputs are disabled in public-demo mode.
- Registry/catalogue conflicts and stale sync states fail closed.
- Required evidence must be loaded and valid before prediction.
- Secrets and private data are provided only through environment variables or
  approved secure deployment configuration, never committed.

## Oracle Cloud Free Tier Deployment

Preferred public demo target:

1. Provision an Oracle Cloud Free Tier Always Free compute instance or another
   low-cost/free Linux server.
2. Install Docker and Docker Compose, or follow the documented equivalent.
3. Clone the repository.
4. Create a server-local environment file from `deployment/env.example`.
5. Configure public-demo mode and paths through environment variables.
6. Copy or mount only approved model artifacts and public/delayed/static or
   otherwise approved non-sensitive data.
7. Run the public-demo release gate:
   - at least one real approved model exists
   - MLflow and SQLite sync is current
   - required evidence is loaded
   - at least one approved non-sensitive data source exists
8. If the gate fails, deploy only degraded-demo mode with visible limitations
   and no public prediction availability claim.
9. Start the Streamlit and FastAPI services.
10. Configure only the required firewall and ingress ports.
11. Open the public URL and run the public demo validation below.

High availability, autoscaling, paid production deployment, brokerage
integration, and live trading infrastructure are out of scope.

## Manual Validation Flow

1. Confirm educational/research disclaimer appears before or during prediction.
2. Confirm the model selector shows approved models only.
3. Confirm public demo does not show mock/demo-only/experimental/dummy models.
4. Confirm registry conflicts or stale/incomplete sync hide the affected model
   and show an unavailable-model message.
5. Inspect model evidence:
   - key metrics
   - evaluation period
   - supported stock universe
   - limitations
   - data-quality notes
   - historical-performance caveat
   - data-as-of timestamp
   - evidence load status
6. Select a supported IDX stock.
7. Confirm the selected ticker's prediction becomes the primary visible content
   after valid selections and passing evidence/data gates.
8. Confirm the primary prediction view shows, before dense methodology or raw
   traceability:
   - ticker
   - model signal
   - Low/Medium/High confidence
   - why this signal appeared
   - key limitations
9. Confirm any manual action uses plain wording such as `Predict` and does not
   use `Request educational prediction`.
10. Confirm limitations read like product guidance rather than raw metadata,
    cell text, or unexplained tags.
11. Confirm detailed evidence, methodology, and traceability remain available as
    secondary or expandable sections.
12. Try an unsupported stock and confirm it is marked unavailable, blocks
   prediction until removed or replaced, and records only aggregate
   non-personal support interest.
13. Request prediction if the flow still uses a manual action.
14. Confirm each successful output includes:
   - ticker
   - prediction target
   - model signal
   - Low/Medium/High confidence
   - plain-language confidence explanation
   - context summary
   - limitation summary
   - selected model name
   - selected model identifier/version
   - data-as-of timestamp
   - feature-generation timestamp
   - prediction timestamp
   - evidence reference
   - evaluation context
   - disclaimer text
15. Confirm missing or invalid feature-generation timestamp fails prediction
    with a clear error.
16. Confirm no screen or response uses buy/sell recommendations, guaranteed
   profit, position sizing, allocation advice, or personalized guidance.
17. Confirm stale/missing/unavailable/not-loaded evidence, stale/missing data,
    failed prediction, and invalid response cases show unavailable/error states
    instead of misleading output.

## Planned Test Command

```bash
pytest tests/unit tests/contract tests/integration tests/ml_safety tests/deployment
```

## Expected Reviewer Outcome

A reviewer can open a public URL, inspect a real approved model's concise
evidence summary, select a supported IDX stock, quickly understand the
prediction-first view, and then inspect confidence, limitations, data-as-of
timestamp, feature-generation timestamp, prediction timestamp, traceability, and
the educational/research boundary without running code locally. If release
gates are not satisfied, the reviewer sees a clearly labelled degraded demo
rather than a claim of full prediction availability.
