"""Local-only dummy predictor for development flow wiring."""

from __future__ import annotations

from ml.prediction.engine import EnginePrediction


def predict_local_dummy(ticker: str, runtime_context: str) -> EnginePrediction:
    if runtime_context == "public_demo":
        raise ValueError("Dummy prediction output is blocked in public demo mode.")
    return EnginePrediction(
        model_signal="neutral",
        confidence_category="Low",
        numeric_confidence=0.5,
        confidence_explanation="Dummy confidence is only for local flow testing.",
        context_summary=f"Local development-only dummy signal for {ticker.upper()}.",
        limitation_summary="Development-only dummy output. Not public-demo eligible.",
    )

