from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService


def test_blocked_logs_are_sanitized(seeded_repo):
    PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="missing-model",
            model_version="1",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )
    log = seeded_repo.list_prediction_logs()[-1]
    assert log["status"] == "blocked"
    assert "secret" not in str(log).lower()
    assert "/Users/" not in str(log)

