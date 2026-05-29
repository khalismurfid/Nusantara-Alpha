"""Pydantic contracts matching the public OpenAPI design."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


StrictBase = ConfigDict(extra="forbid")


class HealthResponse(BaseModel):
    model_config = StrictBase
    status: Literal["ok"]


DataSourceMode = Literal["sample", "mock", "public", "delayed", "static", "approved", "live", "unavailable"]
RuntimeContext = Literal["local", "test", "public_demo"]


class DemoStatusResponse(BaseModel):
    model_config = StrictBase
    environment_name: Literal["local", "public_demo", "review"]
    app_status: Literal["available", "degraded", "unavailable"]
    api_status: Literal["available", "degraded", "unavailable"]
    public_predictions_available: bool
    release_status: Literal["full", "degraded", "unavailable"]
    real_approved_model_available: bool
    approved_data_source_available: bool
    data_source_mode: DataSourceMode
    data_as_of: datetime | None
    demo_limitations: str
    disclaimer: str
    public_demo_url: str | None = None
    release_gate_reason: str | None = None
    unavailable_reason: str | None = None


class DateRange(BaseModel):
    model_config = StrictBase
    start: date
    end: date


class Metric(BaseModel):
    model_config = StrictBase
    name: str
    value: str
    interpretation: str


class CuratedModel(BaseModel):
    model_config = StrictBase
    model_id: str
    model_version: str
    model_name: str
    description: str
    status: Literal["approved"]
    model_origin: Literal["real", "local_mock", "demo_only", "experimental"]
    public_demo_eligible: bool
    registry_sync_status: Literal["current", "stale", "incomplete", "conflict"]
    evaluation_period: DateRange
    supported_universe_id: str
    evidence_available: bool
    evidence_load_status: Literal["loaded", "missing", "stale", "unavailable", "not_loaded"]
    limitations: list[str]
    registry_conflict_reason: str | None = None


class ModelEvidence(BaseModel):
    model_config = StrictBase
    evidence_id: str
    model_id: str
    model_version: str
    evidence_type: Literal["backtest", "paper_trading", "validation_summary"]
    evaluation_period: DateRange
    key_metrics: list[Metric]
    supported_universe: list[str]
    limitations: list[str]
    data_quality_notes: list[str]
    historical_performance_caveat: str
    evidence_status: Literal["complete", "weak", "data_limited", "missing", "stale"]
    evidence_load_status: Literal["loaded", "missing", "stale", "unavailable", "not_loaded"]
    evidence_as_of: datetime
    data_source_mode: DataSourceMode
    paper_trading_summary: str | None = None


class StockAvailability(BaseModel):
    model_config = StrictBase
    ticker: str
    name: str
    exchange: Literal["IDX"]
    support_status: Literal["supported", "unsupported", "temporarily_unavailable"]
    unavailable_reason: str | None = None
    data_as_of: datetime | None = None
    freshness_status: Literal["fresh", "stale", "missing"] | None = None
    market_data_flags: list[str] = Field(default_factory=list)


class PredictionRequest(BaseModel):
    model_config = StrictBase
    model_id: str
    model_version: str
    tickers: list[str] = Field(min_length=1)
    target: Literal["next_market_session_direction"]


class PredictionOutput(BaseModel):
    model_config = StrictBase
    prediction_id: str
    ticker: str
    prediction_target: str
    model_signal: Literal["up", "down", "neutral", "unavailable"]
    confidence_category: Literal["Low", "Medium", "High"]
    confidence_explanation: str
    context_summary: str
    limitation_summary: str
    model_name: str
    model_id: str
    model_version: str
    data_as_of_timestamp: datetime
    feature_generation_timestamp: datetime
    prediction_timestamp: datetime
    evaluation_context: str
    evidence_reference: str
    disclaimer_text: str
    numeric_confidence: float | None = Field(default=None, ge=0, le=1)
    disclaimer_version: str | None = None


BlockedReason = Literal[
    "unsupported_stock",
    "stale_data",
    "missing_data",
    "missing_required_evidence",
    "stale_required_evidence",
    "unavailable_required_evidence",
    "evidence_not_loaded",
    "chronology_violation",
    "missing_feature_timestamp",
    "invalid_feature_timestamp",
    "unreliable_or_untraceable",
    "unavailable_model",
    "registry_conflict",
    "registry_sync_stale",
    "registry_sync_incomplete",
    "public_demo_model_unavailable",
    "public_demo_release_gate_failed",
    "mock_model_blocked_in_public_demo",
    "invalid_prediction_response",
]


class BlockedPrediction(BaseModel):
    model_config = StrictBase
    ticker: str
    reason: BlockedReason
    user_message: str
    next_step: str | None = None


class PredictionResponse(BaseModel):
    model_config = StrictBase
    request_id: str
    predictions: list[PredictionOutput]
    blocked: list[BlockedPrediction]
    disclaimer: str


class UnsupportedStockInterestRequest(BaseModel):
    model_config = StrictBase
    ticker: str
    reason: str
    model_id: str | None = None


class UnsupportedStockInterestResponse(BaseModel):
    model_config = StrictBase
    accepted: bool
    message: str


class ErrorResponse(BaseModel):
    model_config = StrictBase
    error_code: str
    message: str
    next_step: str | None = None


class PredictionLogRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    request_id: str
    model_id: str
    model_version: str
    tickers: list[str]
    status: Literal["success", "blocked", "failed"]
    prediction_timestamp: datetime
    data_as_of_timestamp: datetime | None = None
    feature_generation_timestamp: datetime | None = None
    prediction_output: dict[str, Any] | None = None
    confidence: str | None = None
    disclaimer_version: str | None = None
    error_message: str | None = None
    runtime_context: RuntimeContext = "local"

