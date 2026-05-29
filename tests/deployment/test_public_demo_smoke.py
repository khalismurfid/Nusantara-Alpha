from backend.schemas.contracts import PredictionRequest
from backend.services.demo_status_service import DemoStatusService
from backend.services.prediction_service import PredictionService


def test_public_demo_smoke_flow_with_real_approved_model(seeded_repo):
    status = DemoStatusService(seeded_repo, runtime_context="public_demo").get_status()
    assert status["public_predictions_available"] is True
    response = PredictionService(seeded_repo, runtime_context="public_demo").request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )
    assert response["predictions"]
    assert "not financial advice" in response["disclaimer"].lower()

