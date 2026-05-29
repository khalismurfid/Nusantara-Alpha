from backend.schemas.contracts import PredictionRequest, PredictionOutput
from backend.services.prediction_service import PredictionService


def test_prediction_output_has_traceability_fields(seeded_repo):
    response = PredictionService(seeded_repo).request_prediction(
        PredictionRequest(
            model_id="idx-direction-baseline",
            model_version="2026.05",
            tickers=["TLKM"],
            target="next_market_session_direction",
        )
    )
    output = PredictionOutput.model_validate(response["predictions"][0])
    assert output.model_id == "idx-direction-baseline"
    assert output.model_version == "2026.05"
    assert output.data_as_of_timestamp <= output.prediction_timestamp
    assert output.feature_generation_timestamp <= output.prediction_timestamp
    assert output.evidence_reference
    assert output.evaluation_context
    assert output.disclaimer_version

