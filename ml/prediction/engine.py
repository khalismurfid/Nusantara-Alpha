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
    raise ValueError("Baseline logistic regression model is required for prediction.")


def _predict_with_pooled_model(model: PooledLogisticSignalModel, features: FeaturePayload, limitations: list[str] | None = None) -> EnginePrediction:
    scores = predict_scores(model)
    row = scores[scores["ticker"] == features.ticker.upper()]
    if row.empty:
        raise ValueError(f"{features.ticker.upper()} is not available in the latest pooled model feature set.")
    latest = row.iloc[0]
    probability = float(latest["model_score"])
    upside_probability = float(latest.get("up_probability", 0.0))
    downside_probability = float(latest.get("down_probability", 0.0))
    neutral_probability = float(latest.get("neutral_probability", 0.0))
    limitation_text = "; ".join(
        [
            *(limitations or ["Historical evidence is limited and may not generalize."]),
            "Backtest evidence uses a 5-trading-day ATR barrier test with upward, downward, and neutral outcomes.",
        ]
    )
    relative_return = float(latest.get("relative_return", 0.0))
    rank = int(latest["rank"])
    universe_size = int(len(scores))
    return EnginePrediction(
        model_signal=str(latest["model_signal"]),
        confidence_category=str(latest["confidence_category"]),
        numeric_confidence=round(probability, 4),
        confidence_explanation="Confidence reflects the model's strongest class probability; it can still be wrong.",
        context_summary=(
            f"{features.ticker.upper()} ranks {rank} of {universe_size} by upside barrier probability. "
            f"Latest relative return was {relative_return:.2%}; class probabilities are "
            f"up {upside_probability:.0%}, neutral {neutral_probability:.0%}, down {downside_probability:.0%}."
        ),
        limitation_summary=limitation_text,
        rank=rank,
        rank_universe_size=universe_size,
        ranking_score=round(float(latest.get("ranking_score", upside_probability)), 4),
    )
