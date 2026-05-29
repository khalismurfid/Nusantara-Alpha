from app_streamlit.copy.disclaimers import FORBIDDEN_ADVICE_PHRASES
from app_streamlit.components.unavailable_state import format_unavailable_state


def test_error_copy_avoids_forbidden_advice_terms():
    message = format_unavailable_state("unsupported_stock", "This ticker is unsupported.", "Remove it.")
    rendered = str(message).lower()
    for phrase in FORBIDDEN_ADVICE_PHRASES:
        assert phrase not in rendered

