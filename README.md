# Nusantara Alpha

Nusantara Alpha is an educational Indonesian equity prediction product for
portfolio and academic review. Users choose a curated model, select a supported
IDX ticker, and immediately see a near-term model signal as the main content.
The prediction view leads with the ticker, signal, confidence, context, and key
limitations, while evidence, methodology, timestamps, and traceability remain
available for review.

The current prediction engine trains a pooled logistic regression model on
approved historical IDX OHLCV data stored in SQLite. It uses triple-barrier
labels, so signals can be upward, downward, or neutral based on a profit
target, stop-loss, and time barrier. The first baseline looks up to five
trading days ahead with symmetric 20-day ATR barriers. It also shows an
exploratory market ranking for supported stocks.

The product is not financial advice. It does not provide trade instructions,
personalized guidance, position sizing, portfolio allocation advice, guaranteed
outcomes, brokerage integration, order placement, or real-money execution.

## Local Setup

1. Create a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

3. Seed a local database:

```bash
python3 -m storage.seed_local_demo
```

The local seed includes a small approved static OHLCV fixture for BBCA, TLKM,
and ASII. For broader IDX coverage, load an approved universe CSV and fetch
yfinance `.JK` OHLCV data into SQLite through `ml.market_data.yfinance_ingestion`
before running the app:

```bash
nusantara-ingest-yfinance \
  --universe data/approved_idx_universe.csv \
  --source approved-public-idx-list \
  --source-date 2026-05-30 \
  --start 2018-01-01 \
  --model-id idx-direction-baseline \
  --universe-id idx-approved-universe \
  --refresh-baseline-artifact
```

4. Start the API:

```bash
uvicorn backend.main:app --reload
```

5. Start the app:

```bash
streamlit run app_streamlit/app.py
```

## Validation

```bash
python3 -m pytest tests/unit tests/contract tests/integration tests/ml_safety tests/deployment
```

## Public Demo

Public-demo prediction availability requires a real approved model, current
registry synchronization, loaded required evidence, and approved non-sensitive
data. If any gate is missing, the app may run only as a degraded demo with
prediction unavailable.

For a small VPS deployment, use the Docker Compose stack in `deployment/`.
The public demo exposes Streamlit on port `8501`; the FastAPI backend is bound
to localhost on the server and is not intended to be opened directly to public
reviewers. Approved runtime state must be copied separately into `.local/`
because local databases, model artifacts, secrets, and private data are not
committed to Git.
