# Data Rules

`data/sample/` is for small local-only fixtures used to develop and test the
product flow. Mock catalogues, mock evidence, and dummy predictions must stay
local or test-only and must never be public-demo eligible.

Real IDX market data should be fetched through the yfinance ingestion layer and
stored in SQLite before the app is used. Do not fetch live market data during a
customer prediction request. The approved universe file should contain at least
`ticker` and `company_name`; Yahoo symbols are derived as `<TICKER>.JK` unless a
`yahoo_symbol` column is supplied.

After installing the project, approved `.JK` OHLCV rows can be ingested with:

```bash
nusantara-ingest-yfinance \
  --universe data/approved_idx_universe.csv \
  --source approved-public-idx-list \
  --source-date 2026-05-30 \
  --start 2018-01-01 \
  --model-id idx-direction-baseline \
  --universe-id idx-liquid-demo
```

The public demo may use only public, delayed, static, or otherwise approved
non-sensitive data with a real approved model. Do not commit secrets,
credentials, private datasets, proprietary files, restricted source data, or
unrestricted internal artifacts.
