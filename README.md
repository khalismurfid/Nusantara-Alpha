# Nusantara Alpha

Nusantara Alpha is an educational Indonesian equity prediction product for
portfolio and academic review. Users choose a curated model, inspect historical
evidence, choose supported IDX stocks, request a next-market-session model
signal, and interpret the result with confidence, limitations, timestamps, and
traceability.

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

