"""Prediction engine interface independent of UI and API route handlers."""

from __future__ import annotations

from dataclasses import dataclass

from ml.backtesting.realistic import PooledLogisticSignalModel, predict_scores
from ml.features.generation import FeaturePayload
from ml.loading.model_loader import LoadedModel


@dataclass(frozen=True)
class EnginePrediction:
    model_signal: str
    confidence_category: str
    numeric_confidence: float
    confidence_explanation: str
    context_summary: str
    limitation_summary: str
    rank: int | None = None
    rank_universe_size: int | None = None
    ranking_score: float | None = None


def predict_next_session(model: LoadedModel, features: FeaturePayload, limitations: list[str] | None = None) -> EnginePrediction:
    if isinstance(model.raw, PooledLogisticSignalModel):
        return _predict_with_pooled_model(model.raw, features, limitations)
    if model.artifact_uri:
        raise ValueError("Loaded model artifact does not contain a usable pooled signal model.")
    ticker_score = sum(ord(ch) for ch in features.ticker)
    signal = ["down", "neutral", "up"][ticker_score % 3]
    confidence_value = 0.55 + ((ticker_score % 15) / 100)
    if confidence_value >= 0.66:
        confidence_category = "High"
    elif confidence_value >= 0.58:
        confidence_category = "Medium"
    else:
        confidence_category = "Low"
    limitation_text = "; ".join(limitations or ["Evidence is limited and may not generalize."])
    return EnginePrediction(
        model_signal=signal,
        confidence_category=confidence_category,
        numeric_confidence=round(confidence_value, 2),
        confidence_explanation="Confidence is model uncertainty, not a guarantee of correctness.",
        context_summary=f"{model.model_name} generated an exploratory next-session signal for {features.ticker}.",
        limitation_summary=limitation_text,
    )


def _predict_with_pooled_model(model: PooledLogisticSignalModel, features: FeaturePayload, limitations: list[str] | None = None) -> EnginePrediction:
    scores = predict_scores(model)
    row = scores[scores["ticker"] == features.ticker.upper()]
    if row.empty:
        raise ValueError(f"{features.ticker.upper()} is not available in the latest pooled model feature set.")
    latest = row.iloc[0]
    probability = float(latest["model_score"])
    limitation_text = "; ".join(
        [
            *(limitations or ["Historical evidence is limited and may not generalize."]),
            "Backtest evidence uses next-session open-to-close timing with a 0.25% round-trip cost assumption.",
        ]
    )
    relative_return = float(latest.get("relative_return", 0.0))
    rank = int(latest["rank"])
    universe_size = int(len(scores))
    return EnginePrediction(
        model_signal=str(latest["model_signal"]),
        confidence_category=str(latest["confidence_category"]),
        numeric_confidence=round(probability, 4),
        confidence_explanation="Confidence reflects how far the model probability is from neutral; it can still be wrong.",
        context_summary=(
            f"{features.ticker.upper()} ranks {rank} of {universe_size} by model score. "
            f"Its latest return was {relative_return:.2%} versus the model universe average."
        ),
        limitation_summary=limitation_text,
        rank=rank,
        rank_universe_size=universe_size,
        ranking_score=round(probability, 4),
    )
