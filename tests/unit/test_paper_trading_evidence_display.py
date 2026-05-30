from app_streamlit.components.paper_trading_evidence import format_paper_trading_evidence


def test_paper_trading_evidence_is_separate_when_present():
    formatted = format_paper_trading_evidence({"paper_trading_summary": "Observed separately."})
    assert formatted["available"] is True
    assert formatted["section_title"] == "Paper-trading evidence"
    assert formatted["placement"] == "secondary"
    assert formatted["summary"] == "Observed separately."


def test_paper_trading_absence_does_not_require_generation_logic():
    formatted = format_paper_trading_evidence({"paper_trading_summary": None})
    assert formatted["available"] is False
    assert formatted["placement"] == "secondary"
