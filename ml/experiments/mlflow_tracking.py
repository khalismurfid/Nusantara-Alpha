"""MLflow tracking helpers for local model experiments."""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from ml.backtesting.realistic import fit_pooled_logistic_model, save_pooled_model
from ml.experiments.baseline import BaselineExperimentResult
from model_registry.mlflow_store import DEFAULT_MLFLOW_TRACKING_URI, prepare_mlflow_tracking_uri


@dataclass(frozen=True)
class LoggedExperiment:
    run_id: str
    tracking_uri: str | None
    experiment_name: str
    artifact_path: str


def log_baseline_experiment_to_mlflow(
    result: BaselineExperimentResult,
    price_rows: list[dict[str, Any]],
    tracking_uri: str | None = DEFAULT_MLFLOW_TRACKING_URI,
    experiment_name: str = "nusantara-alpha-local-experiments",
    run_name: str | None = None,
    candidate_model_id: str | None = None,
    candidate_model_version: str | None = None,
) -> LoggedExperiment:
    """Log a baseline experiment run and deployable joblib artifact to MLflow."""
    import mlflow  # type: ignore

    tracking_uri = prepare_mlflow_tracking_uri(tracking_uri)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_name=run_name) as active_run:
        config = result.config
        mlflow.set_tags(
            {
                "workflow": "notebook_experiment",
                "model_family": "pooled_logistic_regression",
                "target_method": "atr_triple_barrier",
                "approval_status": "experimental",
                "public_demo_eligible": "false",
                "feature_columns": ",".join(_feature_columns_from_result(result)),
            }
        )
        if candidate_model_id:
            mlflow.set_tag("candidate_model_id", candidate_model_id)
        if candidate_model_version:
            mlflow.set_tag("candidate_model_version", candidate_model_version)
        mlflow.log_params(
            {
                "transaction_cost": config.transaction_cost,
                "train_ratio": config.train_ratio,
                "min_history": config.min_history,
                "atr_window": config.atr_window,
                "barrier_atr_multiple": config.barrier_atr_multiple,
                "vertical_barrier_sessions": config.vertical_barrier_sessions,
                "random_state": config.random_state,
                "evaluation_period_start": result.summary.get("evaluation_period_start"),
                "evaluation_period_end": result.summary.get("evaluation_period_end"),
                "ticker_count": result.summary.get("ticker_count"),
            }
        )
        mlflow.log_metrics(_numeric_metrics(result.summary))
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _write_csv_artifact(result.per_stock, tmp_path / "per_stock_metrics.csv")
            _write_csv_artifact(result.daily_returns, tmp_path / "daily_returns.csv")
            _write_csv_artifact(_compact_predictions(result.predictions), tmp_path / "heldout_predictions.csv")
            model = fit_pooled_logistic_model(
                price_rows,
                min_history=config.min_history,
                atr_window=config.atr_window,
                barrier_atr_multiple=config.barrier_atr_multiple,
                vertical_barrier_sessions=config.vertical_barrier_sessions,
            )
            model_path = tmp_path / "model.joblib"
            save_pooled_model(model, model_path)
            mlflow.log_artifact(str(model_path), artifact_path="model")
            mlflow.log_artifact(str(tmp_path / "per_stock_metrics.csv"), artifact_path="metrics")
            mlflow.log_artifact(str(tmp_path / "daily_returns.csv"), artifact_path="metrics")
            mlflow.log_artifact(str(tmp_path / "heldout_predictions.csv"), artifact_path="metrics")
        return LoggedExperiment(
            run_id=active_run.info.run_id,
            tracking_uri=tracking_uri,
            experiment_name=experiment_name,
            artifact_path="model/model.joblib",
        )


def _numeric_metrics(summary: dict[str, Any]) -> dict[str, float]:
    metrics = {}
    for key, value in summary.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)) and value is not None:
            metrics[key] = float(value)
    return metrics


def _write_csv_artifact(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False)


def _compact_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "ticker",
        "price_date",
        "target",
        "predicted_target",
        "model_signal",
        "model_score",
        "up_probability",
        "neutral_probability",
        "down_probability",
        "target_barrier_return",
        "simulated_return_after_cost",
    ]
    return predictions[[column for column in columns if column in predictions.columns]].copy()


def _feature_columns_from_result(result: BaselineExperimentResult) -> list[str]:
    return [
        column
        for column in result.supervised.columns
        if column
        in {
            "return_1d",
            "momentum_3",
            "momentum_5",
            "volatility_5",
            "volume_change_5",
            "range_pct",
            "market_return",
            "relative_return",
            "cross_section_rank",
        }
    ]
