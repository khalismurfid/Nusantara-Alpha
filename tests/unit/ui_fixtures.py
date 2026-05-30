"""Reusable UI fixtures for Streamlit presentation tests."""

from __future__ import annotations


def prediction_output(**overrides):
    payload = {
        "prediction_id": "pred-001",
        "ticker": "BBCA",
        "prediction_target": "next_market_session_direction",
        "model_signal": "up",
        "confidence_category": "Medium",
        "numeric_confidence": 0.62,
        "confidence_explanation": "Medium confidence means the model sees a moderate signal, but it can still be wrong.",
        "context_summary": "Recent price and momentum features leaned positive in the latest available sample.",
        "limitation_summary": "This result covers a small demo set of liquid IDX names and may not transfer to every market condition.",
        "model_name": "IDX Direction Baseline",
        "model_id": "idx-direction-baseline",
        "model_version": "2026.05",
        "data_as_of_timestamp": "2026-05-28T16:00:00+07:00",
        "feature_generation_timestamp": "2026-05-28T17:00:00+07:00",
        "prediction_timestamp": "2026-05-28T17:05:00+07:00",
        "evaluation_context": "Backtest from 2024-01-01 to 2026-05-01.",
        "evidence_reference": "evidence-idx-direction-baseline-2026.05",
        "disclaimer_text": "Educational research only, not financial advice.",
        "disclaimer_version": "2026-05-29.v1",
    }
    payload.update(overrides)
    return payload


def evidence_response(**overrides):
    payload = {
        "evidence_id": "evidence-idx-direction-baseline-2026.05",
        "model_id": "idx-direction-baseline",
        "model_version": "2026.05",
        "evidence_type": "backtest",
        "evaluation_period": {"start": "2024-01-01", "end": "2026-05-01"},
        "key_metrics": [
            {
                "name": "Directional accuracy",
                "value": "54%",
                "interpretation": "Slightly above a naive directional baseline in the tested period.",
            }
        ],
        "supported_universe": ["BBCA", "TLKM", "ASII"],
        "limitations": [
            "The model currently covers a small group of liquid IDX names, so unsupported stocks need separate validation."
        ],
        "data_quality_notes": ["Uses static delayed demo data reviewed through 2026-05-01."],
        "historical_performance_caveat": "Historical performance may not generalize to future market sessions.",
        "evidence_status": "complete",
        "evidence_load_status": "loaded",
        "evidence_as_of": "2026-05-28T12:00:00+07:00",
        "data_source_mode": "static",
    }
    payload.update(overrides)
    return payload


def stock_response(**overrides):
    payload = {
        "ticker": "BBCA",
        "name": "Bank Central Asia Tbk",
        "exchange": "IDX",
        "support_status": "supported",
        "data_as_of": "2026-05-28T16:00:00+07:00",
        "freshness_status": "fresh",
        "market_data_flags": [],
    }
    payload.update(overrides)
    return payload


def demo_status(**overrides):
    payload = {
        "environment_name": "local",
        "app_status": "available",
        "api_status": "available",
        "public_predictions_available": False,
        "release_status": "degraded",
        "real_approved_model_available": False,
        "approved_data_source_available": True,
        "data_source_mode": "static",
        "data_as_of": "2026-05-28T16:00:00+07:00",
        "demo_limitations": "Local demo data is static and intended for product review.",
        "disclaimer": "Educational research only, not financial advice.",
    }
    payload.update(overrides)
    return payload
