"""Public demo release-gate service."""

from __future__ import annotations

from app_streamlit.copy.disclaimers import EDUCATIONAL_DISCLAIMER
from backend.schemas.contracts import DemoStatusResponse
from backend.services.evidence_service import EvidenceService, EvidenceUnavailableError
from backend.services.model_service import ModelService
from storage.repositories import Repository


class DemoStatusService:
    def __init__(self, repo: Repository, runtime_context: str = "local", public_demo_url: str | None = None):
        self.repo = repo
        self.runtime_context = runtime_context
        self.public_demo_url = public_demo_url

    def get_status(self) -> dict:
        models = ModelService(self.repo, runtime_context="public_demo").list_models()["models"]
        real_model_with_evidence = False
        for model in models:
            try:
                EvidenceService(self.repo).require_loaded_evidence(model["model_id"], model["model_version"])
                real_model_with_evidence = True
                break
            except EvidenceUnavailableError:
                continue
        assets = self.repo.list_public_demo_assets()
        approved_data_available = bool(assets)
        full = real_model_with_evidence and approved_data_available
        first_asset = assets[0] if assets else {}
        release_status = "full" if full else "degraded"
        reason = None if full else "Public prediction is not available until a real approved model, loaded evidence, current registry sync, and approved data source are all present."
        response = DemoStatusResponse(
            environment_name="public_demo" if self.runtime_context == "public_demo" else "local",
            public_demo_url=self.public_demo_url,
            app_status="available" if full else "degraded",
            api_status="available",
            public_predictions_available=full,
            release_status=release_status,
            real_approved_model_available=real_model_with_evidence,
            approved_data_source_available=approved_data_available,
            release_gate_reason=reason,
            unavailable_reason=reason,
            data_source_mode="approved" if approved_data_available else "unavailable",
            data_as_of=first_asset.get("data_as_of"),
            demo_limitations=first_asset.get("limitations", "Prediction is unavailable in degraded demo mode."),
            disclaimer=EDUCATIONAL_DISCLAIMER,
        )
        return response.model_dump(mode="json")

