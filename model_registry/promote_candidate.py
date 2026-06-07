"""Promote an approved MLflow experiment run into the customer-facing catalogue."""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import get_settings
from ml.backtesting.realistic import load_pooled_model
from model_registry.catalogue_sync import CatalogueSyncService
from model_registry.mlflow_client import MLflowMetadataClient
from model_registry.mlflow_store import prepare_mlflow_tracking_uri
from storage.database import connect, initialize
from storage.repositories import Repository

REQUIRED_METRICS = {
    "directional_accuracy",
    "cumulative_return_after_cost",
    "max_drawdown",
    "test_rows",
    "ticker_count",
}
REQUIRED_PARAMS = {
    "evaluation_period_start",
    "evaluation_period_end",
    "transaction_cost",
    "atr_window",
    "barrier_atr_multiple",
    "vertical_barrier_sessions",
}
MODEL_ARTIFACT_PATH = "model/model.joblib"


class PromotionError(ValueError):
    """Raised when a candidate run is not eligible for catalogue promotion."""


@dataclass(frozen=True)
class PromotionRequest:
    run_id: str
    model_id: str
    model_version: str
    model_name: str
    supported_universe_id: str
    approved: bool
    public_demo_eligible: bool = False
    sqlite_path: Path | None = None
    tracking_uri: str | None = None
    artifact_path: Path | None = None
    description: str | None = None


@dataclass(frozen=True)
class PromotionResult:
    model_id: str
    model_version: str
    run_id: str
    artifact_uri: str
    supported_tickers: int
    registry_sync_status: str


