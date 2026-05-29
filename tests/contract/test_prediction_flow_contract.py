from backend.schemas.contracts import PredictionRequest, PredictionResponse
from backend.services.evidence_service import EvidenceService
from backend.services.model_service import ModelService
from backend.services.prediction_service import PredictionService
from backend.services.stock_service import StockService


def test_happy_path_contracts(seeded_repo):
    models = ModelService(seeded_repo).list_models()
    assert models["models"]
    model = models["models"][0]

    evidence = EvidenceService(seeded_repo).get_model_evidence(model["model_id"], model["model_version"])
    assert evidence["model_id"] == model["model_id"]

    stocks = StockService(seeded_repo).list_stocks(model["model_id"], model["model_version"], "BBCA")
    assert stocks["stocks"][0]["support_status"] == "supported"

    request = PredictionRequest(
        model_id=model["model_id"],
        model_version=model["model_version"],
        tickers=["BBCA"],
        target="next_market_session_direction",
    )
    response = PredictionService(seeded_repo).request_prediction(request)
    parsed = PredictionResponse.model_validate(response)
    assert parsed.predictions
    assert parsed.blocked == []

