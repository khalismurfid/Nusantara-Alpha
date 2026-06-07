"""Reusable local experiment helpers for the IDX logistic baseline."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.backtesting.realistic import (
    ATR_WINDOW,
    BARRIER_ATR_MULTIPLE,
    VERTICAL_BARRIER_SESSIONS,
    build_supervised_frame,
    design_matrix,
    signal_from_target,
)
from storage.database import connect
from storage.repositories import Repository


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for local chronological baseline experiments."""

    transaction_cost: float = 0.0025
    min_history: int = 8
    train_ratio: float = 0.7
    atr_window: int = ATR_WINDOW
    barrier_atr_multiple: float = BARRIER_ATR_MULTIPLE
    vertical_barrier_sessions: int = VERTICAL_BARRIER_SESSIONS
    random_state: int = 42


@dataclass(frozen=True)
class BaselineExperimentResult:
    """Tabular outputs from a local baseline experiment."""

    summary: dict[str, Any]
    per_stock: pd.DataFrame
    predictions: pd.DataFrame
    daily_returns: pd.DataFrame
    supervised: pd.DataFrame
    train_cutoff: pd.Timestamp
    config: ExperimentConfig


def load_price_rows_from_sqlite(
    db_path: str | Path = ".local/nusantara_alpha.sqlite3",
    tickers: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    """Load approved OHLCV rows from the local SQLite market-price cache."""
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"Local market database not found: {path}")
    conn = connect(path)
    try:
        repo = Repository(conn)
        return repo.list_market_prices(tickers=tickers, start_date=start_date, end_date=end_date)
    finally:
        conn.close()


def run_baseline_logistic_experiment(
    price_rows: list[dict[str, Any]],
    config: ExperimentConfig | None = None,
) -> BaselineExperimentResult:
    """Train and evaluate the pooled logistic baseline with a chronological split."""
    config = config or ExperimentConfig()
    supervised = build_supervised_frame(
        price_rows,
        min_history=config.min_history,
        atr_window=config.atr_window,
        barrier_atr_multiple=config.barrier_atr_multiple,
        vertical_barrier_sessions=config.vertical_barrier_sessions,
    )
    train, test, cutoff = chronological_train_test_split(supervised, train_ratio=config.train_ratio)
    scored = score_test_frame(train, test, config)
    scored = add_long_only_simulated_returns(scored, transaction_cost=config.transaction_cost)
    daily = aggregate_daily_returns(scored)
    summary = summarize_predictions(scored, daily, config)
    stock_metrics = per_stock_metrics(scored)
    return BaselineExperimentResult(
        summary=summary,
        per_stock=stock_metrics,
        predictions=scored,
        daily_returns=daily,
        supervised=supervised,
        train_cutoff=cutoff,
        config=config,
    )


def chronological_train_test_split(
    supervised: pd.DataFrame,
    train_ratio: float = 0.7,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    """Split supervised rows by date so test observations occur after training."""
    if supervised.empty:
        raise ValueError("No supervised rows are available for chronological splitting.")
    frame = supervised.copy()
    frame["price_date"] = pd.to_datetime(frame["price_date"])
    dates = sorted(frame["price_date"].dropna().unique())
    if len(dates) < 8:
        raise ValueError("Backtest needs at least eight feature dates.")
    split_index = max(1, min(len(dates) - 1, int(len(dates) * train_ratio)))
    cutoff = pd.Timestamp(dates[split_index])
    train = frame[frame["price_date"] < cutoff].copy()
    test = frame[frame["price_date"] >= cutoff].copy()
    if train.empty or test.empty:
        raise ValueError("Chronological split produced an empty train or test set.")
    if train["target"].nunique() < 2:
        raise ValueError("Training data needs at least two triple-barrier outcome classes.")
    return train, test, cutoff


def score_test_frame(train: pd.DataFrame, test: pd.DataFrame, config: ExperimentConfig) -> pd.DataFrame:
    """Fit the baseline logistic model on train rows and score held-out rows."""
    x_train, columns = design_matrix(train)
    x_test, _ = design_matrix(test, columns)
    pipeline = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=config.random_state,
                ),
            ),
        ]
    )
    pipeline.fit(x_train, train["target"].astype(int))
    probabilities = pipeline.predict_proba(x_test)
    classes = [int(value) for value in pipeline.named_steps["model"].classes_]
    scored = test.copy()
    for target, column in [(-1, "down_probability"), (0, "neutral_probability"), (1, "up_probability")]:
        scored[column] = probabilities[:, classes.index(target)] if target in classes else 0.0
    scored["predicted_target"] = [classes[int(row.argmax())] for row in probabilities]
    scored["model_score"] = probabilities.max(axis=1)
    scored["model_signal"] = scored["predicted_target"].map(signal_from_target)
    return scored


def add_long_only_simulated_returns(
    predictions: pd.DataFrame,
    transaction_cost: float = 0.0025,
) -> pd.DataFrame:
    """Add educational long-only simulated returns for upward model signals."""
    frame = predictions.copy()
    is_up_signal = frame["model_signal"] == "up"
    frame["simulated_return_after_cost"] = 0.0
    frame.loc[is_up_signal, "simulated_return_after_cost"] = (
        frame.loc[is_up_signal, "target_barrier_return"].astype(float) - transaction_cost
    )
    return frame


