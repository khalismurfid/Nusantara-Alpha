from app_streamlit.copy.disclaimers import FORBIDDEN_ADVICE_PHRASES
from app_streamlit.components.unavailable_state import format_unavailable_state


def test_error_copy_avoids_forbidden_advice_terms():
    message = format_unavailable_state("unsupported_stock", "This ticker is unsupported.", "Remove it.")
    rendered = str(message).lower()
    for phrase in FORBIDDEN_ADVICE_PHRASES:
        assert phrase not in rendered


def test_common_unavailable_states_use_plain_copy_without_reason_codes():
    states = [
        (
            "unsupported_stock",
            "This model has not been reviewed for GOTO yet.",
            "Choose one of the supported tickers for this model.",
        ),
        (
            "stale_data",
            "The latest required market data is not fresh enough for this prediction.",
            "Try again after data is refreshed.",
        ),
        (
            "missing_required_evidence",
            "Required model evidence is unavailable.",
            "Select another approved model.",
        ),
        (
            "registry_conflict",
            "This model is temporarily unavailable while its approval records are reviewed.",
            "Select another model or try again later.",
        ),
        (
            "invalid_prediction_response",
            "Prediction generation failed or returned an invalid response.",
            "Try again later or choose another ticker.",
        ),
    ]

    for reason, message, next_step in states:
        formatted = format_unavailable_state(reason, message, next_step)
        rendered = str(formatted).lower()
        assert reason not in rendered
        assert "_" not in formatted["title"]
        for phrase in FORBIDDEN_ADVICE_PHRASES:
            assert phrase not in rendered
