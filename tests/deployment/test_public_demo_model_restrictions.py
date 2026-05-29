from backend.schemas.contracts import PredictionRequest
from backend.services.model_service import ModelService
from backend.services.prediction_service import PredictionService


def test_public_demo_hides_local_mock_models(seeded_repo):
    models = ModelService(seeded_repo, runtime_context="public_demo").list_models()["models"]
    assert {model["model_origin"] for model in models} == {"real"}


def test_public_demo_blocks_dummy_prediction_model(seeded_repo):
    response = PredictionService(seeded_repo, runtime_context="public_demo").request_prediction(
        PredictionRequest(
            model_id="local-dummy-flow",
            model_version="dev",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )
    assert response["predictions"] == []
    assert response["blocked"][0]["reason"] in {"public_demo_model_unavailable", "mock_model_blocked_in_public_demo"}

