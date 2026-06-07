import pytest

from ml.experiments.baseline import run_baseline_logistic_experiment
from ml.experiments.mlflow_tracking import log_baseline_experiment_to_mlflow
from model_registry.mlflow_client import MLflowMetadataClient
from model_registry.promote_candidate import PromotionError, PromotionRequest, promote_candidate
from storage.database import connect, initialize
from storage.repositories import Repository
from storage.seed_local_demo import _sample_market_prices


def _sqlite_tracking_uri(tmp_path):
    return f"sqlite:///{tmp_path / 'mlflow_tracking.sqlite'}"


def test_baseline_experiment_logs_mlflow_run_and_artifact(tmp_path):
    rows = _sample_market_prices([("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk")])
    result = run_baseline_logistic_experiment(rows)
    tracking_uri = _sqlite_tracking_uri(tmp_path)

    logged = log_baseline_experiment_to_mlflow(
        result,
        rows,
        tracking_uri=tracking_uri,
        experiment_name="test-experiments",
        run_name="test-run",
    )

    assert logged.run_id
    assert logged.artifact_path == "model/model.joblib"


def test_promote_candidate_requires_manual_approval(tmp_path):
    with pytest.raises(PromotionError, match="Manual approval"):
        promote_candidate(
            PromotionRequest(
                run_id="missing",
                model_id="idx-test-model",
                model_version="1",
                model_name="IDX Test Model",
                supported_universe_id="idx-approved-universe",
                approved=False,
                sqlite_path=tmp_path / "test.sqlite3",
                tracking_uri=_sqlite_tracking_uri(tmp_path),
            )
        )


def test_promote_candidate_blocks_runs_without_required_metrics(tmp_path):
    import mlflow

    tracking_uri = _sqlite_tracking_uri(tmp_path)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("incomplete")
    with mlflow.start_run() as run:
        run_id = run.info.run_id

    with pytest.raises(PromotionError, match="missing required metrics"):
        promote_candidate(
            PromotionRequest(
                run_id=run_id,
                model_id="idx-test-model",
                model_version="1",
                model_name="IDX Test Model",
                supported_universe_id="idx-approved-universe",
                approved=True,
                sqlite_path=tmp_path / "test.sqlite3",
                tracking_uri=tracking_uri,
            )
        )


def test_promote_candidate_writes_catalogue_evidence_and_mlflow_sync_metadata(tmp_path):
    rows = _sample_market_prices(
        [
            ("BBCA", "Bank Central Asia Tbk"),
            ("TLKM", "Telkom Indonesia Tbk"),
            ("ASII", "Astra International Tbk"),
        ]
    )
    result = run_baseline_logistic_experiment(rows)
    tracking_uri = _sqlite_tracking_uri(tmp_path)
    sqlite_path = tmp_path / "test.sqlite3"
    logged = log_baseline_experiment_to_mlflow(
        result,
        rows,
        tracking_uri=tracking_uri,
        experiment_name="promotion-test",
        run_name="promotable-run",
    )

    promotion = promote_candidate(
        PromotionRequest(
            run_id=logged.run_id,
            model_id="idx-test-model",
            model_version="2026.06",
            model_name="IDX Test Model",
            supported_universe_id="idx-approved-universe",
            approved=True,
            public_demo_eligible=True,
            sqlite_path=sqlite_path,
            tracking_uri=tracking_uri,
            artifact_path=tmp_path / "artifacts" / "model.joblib",
        )
    )

    conn = connect(sqlite_path)
    initialize(conn)
    repo = Repository(conn)
    model = repo.get_model("idx-test-model", "2026.06")
    evidence = repo.get_evidence("idx-test-model", "2026.06")
    stocks = repo.search_stocks("idx-approved-universe")
    conn.close()
    metadata = MLflowMetadataClient(tracking_uri=tracking_uri).get_model_metadata("idx-test-model", "2026.06")

    assert promotion.registry_sync_status == "current"
    assert promotion.supported_tickers == 3
    assert model["status"] == "approved"
    assert model["public_demo_eligible"] is True
    assert model["mlflow_model_uri"] == promotion.artifact_uri
    assert evidence["evidence_load_status"] == "loaded"
    assert {stock["ticker"] for stock in stocks} == {"BBCA", "TLKM", "ASII"}
    assert metadata is not None
    assert metadata.approval_status == "approved"
    assert metadata.artifact_uri == promotion.artifact_uri
