# Methodology

Nusantara Alpha is an educational research and portfolio demonstration product.
Predictions are exploratory model signals for the next IDX market session, not
financial advice or trade instructions.

The current implementation uses a curated model catalogue, loaded model
evidence, supported-stock metadata, data availability checks, and explicit
prediction contracts. Users see a concise evidence summary before or alongside
the prediction view, with detailed methodology and traceability available as
secondary review context.

The first realistic prediction engine is a pooled cross-stock logistic
regression model trained on triple-barrier outcomes. It trains across the
currently approved IDX universe rather than fitting one isolated model per
stock, so it can use stock-specific features together with market and peer
context. Historical OHLCV data is stored in SQLite before prediction; yfinance
ingestion is a separate offline step and is not called from the
customer-facing prediction request.

Approved `.JK` OHLCV rows can be loaded with the `nusantara-ingest-yfinance`
command after preparing an approved IDX universe CSV. The command updates the
IDX universe, market-price cache, supported-stock metadata, and model data
availability when model and universe identifiers are provided.

Features are generated from data available at or before the selected data-as-of
timestamp. The supervised target is built with a triple-barrier method:
simulated entry occurs at the next session open, an upward label is assigned if
the profit-taking barrier is reached first, a downward label is assigned if the
stop-loss barrier is reached first, and a neutral label is assigned when the
vertical time barrier expires or an OHLC bar cannot safely identify which price
barrier came first. The current baseline looks up to five IDX trading sessions
ahead and uses symmetric barriers set one 20-day ATR above and below the entry
price.

Backtest evidence uses chronological splits and the same triple-barrier timing
assumption. Evidence applies a 0.25% round-trip transaction-cost assumption for
simulated upward signals. Downward and neutral signals are evaluated for label
accuracy but are not presented as short selling, position sizing, or trading
instructions.

Evidence includes key metrics, evaluation period, covered stocks, readable
limitations, data-quality notes, evidence status, evidence load status, and the
caveat that historical performance may not generalize to future market sessions.
The product can also show an exploratory market ranking across supported
tickers. Ranking is context for model interpretation only; it is not a
recommendation or portfolio allocation tool. Paper-trading evidence is displayed
separately when it exists, but full paper-trading generation logic remains
deferred.

Chronological integrity is enforced through data-as-of timestamps,
feature-generation timestamps, prediction timestamps, and validation that
future information is not used for historical evidence or near-term prediction
outputs.
