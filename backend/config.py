"""Runtime configuration for the Nusantara Alpha service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from model_registry.mlflow_store import DEFAULT_MLFLOW_TRACKING_URI


@dataclass(frozen=True)
class Settings:
    api_base_url: str
    sqlite_path: Path
    mlflow_tracking_uri: str
    runtime_context: str
    data_path: Path
    public_demo_url: str | None

    @property
    def is_public_demo(self) -> bool:
        return self.runtime_context == "public_demo"


def get_settings() -> Settings:
    return Settings(
        api_base_url=os.getenv("NUSANTARA_API_BASE_URL", "http://localhost:8000"),
        sqlite_path=Path(os.getenv("NUSANTARA_SQLITE_PATH", "./.local/nusantara_alpha.sqlite3")),
        mlflow_tracking_uri=os.getenv("NUSANTARA_MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_TRACKING_URI),
        runtime_context=os.getenv("NUSANTARA_RUNTIME_CONTEXT", "local"),
        data_path=Path(os.getenv("NUSANTARA_DATA_PATH", "./data/sample")),
        public_demo_url=os.getenv("NUSANTARA_PUBLIC_DEMO_URL") or None,
    )
