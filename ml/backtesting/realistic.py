"""Realistic next-session evaluation for pooled IDX model signals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "return_1d",
    "momentum_3",
    "momentum_5",
    "volatility_5",
    "volume_change_5",
    "range_pct",
    "market_return",
    "relative_return",
    "cross_section_rank",
]


@dataclass(frozen=True)
class PooledLogisticSignalModel:
    pipeline: Pipeline
    feature_columns: list[str]
    trained_tickers: list[str]
    data_as_of_date: str
    training_rows: int
    latest_features: pd.DataFrame


def prices_to_frame(price_rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(price_rows)
    if frame.empty:
        raise ValueError("No market prices are available for model training.")
    required = {"ticker", "price_date", "open", "high", "low", "close", "volume"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Market price rows are missing required fields: {sorted(missing)}")
    frame = frame.copy()
    frame["ticker"] = frame["ticker"].str.upper()
    frame["price_date"] = pd.to_datetime(frame["price_date"])
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values(["ticker", "price_date"]).dropna(subset=["open", "high", "low", "close"])


def build_feature_frame(price_rows: list[dict[str, Any]], min_history: int = 8) -> pd.DataFrame:
    frame = prices_to_frame(price_rows)
    feature_frames = []
    for _, group in frame.groupby("ticker", sort=True):
        group = group.sort_values("price_date").copy()
        group["return_1d"] = group["close"].pct_change()
        group["momentum_3"] = group["close"].pct_change(3)
        group["momentum_5"] = group["close"].pct_change(5)
        group["volatility_5"] = group["return_1d"].rolling(5).std()
        group["volume_change_5"] = group["volume"].pct_change(5)
        group["range_pct"] = (group["high"] - group["low"]) / group["close"]
        feature_frames.append(group.iloc[min_history:].copy())
    features = pd.concat(feature_frames, ignore_index=True)
    features["market_return"] = features.groupby("price_date")["return_1d"].transform("mean")
    features["relative_return"] = features["return_1d"] - features["market_return"]
    features["cross_section_rank"] = features.groupby("price_date")["return_1d"].rank(pct=True)
    return features.dropna(subset=FEATURE_COLUMNS)


def build_supervised_frame(price_rows: list[dict[str, Any]], min_history: int = 8) -> pd.DataFrame:
    features = build_feature_frame(price_rows, min_history=min_history)
    target_frames = []
    raw = prices_to_frame(price_rows)
    for _, group in raw.groupby("ticker", sort=True):
        group = group.sort_values("price_date").copy()
        group["next_open"] = group["open"].shift(-1)
        group["next_close"] = group["close"].shift(-1)
        group["target_next_return"] = (group["next_close"] / group["next_open"]) - 1
        target_frames.append(group[["ticker", "price_date", "target_next_return"]])
    targets = pd.concat(target_frames, ignore_index=True)
    supervised = features.merge(targets, on=["ticker", "price_date"], how="left")
    supervised["target"] = (supervised["target_next_return"] > 0).astype(int)
    return supervised.dropna(subset=["target_next_return", *FEATURE_COLUMNS])


def design_matrix(frame: pd.DataFrame, feature_columns: list[str] | None = None) -> tuple[pd.DataFrame, list[str]]:
    numeric = frame[FEATURE_COLUMNS].copy()
    ticker_features = pd.get_dummies(frame["ticker"], prefix="ticker", dtype=float)
    matrix = pd.concat([numeric, ticker_features], axis=1)
    if feature_columns is None:
        feature_columns = list(matrix.columns)
    else:
        matrix = matrix.reindex(columns=feature_columns, fill_value=0.0)
    return matrix, list(feature_columns)


def fit_pooled_logistic_model(price_rows: list[dict[str, Any]], min_history: int = 8) -> PooledLogisticSignalModel:
    supervised = build_supervised_frame(price_rows, min_history=min_history)
    if supervised.empty:
        raise ValueError("Not enough historical rows to train the pooled model.")
    if supervised["target"].nunique() < 2:
        raise ValueError("Training data needs both upward and non-upward next-session outcomes.")
    x_train, columns = design_matrix(supervised)
    y_train = supervised["target"].astype(int)
    pipeline = Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]
    )
    pipeline.fit(x_train, y_train)
    latest_features = latest_feature_rows(price_rows, columns, min_history=min_history)
    return PooledLogisticSignalModel(
        pipeline=pipeline,
        feature_columns=columns,
        trained_tickers=sorted(supervised["ticker"].unique()),
        data_as_of_date=str(supervised["price_date"].max().date()),
        training_rows=len(supervised),
        latest_features=latest_features,
    )


def latest_feature_rows(price_rows: list[dict[str, Any]], feature_columns: list[str], min_history: int = 8) -> pd.DataFrame:
    features = build_feature_frame(price_rows, min_history=min_history)
    latest = features.sort_values("price_date").groupby("ticker", as_index=False).tail(1).copy()
    matrix, _ = design_matrix(latest, feature_columns)
    latest["model_score"] = 0.0
    latest.attrs["matrix"] = matrix
    return latest


def signal_from_probability(probability: float) -> str:
    if probability >= 0.55:
        return "up"
    if probability <= 0.45:
        return "down"
    return "neutral"


def confidence_from_probability(probability: float) -> str:
    distance = abs(probability - 0.5)
    if distance >= 0.18:
        return "High"
    if distance >= 0.08:
        return "Medium"
    return "Low"


def predict_scores(model: PooledLogisticSignalModel) -> pd.DataFrame:
    latest = model.latest_features.copy()
    matrix = latest.attrs.get("matrix")
    if matrix is None:
        matrix, _ = design_matrix(latest, model.feature_columns)
    latest["model_score"] = model.pipeline.predict_proba(matrix)[:, 1]
    latest["model_signal"] = latest["model_score"].map(signal_from_probability)
    latest["confidence_category"] = latest["model_score"].map(confidence_from_probability)
    latest = latest.sort_values("model_score", ascending=False).reset_index(drop=True)
    latest["rank"] = latest.index + 1
    return latest


def backtest_pooled_model(
    price_rows: list[dict[str, Any]],
    transaction_cost: float = 0.0025,
    min_history: int = 8,
    train_ratio: float = 0.7,
) -> dict[str, Any]:
    supervised = build_supervised_frame(price_rows, min_history=min_history)
    dates = sorted(supervised["price_date"].unique())
    if len(dates) < 8:
        raise ValueError("Backtest needs at least eight feature dates.")
    split_index = max(1, min(len(dates) - 1, int(len(dates) * train_ratio)))
    cutoff = dates[split_index]
    train = supervised[supervised["price_date"] < cutoff].copy()
    test = supervised[supervised["price_date"] >= cutoff].copy()
    if train.empty or test.empty or train["target"].nunique() < 2:
        raise ValueError("Backtest split does not contain enough class variation.")
    x_train, columns = design_matrix(train)
    x_test, _ = design_matrix(test, columns)
    pipeline = Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]
    )
    pipeline.fit(x_train, train["target"].astype(int))
    test["model_score"] = pipeline.predict_proba(x_test)[:, 1]
    test["model_signal"] = test["model_score"].map(signal_from_probability)
    test["predicted_direction"] = (test["model_score"] >= 0.5).astype(int)
    test["long_return_after_cost"] = test.apply(
        lambda row: row["target_next_return"] - transaction_cost if row["model_signal"] == "up" else 0.0,
        axis=1,
    )
    daily_returns = test.groupby("price_date")["long_return_after_cost"].mean()
    equity = (1 + daily_returns).cumprod()
    drawdown = equity / equity.cummax() - 1
    upward = test[test["model_signal"] == "up"]
    return {
        "evaluation_period_start": str(test["price_date"].min().date()),
        "evaluation_period_end": str(test["price_date"].max().date()),
        "directional_accuracy": float((test["predicted_direction"] == test["target"]).mean()),
        "upward_precision": float(upward["target"].mean()) if not upward.empty else None,
        "signal_coverage": float((test["model_signal"] != "neutral").mean()),
        "average_next_session_return_after_cost": float(test["long_return_after_cost"].mean()),
        "cumulative_return_after_cost": float(equity.iloc[-1] - 1) if not equity.empty else 0.0,
        "max_drawdown": float(drawdown.min()) if not drawdown.empty else 0.0,
        "test_rows": int(len(test)),
        "ticker_count": int(test["ticker"].nunique()),
        "transaction_cost": transaction_cost,
    }