def aggregate_daily_returns(predictions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate simulated returns into an equity and drawdown curve."""
    if predictions.empty:
        return pd.DataFrame(
            columns=["price_date", "daily_simulated_return", "equity_curve", "drawdown"]
        )
    daily = (
        predictions.groupby("price_date", as_index=False)["simulated_return_after_cost"]
        .mean()
        .rename(columns={"simulated_return_after_cost": "daily_simulated_return"})
        .sort_values("price_date")
    )
    daily["equity_curve"] = (1 + daily["daily_simulated_return"]).cumprod()
    daily["drawdown"] = daily["equity_curve"] / daily["equity_curve"].cummax() - 1
    return daily


def summarize_predictions(
    predictions: pd.DataFrame,
    daily_returns: pd.DataFrame,
    config: ExperimentConfig,
) -> dict[str, Any]:
    """Build aggregate classification and economic metrics for the experiment."""
    up = predictions[predictions["model_signal"] == "up"]
    neutral = predictions[predictions["model_signal"] == "neutral"]
    volatility = _optional_float(daily_returns["daily_simulated_return"].std()) if len(daily_returns) > 1 else 0.0
    average_daily_return = _safe_float(daily_returns["daily_simulated_return"].mean())
    return {
        "evaluation_period_start": _date_string(predictions["price_date"].min()),
        "evaluation_period_end": _date_string(predictions["price_date"].max()),
        "test_rows": int(len(predictions)),
        "ticker_count": int(predictions["ticker"].nunique()),
        "directional_accuracy": _safe_float((predictions["predicted_target"] == predictions["target"]).mean()),
        "upward_precision": _optional_float((up["target"] == 1).mean()) if not up.empty else None,
        "neutral_share": _safe_float(len(neutral) / len(predictions)) if len(predictions) else 0.0,
        "signal_coverage": _safe_float((predictions["model_signal"] != "neutral").mean()),
        "average_daily_simulated_return": average_daily_return,
        "cumulative_return_after_cost": _last_equity_return(daily_returns),
        "max_drawdown": _safe_float(daily_returns["drawdown"].min()) if not daily_returns.empty else 0.0,
        "volatility": volatility,
        "sharpe_like": _sharpe_like(average_daily_return, volatility),
        "up_signal_win_rate": _optional_float((up["simulated_return_after_cost"] > 0).mean()) if not up.empty else None,
        "up_signal_count": int(len(up)),
        "transaction_cost": config.transaction_cost,
        "barrier_method": "atr_triple_barrier",
        "atr_window": config.atr_window,
        "barrier_atr_multiple": config.barrier_atr_multiple,
        "vertical_barrier_sessions": config.vertical_barrier_sessions,
        "ambiguous_same_bar_policy": "neutral",
    }


def per_stock_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    """Calculate per-stock classification and simulated economic metrics."""
    rows = []
    for ticker, group in predictions.groupby("ticker", sort=True):
        up = group[group["model_signal"] == "up"]
        neutral = group[group["model_signal"] == "neutral"]
        down = group[group["model_signal"] == "down"]
        daily = aggregate_daily_returns(group)
        volatility = _optional_float(daily["daily_simulated_return"].std()) if len(daily) > 1 else 0.0
        average_daily_return = _safe_float(daily["daily_simulated_return"].mean())
        rows.append(
            {
                "ticker": ticker,
                "test_rows": int(len(group)),
                "directional_accuracy": _safe_float((group["predicted_target"] == group["target"]).mean()),
                "upward_precision": _optional_float((up["target"] == 1).mean()) if not up.empty else None,
                "neutral_share": _safe_float(len(neutral) / len(group)) if len(group) else 0.0,
                "signal_coverage": _safe_float((group["model_signal"] != "neutral").mean()),
                "up_signal_count": int(len(up)),
                "neutral_signal_count": int(len(neutral)),
                "down_signal_count": int(len(down)),
                "average_daily_simulated_return": average_daily_return,
                "cumulative_return_after_cost": _last_equity_return(daily),
                "max_drawdown": _safe_float(daily["drawdown"].min()) if not daily.empty else 0.0,
                "volatility": volatility,
                "sharpe_like": _sharpe_like(average_daily_return, volatility),
                "up_signal_win_rate": _optional_float((up["simulated_return_after_cost"] > 0).mean()) if not up.empty else None,
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("cumulative_return_after_cost", ascending=False).reset_index(drop=True)


def _last_equity_return(daily_returns: pd.DataFrame) -> float:
    if daily_returns.empty:
        return 0.0
    return _safe_float(daily_returns["equity_curve"].iloc[-1] - 1)


def _sharpe_like(average_daily_return: float, volatility: float | None) -> float | None:
    if volatility is None or volatility <= 0:
        return None
    return _safe_float((average_daily_return / volatility) * sqrt(252))


def _safe_float(value: Any) -> float:
    if pd.isna(value):
        return 0.0
    return float(value)


def _optional_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def _date_string(value: Any) -> str | None:
    if pd.isna(value):
        return None
    return pd.Timestamp(value).date().isoformat()
