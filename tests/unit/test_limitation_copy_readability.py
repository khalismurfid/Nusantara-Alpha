import pytest

from app_streamlit.components.evidence_panel import format_evidence
from app_streamlit.copy.disclaimers import assert_limitation_copy_readable
from tests.unit.ui_fixtures import evidence_response


def test_raw_limitation_fragments_are_rejected():
    with pytest.raises(ValueError):
        assert_limitation_copy_readable("Limited universe")

    with pytest.raises(ValueError):
        assert_limitation_copy_readable("No guarantee of future accuracy")


def test_evidence_formatter_rewrites_raw_limitation_fragments():
    formatted = format_evidence(
        evidence_response(limitations=["Limited universe", "No guarantee of future accuracy"])
    )

    rendered = " ".join(formatted["limitations"]).lower()
    assert "limited universe" not in rendered
    assert "no guarantee" not in rendered
    assert "separate validation" in rendered
    assert "historical test period" in rendered
