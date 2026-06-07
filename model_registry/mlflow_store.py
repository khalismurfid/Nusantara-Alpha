"""MLflow tracking-store configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_MLFLOW_TRACKING_URI = "sqlite:///./.local/mlflow_tracking.sqlite"


def resolve_mlflow_tracking_uri(tracking_uri: str | None = None) -> str:
    """Resolve the MLflow tracking URI from explicit input, env, or default."""
    return tracking_uri or os.getenv("NUSANTARA_MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_TRACKING_URI)


def prepare_mlflow_tracking_uri(tracking_uri: str | None = None) -> str:
    """Resolve a tracking URI and create local SQLite parent directories."""
    resolved = resolve_mlflow_tracking_uri(tracking_uri)
    if resolved.startswith("sqlite:///"):
        db_path = resolved.removeprefix("sqlite:///")
        if db_path and db_path != ":memory:":
            Path(db_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
    return resolved
