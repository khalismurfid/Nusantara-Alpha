from app_streamlit.copy.disclaimers import EDUCATIONAL_DISCLAIMER, FORBIDDEN_ADVICE_PHRASES, contains_forbidden_advice
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

