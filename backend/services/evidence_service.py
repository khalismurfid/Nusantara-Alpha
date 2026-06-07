"""Evidence retrieval and evidence-before-prediction gates."""

from __future__ import annotations

from backend.schemas.contracts import DateRange, Metric, ModelEvidence
from storage.repositories import Repository


BLOCKING_LOAD_STATUSES = {"missing", "stale", "unavailable", "not_loaded"}
BLOCKING_EVIDENCE_STATUSES = {"missing", "stale"}


class EvidenceUnavailableError(ValueError):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason
        self.message = message


class EvidenceService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def get_model_evidence(self, model_id: str, model_version: str) -> dict:
        evidence = self.repo.get_evidence(model_id, model_version)
        if not evidence:
            raise EvidenceUnavailableError("missing_required_evidence", "Required model evidence is unavailable.")
        return self._to_contract(evidence).model_dump(mode="json")

    def require_loaded_evidence(self, model_id: str, model_version: str) -> dict:
        evidence = self.repo.get_evidence(model_id, model_version)
        if not evidence:
            raise EvidenceUnavailableError("missing_required_evidence", "Required model evidence is unavailable.")
        if evidence["evidence_load_status"] in BLOCKING_LOAD_STATUSES:
            reason = {
                "missing": "missing_required_evidence",
                "stale": "stale_required_evidence",
                "unavailable": "unavailable_required_evidence",
                "not_loaded": "evidence_not_loaded",
            }[evidence["evidence_load_status"]]
            raise EvidenceUnavailableError(reason, "Required model evidence is not loaded and valid.")
        if evidence["evidence_status"] in BLOCKING_EVIDENCE_STATUSES:
            reason = "stale_required_evidence" if evidence["evidence_status"] == "stale" else "missing_required_evidence"
            raise EvidenceUnavailableError(reason, "Required model evidence cannot support prediction.")
        return evidence

    def _to_contract(self, evidence: dict) -> ModelEvidence:
        return ModelEvidence(
            evidence_id=evidence["evidence_id"],
            model_id=evidence["model_id"],
            model_version=evidence["model_version"],
            evidence_type=evidence["evidence_type"],
            evaluation_period=DateRange(start=evidence["evaluation_period_start"], end=evidence["evaluation_period_end"]),
            key_metrics=[Metric(**metric) for metric in evidence["key_metrics"]],
            supported_universe=evidence["supported_universe"],
            limitations=evidence["limitations"],
            data_quality_notes=evidence["data_quality_notes"],
            historical_performance_caveat=evidence["historical_performance_caveat"],
            evidence_status=evidence["evidence_status"],
            evidence_load_status=evidence["evidence_load_status"],
            evidence_as_of=evidence["evidence_as_of"],
            data_source_mode=evidence["data_source_mode"],
            barrier_config=evidence.get("barrier_config", {}),
            paper_trading_summary=evidence.get("paper_trading_summary"),
        )
