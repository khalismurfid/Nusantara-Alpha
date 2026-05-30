from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService
from backend.services.stock_service import StockService


def test_unsupported_stock_is_marked_and_logged_as_aggregate_interest(seeded_repo):
    stocks = StockService(seeded_repo).list_stocks("idx-direction-baseline", "2026.05", "GOTO")
    assert stocks["stocks"][0]["support_status"] == "unsupported"
    assert stocks["stocks"][0]["unavailable_reason"] == "This model has not been reviewed for GOTO yet."

    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["GOTO"],
            target="next_market_session_direction",
        )
    )
    assert response["blocked"][0]["reason"] == "unsupported_stock"
    assert response["blocked"][0]["user_message"] == "This model has not been reviewed for GOTO yet."
    assert response["blocked"][0]["next_step"] == "Choose one of the supported tickers for this model."
    assert seeded_repo.get_unsupported_interest("GOTO")["count"] == 1
