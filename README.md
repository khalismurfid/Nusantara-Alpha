# Nusantara Alpha

Nusantara Alpha is an educational Indonesian equity prediction product for
portfolio and academic review. Users choose a curated model, select a supported
IDX ticker, and immediately see a next-market-session model signal as the main
content. The prediction view leads with the ticker, signal, confidence, context,
and key limitations, while evidence, methodology, timestamps, and traceability
remain available for review.

The current prediction engine trains a pooled logistic regression model on
approved historical IDX OHLCV data stored in SQLite. It evaluates next-session
open-to-close behavior with a 0.25% round-trip transaction-cost assumption and
shows an exploratory market ranking for supported stocks.

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
  --universe-id idx-liquid-demo
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
