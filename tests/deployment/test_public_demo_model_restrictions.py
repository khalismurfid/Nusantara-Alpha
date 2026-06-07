from backend.schemas.contracts import PredictionRequest
from backend.services.model_service import ModelService
from backend.services.prediction_service import PredictionService
from app_streamlit.app import public_prediction_is_available


def test_public_demo_hides_local_mock_models(seeded_repo):
    seeded_repo.upsert_model(
        {
            "model_id": "local-dummy-flow",
            "model_version": "dev",
            "model_name": "Local Dummy Flow",
            "description": "Development-only flow fixture that is never public-demo eligible.",
            "status": "approved",
            "model_origin": "local_mock",
            "public_demo_eligible": False,
            "supported_universe_id": "idx-approved-universe",
            "evaluation_period_start": "2024-01-01",
            "evaluation_period_end": "2024-12-31",
            "evidence_available": True,
            "evidence_load_status": "loaded",
            "limitations": ["Development-only dummy output"],
            "mlflow_run_id": None,
            "mlflow_model_uri": None,
            "sqlite_catalogue_revision": "local",
            "mlflow_registry_revision": "local",
            "registry_sync_status": "current",
            "registry_conflict_reason": None,
        }
    )
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
    assert response["blocked"][0]["reason"] == "unavailable_model"


def test_prediction_first_ui_blocks_when_public_demo_gate_is_closed():
    demo_status = {
        "release_status": "degraded",
        "public_predictions_available": False,
        "unavailable_reason": "Public prediction is not available until gates pass.",
    }

    assert public_prediction_is_available(demo_status) is False
