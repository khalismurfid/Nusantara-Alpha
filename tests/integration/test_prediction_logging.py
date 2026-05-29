from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService


def test_successful_prediction_is_logged_with_traceability(seeded_repo):
    PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["ASII"],
            target="next_market_session_direction",
        )
    )
    logs = seeded_repo.list_prediction_logs()
    assert logs
    log = logs[-1]
    assert log["model_version"] == "2026.05"
    assert log["tickers"] == ["ASII"]
    assert log["data_as_of_timestamp"]
    assert log["feature_generation_timestamp"]
    assert log["prediction_timestamp"]
    assert log["disclaimer_version"]
    assert log["status"] == "success"

