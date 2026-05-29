from datetime import datetime, timedelta, timezone

from ml.validation.chronology import validate_prediction_timestamps


def test_missing_feature_timestamp_is_invalid():
    now = datetime.now(timezone.utc)
    result = validate_prediction_timestamps(now, None, now)
    assert not result.valid
    assert result.reason == "missing_feature_timestamp"


def test_future_feature_timestamp_is_invalid():
    now = datetime.now(timezone.utc)
    result = validate_prediction_timestamps(now, now + timedelta(minutes=1), now)
    assert not result.valid
    assert result.reason == "feature_timestamp_after_prediction"

