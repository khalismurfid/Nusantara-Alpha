from backend.services.demo_status_service import DemoStatusService


def test_public_demo_release_gate_requires_real_model_and_approved_data(seeded_repo):
    status = DemoStatusService(seeded_repo, runtime_context="public_demo").get_status()
    assert status["real_approved_model_available"] is True
    assert status["approved_data_source_available"] is True
    assert status["public_predictions_available"] is True

