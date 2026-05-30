from app_streamlit.components.framing import framing_text


def test_project_framing_is_client_facing_and_plain_language():
    text = framing_text().lower()

    assert "quick outlook" in text
    assert "choose a stock" in text
    assert "upward, downward, or neutral" in text
    assert "plain language" in text
    assert "approved model" not in text
    assert "idx market data" not in text
