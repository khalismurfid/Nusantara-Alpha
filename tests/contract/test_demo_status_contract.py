from backend.schemas.contracts import DemoStatusResponse
from backend.services.demo_status_service import DemoStatusService


def test_demo_status_full_response_matches_contract(seeded_repo):
    status = DemoStatusService(seeded_repo, runtime_context="public_demo").get_status()
    parsed = DemoStatusResponse.model_validate(status)
    assert parsed.release_status == "full"
    assert parsed.public_predictions_available is True


def test_demo_status_degraded_response_matches_contract(seeded_repo):
    seeded_repo.conn.execute("DELETE FROM deployable_data_assets")
    seeded_repo.conn.commit()
    status = DemoStatusService(seeded_repo, runtime_context="public_demo").get_status()
    parsed = DemoStatusResponse.model_validate(status)
    assert parsed.release_status == "degraded"
    assert parsed.public_predictions_available is False

