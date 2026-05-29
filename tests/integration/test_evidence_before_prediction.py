import pytest

from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService


@pytest.mark.parametrize(
    "load_status,expected_reason",
    [
        ("missing", "missing_required_evidence"),
        ("stale", "stale_required_evidence"),
        ("unavailable", "unavailable_required_evidence"),
        ("not_loaded", "evidence_not_loaded"),
    ],
)
def test_prediction_blocks_when_required_evidence_not_loaded(seeded_repo, load_status, expected_reason):
    seeded_repo.conn.execute(
        "UPDATE model_evidence SET evidence_load_status=? WHERE model_id='idx-direction-baseline'",
        (load_status,),
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
    assert response["predictions"] == []
    assert response["blocked"][0]["reason"] == expected_reason

