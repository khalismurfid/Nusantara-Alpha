from app_streamlit.components.evidence_panel import format_evidence
from backend.services.evidence_service import EvidenceService


def test_evidence_panel_includes_required_context(seeded_repo):
    evidence = EvidenceService(seeded_repo).get_model_evidence("idx-direction-baseline", "2026.05")
    formatted = format_evidence(evidence)
    assert formatted["metrics"]
    assert formatted["evaluation_period"]
    assert formatted["supported_universe"]
    assert formatted["limitations"]
    assert formatted["data_quality_notes"]
    assert "may not generalize" in formatted["historical_performance_caveat"].lower()

