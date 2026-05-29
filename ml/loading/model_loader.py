"""Model loading boundary for approved model metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LoadedModel:
    model_id: str
    model_version: str
    model_name: str
    artifact_uri: str | None
    raw: Any = None


def load_model(model_metadata: dict[str, Any]) -> LoadedModel:
    if model_metadata.get("status") != "approved":
        raise ValueError("Only approved models can be loaded.")
    if model_metadata.get("registry_sync_status") != "current":
        raise ValueError("Model registry synchronization is not current.")
    return LoadedModel(
        model_id=model_metadata["model_id"],
        model_version=model_metadata["model_version"],
        model_name=model_metadata["model_name"],
        artifact_uri=model_metadata.get("mlflow_model_uri"),
        raw=None,
    )