def promote_candidate(request: PromotionRequest) -> PromotionResult:
    """Promote a manually approved MLflow run into SQLite and verify sync."""
    if not request.approved:
        raise PromotionError("Manual approval is required before a model can be promoted.")

    tracking_uri = prepare_mlflow_tracking_uri(request.tracking_uri or get_settings().mlflow_tracking_uri)
    sqlite_path = request.sqlite_path or get_settings().sqlite_path
    run = _load_mlflow_run(tracking_uri, request.run_id)
    _validate_run(run)

    artifact_path = request.artifact_path or Path(".local/model_artifacts") / request.model_id / request.model_version / "model.joblib"
    artifact_uri = f"file:{artifact_path}"
    _download_artifact(tracking_uri, request.run_id, artifact_path)
    artifact = load_pooled_model(artifact_path)
    if not artifact.trained_tickers:
        raise PromotionError("Candidate artifact has no trained tickers.")

    _stamp_mlflow_approval_tags(
        tracking_uri=tracking_uri,
        run_id=request.run_id,
        request=request,
        artifact_uri=artifact_uri,
    )

    conn = connect(sqlite_path)
    initialize(conn)
    repo = Repository(conn)
    try:
        _upsert_promoted_records(repo, request, run.data.params, run.data.metrics, artifact, artifact_uri)
        decision = CatalogueSyncService(repo, MLflowMetadataClient(tracking_uri=tracking_uri)).sync_model(
            request.model_id,
            request.model_version,
        )
        if not decision.prediction_allowed:
            conn.rollback()
            raise PromotionError(decision.user_message or "Promoted model did not pass registry synchronization.")
        conn.commit()
    finally:
        conn.close()

    return PromotionResult(
        model_id=request.model_id,
        model_version=request.model_version,
        run_id=request.run_id,
        artifact_uri=artifact_uri,
        supported_tickers=len(artifact.trained_tickers),
        registry_sync_status="current",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Promote a manually approved MLflow candidate model into Nusantara Alpha.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--model-version", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--supported-universe-id", required=True)
    parser.add_argument("--approve", action="store_true", help="Required manual approval gate.")
    parser.add_argument("--public-demo-eligible", action="store_true")
    parser.add_argument("--sqlite-path", type=Path, default=None)
    parser.add_argument("--tracking-uri", default=None)
    parser.add_argument("--artifact-path", type=Path, default=None)
    parser.add_argument("--description", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = promote_candidate(
        PromotionRequest(
            run_id=args.run_id,
            model_id=args.model_id,
            model_version=args.model_version,
            model_name=args.model_name,
            supported_universe_id=args.supported_universe_id,
            approved=args.approve,
            public_demo_eligible=args.public_demo_eligible,
            sqlite_path=args.sqlite_path,
            tracking_uri=args.tracking_uri,
            artifact_path=args.artifact_path,
            description=args.description,
        )
    )
    print(
        "Promoted "
        f"{result.model_id} {result.model_version} from MLflow run {result.run_id}; "
        f"{result.supported_tickers} tickers; artifact {result.artifact_uri}; "
        f"registry sync {result.registry_sync_status}."
    )
    return 0


def _load_mlflow_run(tracking_uri: str, run_id: str):
    try:
        import mlflow  # type: ignore
        from mlflow.tracking import MlflowClient  # type: ignore
    except Exception as exc:
        raise PromotionError("MLflow is required to promote a candidate model.") from exc
    mlflow.set_tracking_uri(tracking_uri)
    try:
        return MlflowClient().get_run(run_id)
    except Exception as exc:
        raise PromotionError(f"MLflow run not found: {run_id}") from exc


def _validate_run(run) -> None:
    missing_metrics = sorted(REQUIRED_METRICS.difference(run.data.metrics))
    missing_params = sorted(REQUIRED_PARAMS.difference(run.data.params))
    if missing_metrics:
        raise PromotionError(f"Candidate run is missing required metrics: {', '.join(missing_metrics)}")
    if missing_params:
        raise PromotionError(f"Candidate run is missing required params: {', '.join(missing_params)}")


def _download_artifact(tracking_uri: str, run_id: str, destination: Path) -> None:
    import mlflow  # type: ignore
    from mlflow.tracking import MlflowClient  # type: ignore

    mlflow.set_tracking_uri(tracking_uri)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        downloaded = Path(MlflowClient().download_artifacts(run_id, MODEL_ARTIFACT_PATH))
    except Exception as exc:
        raise PromotionError(f"Candidate run is missing required model artifact: {MODEL_ARTIFACT_PATH}") from exc
    shutil.copy2(downloaded, destination)


def _stamp_mlflow_approval_tags(
    tracking_uri: str,
    run_id: str,
    request: PromotionRequest,
    artifact_uri: str,
) -> None:
    import mlflow  # type: ignore
    from mlflow.tracking import MlflowClient  # type: ignore

    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()
    tags = {
        "workflow": "promoted_model",
        "model_id": request.model_id,
        "model_version": request.model_version,
        "model_name": request.model_name,
        "approval_status": "approved",
        "artifact_uri": artifact_uri,
        "supported_universe_id": request.supported_universe_id,
        "public_demo_eligible": str(request.public_demo_eligible).lower(),
        "registry_revision": request.run_id,
    }
    for key, value in tags.items():
        client.set_tag(run_id, key, value)


def _upsert_promoted_records(
    repo: Repository,
    request: PromotionRequest,
    params: dict[str, str],
    metrics: dict[str, float],
    artifact,
    artifact_uri: str,
) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    now_iso = now.isoformat()
    data_as_of = f"{artifact.data_as_of_date}T00:00:00+00:00"
    limitations = [
        "Historical results may not generalize to future market sessions.",
        "This model is approved for educational research signals only, not trading instructions.",
    ]
    repo.upsert_model(
        {
            "model_id": request.model_id,
            "model_version": request.model_version,
            "model_name": request.model_name,
            "description": request.description or "Manually approved MLflow experiment promoted for educational IDX model signals.",
            "status": "approved",
            "model_origin": "real",
            "public_demo_eligible": request.public_demo_eligible,
            "supported_universe_id": request.supported_universe_id,
            "evaluation_period_start": params["evaluation_period_start"],
            "evaluation_period_end": params["evaluation_period_end"],
            "evidence_available": True,
            "evidence_load_status": "loaded",
            "limitations": limitations,
            "mlflow_run_id": request.run_id,
            "mlflow_model_uri": artifact_uri,
            "sqlite_catalogue_revision": f"catalogue-{now.strftime('%Y%m%d%H%M%S')}",
            "mlflow_registry_revision": request.run_id,
            "registry_sync_status": "current",
            "registry_conflict_reason": None,
        }
    )
    for ticker in artifact.trained_tickers:
        existing = repo.get_stock(request.supported_universe_id, ticker)
        repo.upsert_stock(
            {
                "ticker": ticker,
                "name": existing["name"] if existing else ticker,
                "exchange": existing["exchange"] if existing else "IDX",
                "universe_id": request.supported_universe_id,
                "support_status": "supported",
                "unavailable_reason": None,
                "data_as_of": data_as_of,
                "freshness_status": "fresh",
                "market_data_flags": existing["market_data_flags"] if existing else [],
            }
        )
        repo.upsert_data_availability(
            {
                "model_id": request.model_id,
                "ticker": ticker,
                "required_period_start": params["evaluation_period_start"],
                "required_period_end": artifact.data_as_of_date,
                "data_as_of": data_as_of,
                "feature_generation_timestamp": data_as_of,
                "freshness_status": "fresh",
                "chronology_status": "valid",
                "quality_flags": [],
                "blocking_reason": None,
            }
        )
    repo.upsert_evidence(
        {
            "evidence_id": f"evidence-{request.model_id}-{request.model_version}",
            "model_id": request.model_id,
            "model_version": request.model_version,
            "evidence_type": "backtest",
            "evaluation_period_start": params["evaluation_period_start"],
            "evaluation_period_end": params["evaluation_period_end"],
            "key_metrics": _evidence_metrics(metrics),
            "performance_summary": "Historical backtest evidence from the promoted MLflow experiment.",
            "supported_universe": artifact.trained_tickers,
            "limitations": limitations,
            "data_quality_notes": [
                f"Promoted from MLflow run {request.run_id}.",
                f"Model artifact data as of {artifact.data_as_of_date}.",
            ],
            "historical_performance_caveat": "Historical performance may not generalize to future market sessions.",
            "evidence_status": "complete",
            "evidence_load_status": "loaded",
            "evidence_as_of": now_iso,
            "data_source_mode": "approved",
            "barrier_config": {
                **artifact.barrier_config,
                "transaction_cost": params.get("transaction_cost"),
            },
            "paper_trading_summary": "No paper-trading evidence is available for this promoted run unless logged separately.",
        }
    )


def _evidence_metrics(metrics: dict[str, float]) -> list[dict[str, str]]:
    mapping = [
        ("directional_accuracy", "Triple-barrier accuracy", "Held-out upward, downward, or neutral labels classified correctly."),
        ("cumulative_return_after_cost", "Cumulative simulated return after cost", "Long-only educational simulation for upward signals after cost."),
        ("max_drawdown", "Maximum drawdown", "Largest historical simulated drawdown in the held-out period."),
        ("signal_coverage", "Signal coverage", "Share of held-out rows where the model produced a non-neutral signal."),
        ("ticker_count", "Coverage", "Number of tickers included in the promoted experiment."),
    ]
    output = []
    for key, name, interpretation in mapping:
        if key not in metrics:
            continue
        value = metrics[key]
        formatted = f"{int(value)} IDX stocks" if key == "ticker_count" else f"{value:.2%}"
        output.append({"name": name, "value": formatted, "interpretation": interpretation})
    return output


if __name__ == "__main__":
    raise SystemExit(main())
