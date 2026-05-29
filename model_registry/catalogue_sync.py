"""Fail-closed synchronization between SQLite catalogue and MLflow metadata."""

from __future__ import annotations

from model_registry.approval import ApprovalDecision, reconcile_model
from model_registry.conflict_log import log_conflict
from model_registry.mlflow_client import MLflowMetadataClient
from storage.repositories import Repository


class CatalogueSyncService:
    def __init__(self, repo: Repository, mlflow_client: MLflowMetadataClient | None = None):
        self.repo = repo
        self.mlflow_client = mlflow_client or MLflowMetadataClient()

    def sync_model(self, model_id: str, model_version: str) -> ApprovalDecision:
        model = self.repo.get_model(model_id, model_version)
        if not model:
            return ApprovalDecision(False, False, reason="unavailable_model", user_message="Model not found.")
        mlflow_model = self.mlflow_client.get_model_metadata(model_id, model_version)
        decision = reconcile_model(model, mlflow_model, runtime_context="public_demo" if model.get("public_demo_eligible") else "local")
        if not decision.prediction_allowed and decision.conflict_type:
            sqlite_value = model.get("mlflow_model_uri") if decision.conflict_type == "artifact_uri" else model.get(decision.conflict_type)
            mlflow_value = getattr(mlflow_model, "artifact_uri", None) if mlflow_model else None
            log_conflict(
                self.repo,
                model_id,
                model_version,
                decision.conflict_type,
                sqlite_value,
                mlflow_value,
                decision.user_message or "Model registry conflict.",
            )
        return decision

