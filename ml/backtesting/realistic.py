"""Triple-barrier logistic baseline for pooled IDX model signals."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
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

ATR_WINDOW = 20
BARRIER_ATR_MULTIPLE = 1.0
VERTICAL_BARRIER_SESSIONS = 5
TARGET_TO_SIGNAL = {-1: "down", 0: "neutral", 1: "up"}


@dataclass(frozen=True)
class PooledLogisticSignalModel:
    pipeline: Pipeline
    feature_columns: list[str]
    trained_tickers: list[str]
    data_as_of_date: str
    training_rows: int
    latest_features: pd.DataFrame
    barrier_config: dict[str, Any]


def save_pooled_model(model: PooledLogisticSignalModel, path: str | Path) -> None:
    artifact_path = Path(path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifact_path)


def load_pooled_model(path: str | Path) -> PooledLogisticSignalModel:
    model = joblib.load(Path(path))
    if not isinstance(model, PooledLogisticSignalModel):
        raise ValueError("Artifact does not contain a pooled logistic signal model.")
    return model


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
    features[FEATURE_COLUMNS] = features[FEATURE_COLUMNS].replace([float("inf"), float("-inf")], pd.NA)
    return features.dropna(subset=FEATURE_COLUMNS)


def build_triple_barrier_events(
    price_rows: list[dict[str, Any]],
    atr_window: int = ATR_WINDOW,
    barrier_atr_multiple: float = BARRIER_ATR_MULTIPLE,
    vertical_barrier_sessions: int = VERTICAL_BARRIER_SESSIONS,
) -> pd.DataFrame:
    raw = prices_to_frame(price_rows)
    target_frames = []
    for _, group in raw.groupby("ticker", sort=True):
        ordered = group.sort_values("price_date").reset_index(drop=True)
        previous_close = ordered["close"].shift(1)
        ordered["true_range"] = pd.concat(
            [
                ordered["high"] - ordered["low"],
                (ordered["high"] - previous_close).abs(),
                (ordered["low"] - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        ordered["atr"] = ordered["true_range"].rolling(atr_window).mean()
        rows = []
        for index in range(len(ordered) - 1):
            atr = ordered.iloc[index]["atr"]
            if pd.isna(atr) or atr <= 0:
                continue
            entry_index = index + 1
            window = ordered.iloc[entry_index : entry_index + vertical_barrier_sessions]
            if window.empty:
                continue
            entry = ordered.iloc[entry_index]
            entry_price = float(entry["open"])
            barrier_width = float(atr) * barrier_atr_multiple
            upper_barrier = entry_price + barrier_width
            lower_barrier = entry_price - barrier_width
            event_label = 0
            event_return = float(window.iloc[-1]["close"] / entry_price - 1)
            barrier_hit = "vertical"
            exit_date = window.iloc[-1]["price_date"]
            for _, candidate in window.iterrows():
                upper_hit = float(candidate["high"]) >= upper_barrier
                lower_hit = float(candidate["low"]) <= lower_barrier
                if upper_hit and lower_hit:
                    event_label = 0
                    event_return = float(candidate["close"] / entry_price - 1)
                    barrier_hit = "ambiguous"
                    exit_date = candidate["price_date"]
                    break
                if upper_hit:
                    event_label = 1
                    event_return = float(upper_barrier / entry_price - 1)
                    barrier_hit = "profit_take"
                    exit_date = candidate["price_date"]
                    break
                if lower_hit:
                    event_label = -1
                    event_return = float(lower_barrier / entry_price - 1)
                    barrier_hit = "stop_loss"
                    exit_date = candidate["price_date"]
                    break
            rows.append(
                {
                    "ticker": ordered.iloc[index]["ticker"],
                    "price_date": ordered.iloc[index]["price_date"],
                    "entry_date": entry["price_date"],
                    "entry_price": entry_price,
                    "atr_window": atr_window,
                    "atr_value": float(atr),
                    "barrier_atr_multiple": barrier_atr_multiple,
                    "upper_barrier": upper_barrier,
                    "lower_barrier": lower_barrier,
                    "upper_barrier_return": float(upper_barrier / entry_price - 1),
                    "lower_barrier_return": float(lower_barrier / entry_price - 1),
                    "vertical_barrier_sessions": vertical_barrier_sessions,
                    "barrier_end_date": exit_date,
                    "barrier_hit": barrier_hit,
                    "target_barrier_return": event_return,
                    "target": event_label,
                }
            )
        if rows:
            target_frames.append(pd.DataFrame(rows))
    if not target_frames:
        return pd.DataFrame(
            columns=[
                "ticker",
                "price_date",
                "entry_date",
                "entry_price",
                "atr_window",
                "atr_value",
                "barrier_atr_multiple",
                "upper_barrier",
                "lower_barrier",
                "upper_barrier_return",
                "lower_barrier_return",
                "vertical_barrier_sessions",
                "barrier_end_date",
                "barrier_hit",
                "target_barrier_return",
                "target",
            ]
        )
    return pd.concat(target_frames, ignore_index=True)


def build_supervised_frame(
    price_rows: list[dict[str, Any]],
    min_history: int = 8,
    atr_window: int = ATR_WINDOW,
    barrier_atr_multiple: float = BARRIER_ATR_MULTIPLE,
    vertical_barrier_sessions: int = VERTICAL_BARRIER_SESSIONS,
) -> pd.DataFrame:
    features = build_feature_frame(price_rows, min_history=min_history)
    targets = build_triple_barrier_events(
        price_rows,
        atr_window=atr_window,
        barrier_atr_multiple=barrier_atr_multiple,
        vertical_barrier_sessions=vertical_barrier_sessions,
    )
    supervised = features.merge(targets, on=["ticker", "price_date"], how="left")
    return supervised.dropna(subset=["target_barrier_return", "target", *FEATURE_COLUMNS])


def design_matrix(frame: pd.DataFrame, feature_columns: list[str] | None = None) -> tuple[pd.DataFrame, list[str]]:
    numeric = frame[FEATURE_COLUMNS].copy()
    ticker_features = pd.get_dummies(frame["ticker"], prefix="ticker", dtype=float)
    matrix = pd.concat([numeric, ticker_features], axis=1)
    if feature_columns is None:
        feature_columns = list(matrix.columns)
    else:
        matrix = matrix.reindex(columns=feature_columns, fill_value=0.0)
    return matrix, list(feature_columns)


def fit_pooled_logistic_model(
    price_rows: list[dict[str, Any]],
    min_history: int = 8,
    atr_window: int = ATR_WINDOW,
    barrier_atr_multiple: float = BARRIER_ATR_MULTIPLE,
    vertical_barrier_sessions: int = VERTICAL_BARRIER_SESSIONS,
) -> PooledLogisticSignalModel:
    supervised = build_supervised_frame(
        price_rows,
        min_history=min_history,
        atr_window=atr_window,
        barrier_atr_multiple=barrier_atr_multiple,
        vertical_barrier_sessions=vertical_barrier_sessions,
    )
    if supervised.empty:
        raise ValueError("Not enough historical rows to train the pooled model.")
    if supervised["target"].nunique() < 2:
        raise ValueError("Training data needs at least two triple-barrier outcome classes.")
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
        barrier_config={
            "method": "atr_triple_barrier",
            "atr_window": atr_window,
            "profit_barrier": f"{barrier_atr_multiple:g}x {atr_window}-day ATR",
            "stop_barrier": f"{barrier_atr_multiple:g}x {atr_window}-day ATR",
            "barrier_atr_multiple": barrier_atr_multiple,
            "vertical_barrier_sessions": vertical_barrier_sessions,
            "ambiguous_same_bar_policy": "neutral",
        },
    )


def latest_feature_rows(price_rows: list[dict[str, Any]], feature_columns: list[str], min_history: int = 8) -> pd.DataFrame:
    features = build_feature_frame(price_rows, min_history=min_history)
    latest = features.sort_values("price_date").groupby("ticker", as_index=False).tail(1).copy()
    matrix, _ = design_matrix(latest, feature_columns)
    latest["model_score"] = 0.0
    latest.attrs["matrix"] = matrix
    return latest


def signal_from_target(target: int) -> str:
    return TARGET_TO_SIGNAL.get(int(target), "neutral")


def confidence_from_probability(probability: float) -> str:
    if probability >= 0.60:
        return "High"
    if probability >= 0.45:
        return "Medium"
    return "Low"


def predict_scores(model: PooledLogisticSignalModel) -> pd.DataFrame:
    latest = model.latest_features.copy()
    matrix = latest.attrs.get("matrix")
    if matrix is None:
        matrix, _ = design_matrix(latest, model.feature_columns)
    probabilities = model.pipeline.predict_proba(matrix)
    classes = [int(value) for value in model.pipeline.named_steps["model"].classes_]
    class_probabilities = {target: probabilities[:, classes.index(target)] if target in classes else 0.0 for target in [-1, 0, 1]}
    latest["down_probability"] = class_probabilities[-1]
    latest["neutral_probability"] = class_probabilities[0]
    latest["up_probability"] = class_probabilities[1]
    latest["predicted_target"] = [
        classes[int(row.argmax())]
        for row in probabilities
    ]
    latest["model_score"] = probabilities.max(axis=1)
    latest["ranking_score"] = latest["up_probability"]
    latest["model_signal"] = latest["predicted_target"].map(signal_from_target)
    latest["confidence_category"] = latest["model_score"].map(confidence_from_probability)
    latest = latest.sort_values("ranking_score", ascending=False).reset_index(drop=True)
    latest["rank"] = latest.index + 1
    return latest


def backtest_pooled_model(
    price_rows: list[dict[str, Any]],
    transaction_cost: float = 0.0025,
    min_history: int = 8,
    train_ratio: float = 0.7,
    atr_window: int = ATR_WINDOW,
    barrier_atr_multiple: float = BARRIER_ATR_MULTIPLE,
    vertical_barrier_sessions: int = VERTICAL_BARRIER_SESSIONS,
) -> dict[str, Any]:
    supervised = build_supervised_frame(
        price_rows,
        min_history=min_history,
        atr_window=atr_window,
        barrier_atr_multiple=barrier_atr_multiple,
        vertical_barrier_sessions=vertical_barrier_sessions,
    )
    dates = sorted(supervised["price_date"].unique())
    if len(dates) < 8:
        raise ValueError("Backtest needs at least eight feature dates.")
    split_index = max(1, min(len(dates) - 1, int(len(dates) * train_ratio)))
    cutoff = dates[split_index]
    train = supervised[supervised["price_date"] < cutoff].copy()
    test = supervised[supervised["price_date"] >= cutoff].copy()
    if train.empty or test.empty or train["target"].nunique() < 2:
        raise ValueError("Backtest split does not contain enough triple-barrier class variation.")
    x_train, columns = design_matrix(train)
    x_test, _ = design_matrix(test, columns)
    pipeline = Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]
    )
    pipeline.fit(x_train, train["target"].astype(int))
    probabilities = pipeline.predict_proba(x_test)
    classes = [int(value) for value in pipeline.named_steps["model"].classes_]
    class_probabilities = {target: probabilities[:, classes.index(target)] if target in classes else 0.0 for target in [-1, 0, 1]}
    test["down_probability"] = class_probabilities[-1]
    test["neutral_probability"] = class_probabilities[0]
    test["up_probability"] = class_probabilities[1]
    test["predicted_target"] = [classes[int(row.argmax())] for row in probabilities]
    test["model_score"] = probabilities.max(axis=1)
    test["model_signal"] = test["predicted_target"].map(signal_from_target)
    test["long_return_after_cost"] = test.apply(
        lambda row: row["target_barrier_return"] - transaction_cost if row["model_signal"] == "up" else 0.0,
        axis=1,
    )
    daily_returns = test.groupby("price_date")["long_return_after_cost"].mean()
    equity = (1 + daily_returns).cumprod()
    drawdown = equity / equity.cummax() - 1
    upward = test[test["model_signal"] == "up"]
    neutral = test[test["model_signal"] == "neutral"]
    return {
        "evaluation_period_start": str(test["price_date"].min().date()),
        "evaluation_period_end": str(test["price_date"].max().date()),
        "directional_accuracy": float((test["predicted_target"] == test["target"]).mean()),
        "upward_precision": float((upward["target"] == 1).mean()) if not upward.empty else None,
        "neutral_share": float(len(neutral) / len(test)) if len(test) else 0.0,
        "signal_coverage": float((test["model_signal"] != "neutral").mean()),
        "average_next_session_return_after_cost": float(test["long_return_after_cost"].mean()),
        "cumulative_return_after_cost": float(equity.iloc[-1] - 1) if not equity.empty else 0.0,
        "max_drawdown": float(drawdown.min()) if not drawdown.empty else 0.0,
        "test_rows": int(len(test)),
        "ticker_count": int(test["ticker"].nunique()),
        "transaction_cost": transaction_cost,
        "barrier_method": "atr_triple_barrier",
        "atr_window": atr_window,
        "barrier_atr_multiple": barrier_atr_multiple,
        "vertical_barrier_sessions": vertical_barrier_sessions,
        "ambiguous_same_bar_policy": "neutral",
    }
