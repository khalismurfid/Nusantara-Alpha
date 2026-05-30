"""Fail-closed model approval reconciliation."""

from __future__ import annotations

from dataclasses import dataclass

from model_registry.mlflow_client import MLflowModelMetadata


@dataclass(frozen=True)
class ApprovalDecision:
    visible: bool
    prediction_allowed: bool
    reason: str | None = None
    conflict_type: str | None = None
    user_message: str | None = None


def reconcile_model(sqlite_model: dict, mlflow_model: MLflowModelMetadata | None, runtime_context: str = "local") -> ApprovalDecision:
    if sqlite_model.get("status") != "approved":
        return _blocked("unavailable_model", "This model is not approved for display.")
    if sqlite_model.get("registry_sync_status") == "conflict":
        return _blocked("registry_conflict", "This model is temporarily unavailable while its approval records are reviewed.")
    if sqlite_model.get("registry_sync_status") == "stale":
        return _blocked("sync_stale", "This model is temporarily unavailable while its approval records are refreshed.")
    if sqlite_model.get("registry_sync_status") != "current":
        return _blocked("sync_incomplete", "This model is temporarily unavailable until approval records are complete.")
    if runtime_context == "public_demo":
        if sqlite_model.get("model_origin") != "real":
            return _blocked("public_demo_eligibility", "Public demo predictions require a real approved model.")
        if not sqlite_model.get("public_demo_eligible"):
            return _blocked("public_demo_eligibility", "This model is not eligible for public demo prediction.")
    if mlflow_model is None:
        if sqlite_model.get("mlflow_model_uri"):
            return ApprovalDecision(True, True)
        if runtime_context == "public_demo":
            return _blocked("artifact_uri", "Public demo model metadata is incomplete.")
        return ApprovalDecision(True, True)
    comparisons = [
        ("approval_status", sqlite_model.get("status"), mlflow_model.approval_status),
        ("model_version", sqlite_model.get("model_version"), mlflow_model.model_version),
        ("artifact_uri", sqlite_model.get("mlflow_model_uri"), mlflow_model.artifact_uri),
        ("supported_universe", sqlite_model.get("supported_universe_id"), mlflow_model.supported_universe_id),
        ("public_demo_eligibility", bool(sqlite_model.get("public_demo_eligible")), mlflow_model.public_demo_eligible),
    ]
    for conflict_type, sqlite_value, mlflow_value in comparisons:
        if sqlite_value != mlflow_value:
            return _blocked(
                conflict_type,
                "This model is temporarily unavailable while its approval records are reviewed.",
            )
    return ApprovalDecision(True, True)


def _blocked(conflict_type: str, message: str) -> ApprovalDecision:
    return ApprovalDecision(False, False, reason=conflict_type, conflict_type=conflict_type, user_message=message)
