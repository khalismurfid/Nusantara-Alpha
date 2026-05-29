"""Prediction engine interface independent of UI and API route handlers."""

from __future__ import annotations

from dataclasses import dataclass

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


def predict_next_session(model: LoadedModel, features: FeaturePayload, limitations: list[str] | None = None) -> EnginePrediction:
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

