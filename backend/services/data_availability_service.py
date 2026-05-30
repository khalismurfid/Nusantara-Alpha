"""Data availability service."""

from __future__ import annotations

from ml.validation.market_data import assess_market_data
from storage.repositories import Repository


class DataAvailabilityService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def assess(self, model_id: str, ticker: str) -> dict:
        state = self.repo.get_data_availability(model_id, ticker)
        if not state:
            return {"allowed": False, "reason": "missing_data", "message": "The latest required data is not available for this ticker yet."}
        if state.get("chronology_status") != "valid":
            return {
                "allowed": False,
                "reason": "chronology_violation",
                "message": "This output is paused because the available data cannot be matched safely to the prediction time.",
            }
        assessment = assess_market_data(state.get("freshness_status"), state.get("quality_flags"))
        return {
            "allowed": assessment.allowed,
            "reason": assessment.blocking_reason,
            "message": "; ".join(assessment.notes) or "Data is available for this ticker.",
            "state": state,
        }
