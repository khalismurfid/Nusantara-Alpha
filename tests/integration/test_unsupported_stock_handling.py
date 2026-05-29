from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService
from backend.services.stock_service import StockService


def test_unsupported_stock_is_marked_and_logged_as_aggregate_interest(seeded_repo):
    stocks = StockService(seeded_repo).list_stocks("idx-direction-baseline", "2026.05", "GOTO")
    assert stocks["stocks"][0]["support_status"] == "unsupported"

    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["GOTO"],
            target="next_market_session_direction",
        )
    )
    assert response["blocked"][0]["reason"] == "unsupported_stock"
    assert seeded_repo.get_unsupported_interest("GOTO")["count"] == 1

