import pytest

from backend.schemas.contracts import ModelEvidence
from backend.services.evidence_service import EvidenceService, EvidenceUnavailableError


def test_loaded_evidence_matches_contract(seeded_repo):
    evidence = EvidenceService(seeded_repo).get_model_evidence("idx-direction-baseline", "2026.05")
    parsed = ModelEvidence.model_validate(evidence)
    assert parsed.evidence_load_status == "loaded"
    assert parsed.historical_performance_caveat
    assert parsed.barrier_config["volatility_measure"] == "20-day ATR"
    assert parsed.barrier_config["vertical_barrier_sessions"] == 5


@pytest.mark.parametrize("load_status", ["missing", "stale", "unavailable", "not_loaded"])
def test_required_evidence_load_status_blocks_prediction(seeded_repo, load_status):
    seeded_repo.conn.execute(
        "UPDATE model_evidence SET evidence_load_status=? WHERE model_id='idx-direction-baseline'",
        (load_status,),
    )
    seeded_repo.conn.commit()
    with pytest.raises(EvidenceUnavailableError):
        EvidenceService(seeded_repo).require_loaded_evidence("idx-direction-baseline", "2026.05")
