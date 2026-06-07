from app_streamlit.components.prediction_result import format_prediction_result
from tests.unit.ui_fixtures import prediction_output


def test_prediction_view_uses_primary_supporting_secondary_sections():
    formatted = format_prediction_result(prediction_output())

    assert list(formatted.keys()) == ["primary", "supporting", "secondary", "disclaimer"]
    assert formatted["primary"]["ticker"] == "BBCA"
    assert formatted["primary"]["signal"] == "UP - leans toward the upward barrier"
    assert formatted["primary"]["signal_badge"] == "UP"
    assert "upward barrier" in formatted["primary"]["signal_summary"].lower()
    assert formatted["primary"]["confidence"] == "Medium"
    assert formatted["primary"]["confidence_value"] == "62%"
    assert formatted["primary"]["target"] == "Near-term signal"
    assert formatted["primary"]["meta_items"][0]["label"] == "Model"

    assert formatted["supporting"]["why_signal_title"] == "What influenced the signal"
    assert formatted["supporting"]["limitations_title"] == "Important limitations"
    assert formatted["supporting"]["limitations"]
    assert formatted["supporting"]["insights"][0]["title"] == "Confidence"


def test_traceability_stays_secondary_but_key_timing_is_visible():
    formatted = format_prediction_result(prediction_output())

    primary_meta = {item["label"]: item["value"] for item in formatted["primary"]["meta_items"]}
    assert primary_meta["Market data reviewed"] == "2026-05-28T16:00:00+07:00"
    assert primary_meta["Signal generated"] == "2026-05-28T17:05:00+07:00"

    traceability = formatted["secondary"]["traceability"]
    assert traceability["model_id"] == "idx-direction-baseline"
    assert traceability["data_as_of"] == "2026-05-28T16:00:00+07:00"
    assert traceability["feature_generated_at"] == "2026-05-28T17:00:00+07:00"
    assert traceability["prediction_generated_at"] == "2026-05-28T17:05:00+07:00"
