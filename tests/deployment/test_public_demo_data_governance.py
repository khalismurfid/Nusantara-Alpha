from backend.services.demo_status_service import DemoStatusService


def test_public_demo_status_does_not_expose_restricted_content(seeded_repo):
    status = DemoStatusService(seeded_repo, runtime_context="public_demo").get_status()
    rendered = str(status).lower()
    for forbidden in ["secret", "credential", "private dataset", "proprietary file", "/users/"]:
        assert forbidden not in rendered

