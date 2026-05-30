from app_streamlit.components.unavailable_state import format_unavailable_state


def test_unavailable_state_hides_internal_reason_code():
    formatted = format_unavailable_state(
        "unsupported_stock",
        "This model has not been reviewed for GOTO yet.",
        "Choose one of the supported tickers for this model.",
    )

    rendered = str(formatted).lower()
    assert formatted["title"] == "Ticker not available for this model"
    assert "unsupported_stock" not in rendered
    assert "this model has not been reviewed" in formatted["message"].lower()
    assert "choose one" in formatted["next_step"].lower()


def test_registry_conflict_copy_is_customer_facing():
    formatted = format_unavailable_state(
        "registry_conflict",
        "This model is temporarily unavailable while its approval records are reviewed.",
        "Select another model or try again later.",
    )

    rendered = str(formatted).lower()
    assert "registry_conflict" not in rendered
    assert "metadata" not in rendered
    assert "approval records" in rendered
