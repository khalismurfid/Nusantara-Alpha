from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService


def test_unavailable_model_returns_blocked_prediction(seeded_repo):
    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="missing-model",
            model_version="1",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )
    assert response["predictions"] == []
    assert response["blocked"][0]["reason"] == "unavailable_model"


def test_invalid_prediction_response_is_not_displayed_as_valid(seeded_repo, monkeypatch):
    from backend.services import prediction_service

    def bad_predict(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(prediction_service, "predict_next_session", bad_predict)
    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )
    assert response["predictions"] == []
    assert response["blocked"][0]["reason"] == "invalid_prediction_response"

