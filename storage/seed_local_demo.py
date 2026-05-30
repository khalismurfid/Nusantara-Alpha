"""Seed a local development database with safe sample records."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app_streamlit.copy.disclaimers import DISCLAIMER_VERSION, EDUCATIONAL_DISCLAIMER
from ml.backtesting.realistic import backtest_pooled_model
from ml.market_data.yfinance_ingestion import idx_to_yahoo_symbol
from storage.database import connect, initialize
from storage.repositories import Repository


def seed_connection(repo: Repository) -> None:
    now = datetime(2026, 5, 29, 9, 0, tzinfo=timezone.utc).isoformat()
    supported_names = [("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk"), ("ASII", "Astra International Tbk")]
    sample_price_rows = _sample_market_prices(supported_names)
    backtest = backtest_pooled_model(sample_price_rows)
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
            "description": "Baseline model that estimates next-session direction for a small reviewed IDX set.",
            "status": "approved",
            "model_origin": "real",
            "public_demo_eligible": True,
            "supported_universe_id": "idx-liquid-demo",
            "evaluation_period_start": "2023-01-01",
            "evaluation_period_end": "2026-04-30",
            "evidence_available": True,
            "evidence_load_status": "loaded",
            "limitations": [
                "This model currently covers a small group of liquid IDX names, so other stocks need separate review.",
                "Historical results can differ from future market behavior.",
            ],
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
                    {
                        "name": "Directional accuracy",
                        "value": f"{backtest['directional_accuracy']:.0%}",
                        "interpretation": "Share of held-out next-session directions classified correctly in chronological testing.",
                    },
                    {
                        "name": "Average return after cost",
                        "value": f"{backtest['average_next_session_return_after_cost']:.2%}",
                        "interpretation": "Average simulated next-session return after a 0.25% round-trip cost assumption.",
                    },
                    {
                        "name": "Coverage",
                        "value": f"{backtest['ticker_count']} IDX stocks",
                        "interpretation": "Training and testing use a pooled model across the reviewed ticker universe.",
                    },
                ],
                "performance_summary": "Historical evidence uses chronological next-open to next-close simulation and should be interpreted cautiously.",
                "supported_universe": ["BBCA", "TLKM", "ASII"],
                "limitations": [
                    "The model currently covers BBCA, TLKM, and ASII only, so other tickers need separate validation.",
                    "Future market sessions can behave differently from the historical test period.",
                ],
                "data_quality_notes": [
                    "Uses static approved sample data for the local product flow.",
                    "Corporate-action handling is documented for reviewer inspection.",
                ],
                "historical_performance_caveat": "Historical performance may not generalize to future market sessions.",
                "evidence_status": "complete",
                "evidence_load_status": "loaded",
                "evidence_as_of": now,
                "data_source_mode": "approved",
                "paper_trading_summary": "No paper-trading evidence is available yet.",
            }
        )
    for ticker, name in supported_names:
        repo.upsert_idx_universe(
            {
                "ticker": ticker,
                "company_name": name,
                "yahoo_symbol": idx_to_yahoo_symbol(ticker),
                "active": True,
                "source": "local-approved-sample",
                "source_date": "2026-05-29",
            }
        )
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
    repo.upsert_market_prices(sample_price_rows)
    repo.upsert_stock(
        {
            "ticker": "GOTO",
            "name": "GoTo Gojek Tokopedia Tbk",
            "exchange": "IDX",
            "universe_id": "idx-liquid-demo",
            "support_status": "unsupported",
            "unavailable_reason": "This model has not been reviewed for GOTO yet.",
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
    repo.upsert_stock(
        {
            "ticker": "SMGR",
            "name": "Semen Indonesia Persero Tbk",
            "exchange": "IDX",
            "universe_id": "idx-liquid-demo",
            "support_status": "temporarily_unavailable",
            "unavailable_reason": "Recent data for SMGR is not fresh enough for this model right now.",
            "data_as_of": "2026-05-20T09:00:00+00:00",
            "freshness_status": "stale",
            "market_data_flags": ["stale_required_data"],
        }
    )
    repo.upsert_data_availability(
        {
            "model_id": "idx-direction-baseline",
            "ticker": "SMGR",
            "required_period_start": "2023-01-01",
            "required_period_end": "2026-05-28",
            "data_as_of": "2026-05-20T09:00:00+00:00",
            "feature_generation_timestamp": "2026-05-20T09:00:00+00:00",
            "freshness_status": "stale",
            "chronology_status": "valid",
            "quality_flags": ["stale_required_data"],
            "blocking_reason": "stale_data",
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
            "limitations": ["This fixture is used only to verify unavailable-model handling."],
            "mlflow_run_id": "conflict-run",
            "mlflow_model_uri": "models:/registry-conflict-fixture/1",
            "sqlite_catalogue_revision": "catalogue-a",
            "mlflow_registry_revision": "registry-b",
            "registry_sync_status": "conflict",
            "registry_conflict_reason": "Approval records need review before this model can be shown.",
        }
    )
    repo.upsert_deployable_asset(
        {
            "asset_id": "approved-static-idx-sample",
            "asset_type": "approved_artifact",
            "classification": "public_demo_allowed",
            "data_as_of": now,
            "limitations": "Static approved non-sensitive data for reviewing the product flow.",
            "approval_reference": "internal-demo-approval-2026-05-29",
        }
    )


def seed_database(db_path: str | Path) -> None:
    conn = connect(db_path)
    initialize(conn)
    seed_connection(Repository(conn))
    conn.commit()
    conn.close()


def _sample_market_prices(stocks: list[tuple[str, str]]) -> list[dict]:
    rows = []
    fetched_at = datetime(2026, 5, 29, 9, 0, tzinfo=timezone.utc).isoformat()
    start = datetime(2025, 12, 1, tzinfo=timezone.utc)
    bases = {"BBCA": 9000.0, "TLKM": 3100.0, "ASII": 5200.0}
    offsets = {"BBCA": 0.0, "TLKM": 1.1, "ASII": 2.2}
    trading_index = 0
    for day_offset in range(180):
        current = start + timedelta(days=day_offset)
        if current.weekday() >= 5:
            continue
        for ticker, _ in stocks:
            base = bases[ticker]
            offset = offsets[ticker]
            trend = 1 + (trading_index * 0.0008)
            cycle = math.sin((trading_index / 4.0) + offset)
            overnight = 1 + (0.003 * math.sin((trading_index / 5.0) + offset))
            intraday = 0.006 * math.sin((trading_index / 3.0) + offset) + (0.001 if ticker == "BBCA" else -0.0005)
            open_price = base * trend * overnight * (1 + 0.015 * cycle)
            close_price = open_price * (1 + intraday)
            high = max(open_price, close_price) * 1.006
            low = min(open_price, close_price) * 0.994
            rows.append(
                {
                    "ticker": ticker,
                    "price_date": current.date().isoformat(),
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close_price, 2),
                    "adj_close": round(close_price, 2),
                    "volume": 1_000_000 + (trading_index * 7500) + int(50_000 * abs(cycle)),
                    "source": "local-approved-sample",
                    "fetched_at": fetched_at,
                }
            )
        trading_index += 1
    return rows


if __name__ == "__main__":
    seed_database("./.local/nusantara_alpha.sqlite3")
