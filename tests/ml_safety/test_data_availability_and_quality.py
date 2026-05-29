from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService


def test_stale_data_blocks_prediction(seeded_repo):
    seeded_repo.conn.execute(
        "UPDATE data_availability SET freshness_status='stale' WHERE ticker='BBCA'"
    )
    seeded_repo.conn.commit()
    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["BBCA"],
            target="next_market_session_direction",
        )
    )
    assert response["blocked"][0]["reason"] == "stale_data"


def test_invalid_chronology_blocks_prediction(seeded_repo):
    seeded_repo.conn.execute(
        "UPDATE data_availability SET chronology_status='invalid_future_information' WHERE ticker='TLKM'"
    )
    seeded_repo.conn.commit()
    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["TLKM"],
            target="next_market_session_direction",
        )
    )
    assert response["blocked"][0]["reason"] == "chronology_violation"

