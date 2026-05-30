from app_streamlit.components.demo_banner import format_demo_banner
from backend.services.demo_status_service import DemoStatusService


def test_degraded_demo_labels_release_gate_failure(seeded_repo):
    seeded_repo.conn.execute("DELETE FROM deployable_data_assets")
    seeded_repo.conn.commit()
    status = DemoStatusService(seeded_repo, runtime_context="public_demo").get_status()
    banner = format_demo_banner(status)
    assert banner["release_status"] == "degraded"
    assert banner["title"] == "Signal availability"
    assert banner["public_predictions_available"] is False
    assert "paused" in banner["message"].lower()
    assert "full public prediction" not in banner["message"].lower()
    assert "demo data as of" not in str(banner).lower()
