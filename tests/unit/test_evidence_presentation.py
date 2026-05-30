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


def test_evidence_panel_provides_concise_summary_and_secondary_details(seeded_repo):
    evidence = EvidenceService(seeded_repo).get_model_evidence("idx-direction-baseline", "2026.05")
    formatted = format_evidence(evidence)

    summary = formatted["concise_summary"]
    assert summary["section_title"] == "Past performance snapshot"
    assert summary["headline"] == "Historical test period: 2023-01-01 to 2026-04-30"
    assert summary["metric_highlights"]
    assert summary["metric_highlights"][0]["name"] == "Directional accuracy"
    assert "reviewed IDX tickers" in summary["stocks_covered"]
    assert formatted["details_title"] == "More model details"
