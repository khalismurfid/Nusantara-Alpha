"""MLflow metadata access with graceful fallback when MLflow is unavailable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from model_registry.mlflow_store import prepare_mlflow_tracking_uri, resolve_mlflow_tracking_uri


@dataclass(frozen=True)
class MLflowModelMetadata:
    model_id: str
    model_version: str
    approval_status: str
    artifact_uri: str | None
    supported_universe_id: str | None
    public_demo_eligible: bool
    registry_revision: str | None
    raw: dict[str, Any]


class MLflowMetadataClient:
    def __init__(self, tracking_uri: str | None = None, in_memory: dict[tuple[str, str], MLflowModelMetadata] | None = None):
        self.tracking_uri = resolve_mlflow_tracking_uri(tracking_uri)
        self.in_memory = in_memory or {}

    def get_model_metadata(self, model_id: str, model_version: str) -> MLflowModelMetadata | None:
        key = (model_id, model_version)
        if key in self.in_memory:
            return self.in_memory[key]
        try:
            import mlflow  # type: ignore
            from mlflow.tracking import MlflowClient  # type: ignore
        except Exception:
            return None
        mlflow.set_tracking_uri(prepare_mlflow_tracking_uri(self.tracking_uri))
        try:
            client = MlflowClient()
            experiments = client.search_experiments()
            experiment_ids = [experiment.experiment_id for experiment in experiments]
            if not experiment_ids:
                return None
            runs = client.search_runs(
                experiment_ids=experiment_ids,
                max_results=1000,
                order_by=["attributes.start_time DESC"],
            )
        except Exception:
            return None
        for run in runs:
            tags = run.data.tags
            if tags.get("model_id") != model_id or tags.get("model_version") != model_version:
                continue
            public_demo_eligible = str(tags.get("public_demo_eligible", "false")).lower() == "true"
            return MLflowModelMetadata(
                model_id=model_id,
                model_version=model_version,
                approval_status=tags.get("approval_status", "experimental"),
                artifact_uri=tags.get("artifact_uri"),
                supported_universe_id=tags.get("supported_universe_id"),
                public_demo_eligible=public_demo_eligible,
                registry_revision=tags.get("registry_revision"),
                raw={"run_id": run.info.run_id, "tags": dict(tags), "params": dict(run.data.params), "metrics": dict(run.data.metrics)},
            )
        return None
