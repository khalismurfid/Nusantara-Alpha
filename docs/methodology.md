# Methodology

Nusantara Alpha is an educational research and portfolio demonstration product.
Predictions are exploratory model signals for the next IDX market session, not
financial advice or trade instructions.

The first implementation uses a curated model catalogue, loaded model evidence,
supported-stock metadata, data availability checks, and explicit prediction
contracts. Users inspect historical evidence before requesting a prediction.

Evidence includes key metrics, evaluation period, supported universe,
limitations, data-quality notes, evidence status, evidence load status, and the
caveat that historical performance may not generalize to future market sessions.
Paper-trading evidence is displayed separately when it exists, but full
paper-trading generation logic is deferred until evidence exists and the core
product flow is stable.

Chronological integrity is enforced through data-as-of timestamps,
feature-generation timestamps, prediction timestamps, and validation that
future information is not used for historical evidence or next-session
prediction outputs.

