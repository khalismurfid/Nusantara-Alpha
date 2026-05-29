"""Seed a local development database with safe sample records."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app_streamlit.copy.disclaimers import DISCLAIMER_VERSION, EDUCATIONAL_DISCLAIMER
from storage.database import connect, initialize
from storage.repositories import Repository


def seed_connection(repo: Repository) -> None:
    now = datetime(2026, 5, 29, 9, 0, tzinfo=timezone.utc).isoformat()
    repo.upsert_disclaimer(
        {
            "disclaimer_id": "educational-research",
            "version": DISCLAIMER_VERSION,
            "text": EDUCATIONAL_DISCLAIMER,
            "placement": "prediction_flow_and_output",
            "effective_date": "2026-05-29",
        }
    )
    repo.upsert_model(
        {
            "model_id": "idx-direction-baseline",
            "model_version": "2026.05",
            "model_name": "IDX Direction Baseline",
            "description": "Approved baseline model for next-session direction research.",
            "status": "approved",
            "model_origin": "real",
            "public_demo_eligible": True,
            "supported_universe_id": "idx-liquid-demo",
            "evaluation_period_start": "2023-01-01",
            "evaluation_period_end": "2026-04-30",
            "evidence_available": True,
            "evidence_load_status": "loaded",
            "limitations": ["Small supported universe", "Historical evidence may not generalize"],
            "mlflow_run_id": "run-idx-baseline-202605",
            "mlflow_model_uri": "models:/idx-direction-baseline/2026.05",
            "sqlite_catalogue_revision": "catalogue-2026-05-29",
            "mlflow_registry_revision": "registry-2026-05-29",
            "registry_sync_status": "current",
            "registry_conflict_reason": None,
        }
    )
    repo.upsert_model(
        {
            "model_id": "local-dummy-flow",
            "model_version": "dev",
            "model_name": "Local Dummy Flow",
            "description": "Development-only flow fixture that is never public-demo eligible.",
            "status": "approved",
            "model_origin": "local_mock",
            "public_demo_eligible": False,
            "supported_universe_id": "idx-liquid-demo",
            "evaluation_period_start": "2024-01-01",
            "evaluation_period_end": "2024-12-31",
            "evidence_available": True,
            "evidence_load_status": "loaded",
            "limitations": ["Development-only dummy output"],
            "mlflow_run_id": None,
            "mlflow_model_uri": None,
            "sqlite_catalogue_revision": "local",
            "mlflow_registry_revision": "local",
            "registry_sync_status": "current",
            "registry_conflict_reason": None,
        }
    )
    for model_id, version in [("idx-direction-baseline", "2026.05"), ("local-dummy-flow", "dev")]:
        repo.upsert_evidence(
            {
                "evidence_id": f"evidence-{model_id}-{version}",
                "model_id": model_id,
                "model_version": version,
                "evidence_type": "backtest",
                "evaluation_period_start": "2023-01-01",
                "evaluation_period_end": "2026-04-30",
                "key_metrics": [
                    {"name": "Directional accuracy", "value": "54%", "interpretation": "Slightly above random in this historical window"},
                    {"name": "Coverage", "value": "3 IDX stocks", "interpretation": "Limited demonstration universe"},
                ],
                "performance_summary": "Historical evidence is modest and should be interpreted cautiously.",
                "supported_universe": ["BBCA", "TLKM", "ASII"],
                "limitations": ["Limited universe", "No guarantee of future accuracy"],
                "data_quality_notes": ["Static approved sample data", "Corporate-action handling documented for review"],
                "historical_performance_caveat": "Historical performance may not generalize to future market sessions.",
                "evidence_status": "complete",
                "evidence_load_status": "loaded",
                "evidence_as_of": now,
                "data_source_mode": "approved",
                "paper_trading_summary": "No paper-trading evidence is available yet.",
            }
        )
    for ticker, name in [("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk"), ("ASII", "Astra International Tbk")]:
        repo.upsert_stock(
            {
                "ticker": ticker,
                "name": name,
                "exchange": "IDX",
                "universe_id": "idx-liquid-demo",
                "support_status": "supported",
                "unavailable_reason": None,
                "data_as_of": now,
                "freshness_status": "fresh",
                "market_data_flags": [],
            }
        )
        repo.upsert_data_availability(
            {
                "model_id": "idx-direction-baseline",
                "ticker": ticker,
                "required_period_start": "2023-01-01",
                "required_period_end": "2026-05-28",
                "data_as_of": now,
                "feature_generation_timestamp": now,
                "freshness_status": "fresh",
                "chronology_status": "valid",
                "quality_flags": [],
                "blocking_reason": None,
            }
        )
    repo.upsert_stock(
        {
            "ticker": "GOTO",
            "name": "GoTo Gojek Tokopedia Tbk",
            "exchange": "IDX",
            "universe_id": "idx-liquid-demo",
            "support_status": "unsupported",
            "unavailable_reason": "This ticker is outside the selected model's supported universe.",
            "data_as_of": None,
            "freshness_status": "missing",
            "market_data_flags": ["unsupported_universe"],
        }
    )
    repo.upsert_data_availability(
        {
            "model_id": "idx-direction-baseline",
            "ticker": "GOTO",
            "required_period_start": "2023-01-01",
            "required_period_end": "2026-05-28",
            "data_as_of": None,
            "feature_generation_timestamp": None,
            "freshness_status": "missing",
            "chronology_status": "valid",
            "quality_flags": ["unsupported_universe"],
            "blocking_reason": "unsupported_stock",
        }
    )
    repo.upsert_model(
        {
            "model_id": "registry-conflict-fixture",
            "model_version": "1",
            "model_name": "Registry Conflict Fixture",
            "description": "Fixture for fail-closed registry conflict behavior.",
            "status": "approved",
            "model_origin": "real",
            "public_demo_eligible": True,
            "supported_universe_id": "idx-liquid-demo",
            "evaluation_period_start": "2023-01-01",
            "evaluation_period_end": "2026-04-30",
            "evidence_available": True,
            "evidence_load_status": "loaded",
            "limitations": ["Conflict fixture only"],
            "mlflow_run_id": "conflict-run",
            "mlflow_model_uri": "models:/registry-conflict-fixture/1",
            "sqlite_catalogue_revision": "catalogue-a",
            "mlflow_registry_revision": "registry-b",
            "registry_sync_status": "conflict",
            "registry_conflict_reason": "fixture conflict",
        }
    )
    repo.upsert_deployable_asset(
        {
            "asset_id": "approved-static-idx-sample",
            "asset_type": "approved_artifact",
            "classification": "public_demo_allowed",
            "data_as_of": now,
            "limitations": "Static approved non-sensitive demonstration data.",
            "approval_reference": "internal-demo-approval-2026-05-29",
        }
    )


def seed_database(db_path: str | Path) -> None:
    conn = connect(db_path)
    initialize(conn)
    seed_connection(Repository(conn))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_database("./.local/nusantara_alpha.sqlite3")
