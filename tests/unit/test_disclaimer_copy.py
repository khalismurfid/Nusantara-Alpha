from app_streamlit.copy.disclaimers import EDUCATIONAL_DISCLAIMER, FORBIDDEN_ADVICE_PHRASES, contains_forbidden_advice
from app_streamlit.copy.product_language import SECTION_TITLES
from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService


def test_disclaimer_is_educational_and_copy_safe():
    assert "educational research" in EDUCATIONAL_DISCLAIMER.lower()
    assert "not financial advice" in EDUCATIONAL_DISCLAIMER.lower()
    assert not contains_forbidden_advice(EDUCATIONAL_DISCLAIMER)


def test_prediction_text_avoids_forbidden_phrases(seeded_repo):
    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )
    rendered = str(response).lower()
    for phrase in FORBIDDEN_ADVICE_PHRASES:
        assert phrase not in rendered


def test_prediction_first_section_labels_are_plain_and_safe():
    labels = " ".join(SECTION_TITLES.values())
    assert "signal" in labels.lower()
    assert "confidence" in labels.lower()
    assert "what influenced the signal" in labels.lower()
    assert not contains_forbidden_advice(labels)
    assert "request educational prediction" not in labels.lower()


def test_confidence_copy_preserves_uncertainty_without_advice(seeded_repo):
    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )
    explanation = response["predictions"][0]["confidence_explanation"].lower()
    assert "confidence" in explanation
    assert "wrong" in explanation or "uncertain" in explanation
    assert not contains_forbidden_advice(explanation)
