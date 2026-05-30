"""Market-data quality and bias controls."""

from __future__ import annotations

from dataclasses import dataclass, field

BLOCKING_FLAGS = {
    "future_information",
    "untraceable_data",
    "stale_required_data",
    "missing_required_data",
    "ticker_identity_unknown",
    "delisted_without_adjustment",
}


@dataclass(frozen=True)
class MarketDataAssessment:
    allowed: bool
    flags: list[str] = field(default_factory=list)
    blocking_reason: str | None = None
    notes: list[str] = field(default_factory=list)


def assess_market_data(freshness_status: str | None, quality_flags: list[str] | None = None) -> MarketDataAssessment:
    flags = quality_flags or []
    notes: list[str] = []
    if freshness_status == "missing":
        return MarketDataAssessment(False, flags, "missing_data", ["The latest required market data is not available yet."])
    if freshness_status == "stale":
        return MarketDataAssessment(False, flags, "stale_data", ["The latest required market data is not fresh enough for this prediction."])
    blocking = sorted(set(flags) & BLOCKING_FLAGS)
    if blocking:
        return MarketDataAssessment(False, flags, "unreliable_or_untraceable", [f"Blocking data quality flag: {flag}" for flag in blocking])
    for flag in flags:
        notes.append(f"Data quality note: {flag}")
    return MarketDataAssessment(True, flags, None, notes)
