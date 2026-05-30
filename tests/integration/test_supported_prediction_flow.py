from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService


def test_supported_prediction_flow_returns_structured_prediction(seeded_repo):
    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )

    output = response["predictions"][0]
    assert output["ticker"] == "BBCA"
    assert output["model_signal"] in {"up", "down", "neutral"}
    assert output["confidence_category"] in {"Low", "Medium", "High"}
    assert output["rank"] is not None
    assert output["rank_universe_size"] == 3
    assert "ranks" in output["context_summary"].lower()
    assert "not financial advice" in output["disclaimer_text"].lower()
