from app_streamlit.app import (
    _format_ranking_row,
    evidence_is_loaded,
    prediction_cache_key,
    prediction_is_ready,
    selected_ticker_from_stock,
    split_stock_availability,
    stock_display_name,
    supported_stock_options,
)
from tests.unit.ui_fixtures import evidence_response, stock_response


def test_prediction_ready_after_model_loaded_evidence_and_supported_ticker():
    model = {"model_id": "idx-direction-baseline", "model_version": "2026.05"}

    assert prediction_is_ready(model, evidence_response(), ["BBCA"])


def test_prediction_not_ready_without_loaded_evidence_or_ticker():
    model = {"model_id": "idx-direction-baseline", "model_version": "2026.05"}

    assert not prediction_is_ready(model, evidence_response(evidence_load_status="stale"), ["BBCA"])
    assert not prediction_is_ready(model, evidence_response(), [])
    assert not prediction_is_ready(None, evidence_response(), ["BBCA"])


def test_supported_stock_helpers_separate_unavailable_tickers():
    supported = stock_response(ticker="BBCA")
    unavailable = stock_response(
        ticker="GOTO",
        support_status="unsupported",
        unavailable_reason="This model has not been reviewed for GOTO yet.",
    )

    supported_stocks, unavailable_stocks = split_stock_availability([supported, unavailable])

    assert evidence_is_loaded(evidence_response())
    assert supported_stock_options([supported, unavailable]) == ["BBCA"]
    assert supported_stocks == [supported]
    assert unavailable_stocks == [unavailable]


def test_stock_selector_helpers_keep_prediction_single_stock():
    stock = stock_response(ticker="BBCA", name="Bank Central Asia Tbk")

    assert stock_display_name(stock) == "BBCA - Bank Central Asia Tbk"
    assert selected_ticker_from_stock(stock) == ["BBCA"]
    assert selected_ticker_from_stock(None) == []


def test_prediction_cache_key_tracks_model_tickers_and_evidence():
    model = {"model_id": "idx-direction-baseline", "model_version": "2026.05"}
    evidence = evidence_response()

    assert prediction_cache_key(model, evidence, ["BBCA"]) == (
        "idx-direction-baseline",
        "2026.05",
        ("BBCA",),
        "evidence-idx-direction-baseline-2026.05",
        "2026-05-28T12:00:00+07:00",
    )


def test_ranking_row_uses_readable_signal_and_percent_score():
    row = _format_ranking_row(
        {
            "rank": 38,
            "ticker": "BBCA",
            "name": "Bank Central Asia Tbk",
            "model_signal": "up",
            "confidence_category": "Low",
            "ranking_score": 0.4197,
        },
        {"BBCA"},
    )

    assert row["Signal"] == "UP - leans toward the upward barrier"
    assert row["Upside score"] == 42
    assert row["Selected"] == "Selected stock"
