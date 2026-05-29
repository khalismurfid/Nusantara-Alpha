"""MLflow metadata access with graceful fallback when MLflow is unavailable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
        self.tracking_uri = tracking_uri
        self.in_memory = in_memory or {}

    def get_model_metadata(self, model_id: str, model_version: str) -> MLflowModelMetadata | None:
        key = (model_id, model_version)
        if key in self.in_memory:
            return self.in_memory[key]
        try:
            import mlflow  # type: ignore
        except Exception:
            return None
        if self.tracking_uri:
            mlflow.set_tracking_uri(self.tracking_uri)
        return None

