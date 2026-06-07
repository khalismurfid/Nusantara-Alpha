from model_registry.catalogue_sync import CatalogueSyncService
from model_registry.mlflow_client import MLflowMetadataClient, MLflowModelMetadata


def test_registry_conflict_hides_model_and_logs_conflict(seeded_repo):
    client = MLflowMetadataClient(
        in_memory={
            ("idx-direction-baseline", "2026.05"): MLflowModelMetadata(
                model_id="idx-direction-baseline",
                model_version="2026.05",
                approval_status="approved",
                artifact_uri="models:/different/uri",
                supported_universe_id="idx-approved-universe",
                public_demo_eligible=True,
                registry_revision="registry-2026-05-29",
                raw={},
            )
        }
    )
    service = CatalogueSyncService(seeded_repo, client)
    result = service.sync_model("idx-direction-baseline", "2026.05")
    assert not result.prediction_allowed
    conflicts = seeded_repo.list_open_registry_conflicts("idx-direction-baseline")
    assert conflicts
