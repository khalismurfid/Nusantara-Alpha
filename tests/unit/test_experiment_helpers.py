from ml.experiments.baseline import (
    ExperimentConfig,
    aggregate_daily_returns,
    chronological_train_test_split,
    per_stock_metrics,
    run_baseline_logistic_experiment,
)
from ml.backtesting.realistic import build_supervised_frame
from storage.seed_local_demo import _sample_market_prices


def test_baseline_experiment_returns_aggregate_and_per_stock_metrics():
    rows = _sample_market_prices(
        [
            ("BBCA", "Bank Central Asia Tbk"),
            ("TLKM", "Telkom Indonesia Tbk"),
            ("ASII", "Astra International Tbk"),
        ]
    )

    result = run_baseline_logistic_experiment(rows)

    assert result.summary["ticker_count"] == 3
    assert result.summary["test_rows"] == len(result.predictions)
    assert result.summary["transaction_cost"] == 0.0025
    assert set(result.per_stock["ticker"]) == {"BBCA", "TLKM", "ASII"}
    assert {
        "directional_accuracy",
        "upward_precision",
        "cumulative_return_after_cost",
        "max_drawdown",
        "sharpe_like",
        "up_signal_count",
        "neutral_signal_count",
        "down_signal_count",
    }.issubset(result.per_stock.columns)


def test_chronological_split_keeps_test_dates_after_training_dates():
    rows = _sample_market_prices([("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk")])
    supervised = build_supervised_frame(rows)

    train, test, cutoff = chronological_train_test_split(supervised)

    assert train["price_date"].max() < cutoff
    assert test["price_date"].min() >= cutoff


def test_daily_return_aggregation_builds_equity_and_drawdown_columns():
    rows = _sample_market_prices([("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk")])
    result = run_baseline_logistic_experiment(rows, ExperimentConfig(train_ratio=0.65))

    daily = aggregate_daily_returns(result.predictions)

    assert not daily.empty
    assert {"daily_simulated_return", "equity_curve", "drawdown"}.issubset(daily.columns)
    assert daily["equity_curve"].iloc[0] > 0


def test_per_stock_metrics_handles_empty_up_signal_cases():
    rows = _sample_market_prices([("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk")])
    result = run_baseline_logistic_experiment(rows)
    predictions = result.predictions.copy()
    predictions["model_signal"] = "neutral"
    predictions["simulated_return_after_cost"] = 0.0

    metrics = per_stock_metrics(predictions)

    assert set(metrics["up_signal_count"]) == {0}
    assert metrics["upward_precision"].isna().all()
    assert set(metrics["neutral_share"]) == {1.0}
