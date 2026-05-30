# ML Safety Review

Date: 2026-05-29

Implemented controls:

- `ml/validation/chronology.py` validates data-as-of, feature-generation, and
  prediction timestamp order.
- `ml/validation/market_data.py` blocks stale, missing, unreliable, or
  untraceable data conditions.
- `backend/services/prediction_service.py` checks model approval, registry sync,
  evidence availability, supported tickers, data availability, chronology,
  feature timestamps, and prediction contract shape before returning outputs.
- `model_registry/approval.py` fails closed when catalogue and registry status
  are stale, incomplete, conflicted, or not public-demo eligible.
- Prediction logs store data-as-of, feature-generation, prediction timestamp,
  model identity, ticker, confidence, disclaimer version, and status.
- The realistic prediction engine trains a pooled logistic regression on
  historical OHLCV rows stored in SQLite and uses next-session open-to-close
  targets only after feature rows have been generated from prior data.
- Ranking responses reuse the same approved model, loaded evidence, and stored
  market-data constraints; rankings are educational context, not advice.

Residual risk:

- Full all-IDX coverage depends on the approved universe file and yfinance data
  availability. Missing, stale, sparse, halted, delisted, or failed-download
  tickers must remain excluded or blocked until reviewed.
