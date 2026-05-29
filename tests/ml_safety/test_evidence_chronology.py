from datetime import datetime, timezone

from ml.validation.chronology import validate_prediction_timestamps


def test_evidence_data_timestamp_cannot_be_after_prediction_timestamp():
    data_as_of = datetime(2026, 6, 1, tzinfo=timezone.utc)
    prediction_ts = datetime(2026, 5, 29, tzinfo=timezone.utc)
    result = validate_prediction_timestamps(data_as_of, prediction_ts, prediction_ts)
    assert not result.valid
    assert result.reason == "data_as_of_after_prediction"

