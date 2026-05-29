"""Runtime configuration for the Nusantara Alpha service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_base_url: str
    sqlite_path: Path
    mlflow_tracking_uri: str
    runtime_context: str
    data_path: Path
    public_demo_url: str | None
    allow_local_dummy: bool

    @property
    def is_public_demo(self) -> bool:
        return self.runtime_context == "public_demo"


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    return Settings(
        api_base_url=os.getenv("NUSANTARA_API_BASE_URL", "http://localhost:8000"),
        sqlite_path=Path(os.getenv("NUSANTARA_SQLITE_PATH", "./.local/nusantara_alpha.sqlite3")),
        mlflow_tracking_uri=os.getenv("NUSANTARA_MLFLOW_TRACKING_URI", "./mlruns"),
        runtime_context=os.getenv("NUSANTARA_RUNTIME_CONTEXT", "local"),
        data_path=Path(os.getenv("NUSANTARA_DATA_PATH", "./data/sample")),
        public_demo_url=os.getenv("NUSANTARA_PUBLIC_DEMO_URL") or None,
        allow_local_dummy=_env_bool("NUSANTARA_ALLOW_LOCAL_DUMMY", True),
    )

