"""Chronological integrity and leakage-prevention validators."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChronologyResult:
    valid: bool
    reason: str | None = None


def parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_prediction_timestamps(data_as_of: str | datetime | None, feature_generation_timestamp: str | datetime | None, prediction_timestamp: str | datetime | None) -> ChronologyResult:
    data_ts = parse_datetime(data_as_of)
    feature_ts = parse_datetime(feature_generation_timestamp)
    prediction_ts = parse_datetime(prediction_timestamp)
    if prediction_ts is None:
        return ChronologyResult(False, "missing_prediction_timestamp")
    if data_ts is None:
        return ChronologyResult(False, "missing_data_as_of_timestamp")
    if feature_ts is None:
        return ChronologyResult(False, "missing_feature_timestamp")
    if data_ts > prediction_ts:
        return ChronologyResult(False, "data_as_of_after_prediction")
    if feature_ts > prediction_ts:
        return ChronologyResult(False, "feature_timestamp_after_prediction")
    return ChronologyResult(True)


def validate_time_ordered_split(train_end: str | datetime, validation_start: str | datetime, validation_end: str | datetime | None = None, test_start: str | datetime | None = None) -> ChronologyResult:
    train_end_dt = parse_datetime(train_end)
    validation_start_dt = parse_datetime(validation_start)
    if train_end_dt is None or validation_start_dt is None:
        return ChronologyResult(False, "missing_split_timestamp")
    if train_end_dt >= validation_start_dt:
        return ChronologyResult(False, "training_overlaps_validation")
    if validation_end is not None and test_start is not None:
        validation_end_dt = parse_datetime(validation_end)
        test_start_dt = parse_datetime(test_start)
        if validation_end_dt is None or test_start_dt is None:
            return ChronologyResult(False, "missing_split_timestamp")
        if validation_end_dt >= test_start_dt:
            return ChronologyResult(False, "validation_overlaps_test")
    return ChronologyResult(True)


def assert_no_future_information(feature_max_timestamp: str | datetime, prediction_timestamp: str | datetime) -> None:
    feature_ts = parse_datetime(feature_max_timestamp)
    prediction_ts = parse_datetime(prediction_timestamp)
    if feature_ts is None or prediction_ts is None:
        raise ValueError("Missing timestamp for future-information validation.")
    if feature_ts > prediction_ts:
        raise ValueError("Future information cannot be used for this prediction.")

