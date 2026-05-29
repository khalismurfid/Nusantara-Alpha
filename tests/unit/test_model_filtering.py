from backend.services.model_service import ModelService


def test_model_list_hides_unapproved_and_conflicted_models(seeded_repo):
    seeded_repo.upsert_model(
        {
            "model_id": "experimental-model",
            "model_version": "dev",
            "model_name": "Experimental",
            "description": "Hidden experiment",
            "status": "experimental",
            "model_origin": "experimental",
            "public_demo_eligible": False,
            "supported_universe_id": "idx-liquid-demo",
            "evaluation_period_start": "2025-01-01",
            "evaluation_period_end": "2025-12-31",
            "evidence_available": False,
            "evidence_load_status": "missing",
            "limitations": [],
            "mlflow_run_id": None,
            "mlflow_model_uri": None,
            "sqlite_catalogue_revision": "x",
            "mlflow_registry_revision": "x",
            "registry_sync_status": "current",
            "registry_conflict_reason": None,
        }
    )
    seeded_repo.upsert_model(
        {
            "model_id": "conflicted-model",
            "model_version": "1",
            "model_name": "Conflict",
            "description": "Conflict",
            "status": "approved",
            "model_origin": "real",
            "public_demo_eligible": True,
            "supported_universe_id": "idx-liquid-demo",
            "evaluation_period_start": "2025-01-01",
            "evaluation_period_end": "2025-12-31",
            "evidence_available": True,
            "evidence_load_status": "loaded",
            "limitations": [],
            "mlflow_run_id": "run",
            "mlflow_model_uri": "models:/conflict/1",
            "sqlite_catalogue_revision": "x",
            "mlflow_registry_revision": "y",
            "registry_sync_status": "conflict",
            "registry_conflict_reason": "version mismatch",
        }
    )
    models = ModelService(seeded_repo).list_models()["models"]
    ids = {model["model_id"] for model in models}
    assert "experimental-model" not in ids
    assert "conflicted-model" not in ids

