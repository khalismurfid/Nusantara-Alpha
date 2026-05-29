"""Model catalogue service."""

from __future__ import annotations

from backend.schemas.contracts import CuratedModel, DateRange
from model_registry.approval import reconcile_model
from model_registry.conflict_log import log_conflict
from model_registry.mlflow_client import MLflowMetadataClient
from storage.repositories import Repository


class ModelService:
    def __init__(self, repo: Repository, runtime_context: str = "local", mlflow_client: MLflowMetadataClient | None = None):
        self.repo = repo
        self.runtime_context = runtime_context
        self.mlflow_client = mlflow_client or MLflowMetadataClient()

    def list_models(self) -> dict:
        visible = []
        for model in self.repo.list_models(self.runtime_context):
            decision = reconcile_model(
                model,
                self.mlflow_client.get_model_metadata(model["model_id"], model["model_version"]),
                self.runtime_context,
            )
            if decision.visible:
                visible.append(self._to_contract(model).model_dump(mode="json"))
            elif decision.conflict_type:
                log_conflict(
                    self.repo,
                    model["model_id"],
                    model["model_version"],
                    decision.conflict_type,
                    "sqlite",
                    "mlflow",
                    decision.user_message or "Model unavailable.",
                )
        return {"models": visible}

    def get_approved_model(self, model_id: str, model_version: str) -> dict | None:
        model = self.repo.get_model(model_id, model_version)
        if not model:
            return None
        decision = reconcile_model(
            model,
            self.mlflow_client.get_model_metadata(model_id, model_version),
            self.runtime_context,
        )
        if not decision.prediction_allowed:
            if decision.conflict_type:
                log_conflict(
                    self.repo,
                    model_id,
                    model_version,
                    decision.conflict_type,
                    "sqlite",
                    "mlflow",
                    decision.user_message or "Model unavailable.",
                )
            return None
        return model

    def _to_contract(self, model: dict) -> CuratedModel:
        return CuratedModel(
            model_id=model["model_id"],
            model_version=model["model_version"],
            model_name=model["model_name"],
            description=model["description"],
            status="approved",
            model_origin=model["model_origin"],
            public_demo_eligible=model["public_demo_eligible"],
            registry_sync_status=model["registry_sync_status"],
            registry_conflict_reason=model.get("registry_conflict_reason"),
            evaluation_period=DateRange(start=model["evaluation_period_start"], end=model["evaluation_period_end"]),
            supported_universe_id=model["supported_universe_id"],
            evidence_available=model["evidence_available"],
            evidence_load_status=model["evidence_load_status"],
            limitations=model["limitations"],
        )

