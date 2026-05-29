"""Feature generation interface with explicit feature timestamp traceability."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class FeaturePayload:
    ticker: str
    features: dict[str, Any]
    data_as_of_timestamp: datetime
    feature_generation_timestamp: datetime


def generate_features(ticker: str, data_as_of_timestamp: datetime, feature_generation_timestamp: datetime | None = None) -> FeaturePayload:
    feature_ts = feature_generation_timestamp or datetime.now(timezone.utc).replace(microsecond=0)
    return FeaturePayload(
        ticker=ticker.upper(),
        data_as_of_timestamp=data_as_of_timestamp,
        feature_generation_timestamp=feature_ts,
        features={
            "ticker_length": len(ticker),
            "data_year": data_as_of_timestamp.year,
        },
    )

