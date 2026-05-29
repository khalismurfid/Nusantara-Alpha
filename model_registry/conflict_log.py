"""Sanitized registry conflict logging helpers."""

from __future__ import annotations

from storage.repositories import Repository


SENSITIVE_MARKERS = ("secret", "token", "password", "private", "/Users/", "\\Users\\")


def sanitize_value(value: object) -> str:
    text = "" if value is None else str(value)
    lowered = text.lower()
    if any(marker.lower() in lowered for marker in SENSITIVE_MARKERS):
        return "[redacted]"
    return text[:240]


def log_conflict(repo: Repository, model_id: str, model_version: str, conflict_type: str, sqlite_value: object, mlflow_value: object, user_message: str) -> str:
    return repo.record_registry_conflict(
        {
            "model_id": model_id,
            "model_version": model_version,
            "conflict_type": conflict_type,
            "sqlite_value": sanitize_value(sqlite_value),
            "mlflow_value": sanitize_value(mlflow_value),
            "resolution_status": "open",
            "user_message": user_message,
        }
    )

