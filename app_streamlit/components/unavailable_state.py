"""Unavailable and error state presentation helpers."""

from __future__ import annotations


UNAVAILABLE_TITLES = {
    "unsupported_stock": "Ticker not available for this model",
    "stale_data": "Prediction paused for this ticker",
    "missing_data": "Prediction data is not ready",
    "missing_required_evidence": "Model background is not ready",
    "stale_required_evidence": "Model background needs review",
    "unavailable_required_evidence": "Model background is unavailable",
    "evidence_not_loaded": "Model background is still loading",
    "chronology_violation": "Prediction paused for data timing review",
    "missing_feature_timestamp": "Prediction timing is incomplete",
    "invalid_feature_timestamp": "Prediction timing needs review",
    "unavailable_model": "Model temporarily unavailable",
    "registry_conflict": "Model temporarily unavailable",
    "registry_sync_stale": "Model temporarily unavailable",
    "registry_sync_incomplete": "Model temporarily unavailable",
    "public_demo_model_unavailable": "Signal unavailable",
    "public_demo_release_gate_failed": "Signal unavailable",
    "mock_model_blocked_in_public_demo": "Signal unavailable",
    "invalid_prediction_response": "Prediction could not be shown",
    "prediction_not_ready": "Prediction will appear when selections are ready",
}


def format_unavailable_state(reason: str, message: str, next_step: str | None = None) -> dict:
    return {
        "title": UNAVAILABLE_TITLES.get(reason, "Prediction unavailable"),
        "message": message,
        "next_step": next_step,
    }


def render_unavailable_state(reason: str, message: str, next_step: str | None = None, st=None) -> dict:
    formatted = format_unavailable_state(reason, message, next_step)
    if st is not None:
        st.warning(formatted["title"])
        st.write(formatted["message"])
        if next_step:
            st.caption(formatted["next_step"])
    return formatted
