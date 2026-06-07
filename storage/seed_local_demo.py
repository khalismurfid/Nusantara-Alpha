"""Seed a local development database with safe sample records."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app_streamlit.copy.disclaimers import DISCLAIMER_VERSION, EDUCATIONAL_DISCLAIMER
from ml.backtesting.realistic import (
    ATR_WINDOW,
    BARRIER_ATR_MULTIPLE,
    VERTICAL_BARRIER_SESSIONS,
    backtest_pooled_model,
    fit_pooled_logistic_model,
    save_pooled_model,
)
from ml.market_data.yfinance_ingestion import idx_to_yahoo_symbol
from storage.database import connect, initialize
from storage.repositories import Repository

BASELINE_MODEL_ID = "idx-direction-baseline"
BASELINE_MODEL_VERSION = "2026.05"
BASELINE_MODEL_NAME = "Logistic Regression Model"
BASELINE_UNIVERSE_ID = "idx-approved-universe"
BASELINE_ARTIFACT_PATH = Path(".local/model_artifacts/idx-direction-baseline/2026.05/model.joblib")
BASELINE_ARTIFACT_URI = f"file:{BASELINE_ARTIFACT_PATH}"


def seed_connection(repo: Repository) -> None:
    now = datetime(2026, 5, 29, 9, 0, tzinfo=timezone.utc).isoformat()
    repo.retire_model("local-dummy-flow", "dev", "Replaced by the baseline logistic regression model.")
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
            "model_id": BASELINE_MODEL_ID,
            "model_version": BASELINE_MODEL_VERSION,
            "model_name": BASELINE_MODEL_NAME,
            "description": "Logistic regression model that looks up to five trading days ahead with ATR triple-barrier labels.",
            "status": "approved",
            "model_origin": "real",
            "public_demo_eligible": True,
            "supported_universe_id": BASELINE_UNIVERSE_ID,
            "evaluation_period_start": "2023-01-01",
            "evaluation_period_end": "2026-04-30",
            "evidence_available": True,
            "evidence_load_status": "loaded",
            "limitations": [
                "This local seed only includes a small approved sample universe. Load an approved IDX universe and refresh the baseline artifact for broader coverage.",
                "Historical results can differ from future market behavior.",
            ],
            "mlflow_run_id": "run-idx-baseline-202605",
            "mlflow_model_uri": BASELINE_ARTIFACT_URI,
            "sqlite_catalogue_revision": "catalogue-2026-05-29",
            "mlflow_registry_revision": "registry-2026-05-29",
            "registry_sync_status": "current",
            "registry_conflict_reason": None,
        }
    )
    repo.upsert_evidence(
        {
            "evidence_id": "evidence-idx-direction-baseline-2026.05",
            "model_id": BASELINE_MODEL_ID,
            "model_version": BASELINE_MODEL_VERSION,
            "evidence_type": "backtest",
            "evaluation_period_start": "2023-01-01",
            "evaluation_period_end": "2026-04-30",
            "key_metrics": [
                {
                    "name": "Triple-barrier accuracy",
                    "value": f"{backtest['directional_accuracy']:.0%}",
                    "interpretation": "Share of held-out upward, downward, or neutral near-term labels classified correctly in chronological testing.",
                },
                {
                    "name": "Average return after cost",
                    "value": f"{backtest['average_next_session_return_after_cost']:.2%}",
                    "interpretation": "Average simulated return after a 0.25% round-trip cost assumption when the model produced an upward signal.",
                },
                {
                    "name": "Neutral share",
                    "value": f"{backtest['neutral_share']:.0%}",
                    "interpretation": "Share of held-out predictions where the model did not identify a clear barrier direction.",
                },
                {
                    "name": "Coverage",
                    "value": f"{backtest['ticker_count']} IDX stocks",
                    "interpretation": "Training and testing use a pooled model across the reviewed ticker universe.",
                },
            ],
            "performance_summary": "Historical evidence uses a five-trading-day barrier test and should be interpreted cautiously.",
            "supported_universe": ["BBCA", "TLKM", "ASII"],
            "limitations": [
                "The local seed currently covers BBCA, TLKM, and ASII only. Broader coverage requires an approved IDX universe, approved OHLCV data, and a refreshed baseline artifact.",
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
            "barrier_config": {
                "method": "atr_triple_barrier",
                "horizon": "Looks up to 5 IDX trading sessions ahead.",
                "entry": "Uses the next session open after the signal date.",
                "volatility_measure": f"{ATR_WINDOW}-day ATR",
                "profit_barrier": f"Upward barrier at +{BARRIER_ATR_MULTIPLE:g}x ATR from entry.",
                "stop_barrier": f"Downward barrier at -{BARRIER_ATR_MULTIPLE:g}x ATR from entry.",
                "neutral_policy": "Neutral when neither barrier is reached within 5 trading sessions, or when daily OHLC cannot prove which barrier was reached first.",
                "vertical_barrier_sessions": VERTICAL_BARRIER_SESSIONS,
                "atr_window": ATR_WINDOW,
                "barrier_atr_multiple": BARRIER_ATR_MULTIPLE,
            },
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
                "universe_id": BASELINE_UNIVERSE_ID,
                "support_status": "supported",
                "unavailable_reason": None,
                "data_as_of": now,
                "freshness_status": "fresh",
                "market_data_flags": [],
            }
        )
        repo.upsert_data_availability(
            {
                "model_id": BASELINE_MODEL_ID,
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
            "universe_id": BASELINE_UNIVERSE_ID,
            "support_status": "unsupported",
            "unavailable_reason": "This model has not been reviewed for GOTO yet.",
            "data_as_of": None,
            "freshness_status": "missing",
            "market_data_flags": ["unsupported_universe"],
        }
    )
    repo.upsert_data_availability(
        {
            "model_id": BASELINE_MODEL_ID,
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
            "universe_id": BASELINE_UNIVERSE_ID,
            "support_status": "temporarily_unavailable",
            "unavailable_reason": "Recent data for SMGR is not fresh enough for this model right now.",
            "data_as_of": "2026-05-20T09:00:00+00:00",
            "freshness_status": "stale",
            "market_data_flags": ["stale_required_data"],
        }
    )
    repo.upsert_data_availability(
        {
            "model_id": BASELINE_MODEL_ID,
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
            "supported_universe_id": BASELINE_UNIVERSE_ID,
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
    repo = Repository(conn)
    seed_connection(repo)
    refresh_baseline_artifact(repo)
    conn.commit()
    conn.close()


def refresh_baseline_artifact(repo: Repository, artifact_path: str | Path = BASELINE_ARTIFACT_PATH):
    """Train and persist the baseline logistic artifact from currently approved rows."""
    supported = _supported_baseline_tickers(repo)
    model = fit_pooled_logistic_model(repo.list_market_prices(tickers=supported or None))
    save_pooled_model(model, artifact_path)
    return model


def refresh_baseline_evidence(repo: Repository, data_source_label: str = "approved yfinance OHLCV") -> dict:
    """Refresh customer-facing evidence from the current approved market rows."""
    supported = _supported_baseline_tickers(repo)
    price_rows = repo.list_market_prices(tickers=supported or None)
    backtest = backtest_pooled_model(price_rows)
    latest_price_date = repo.latest_market_price_date()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    coverage_note = (
        "Coverage is limited to IDX tickers with valid yfinance OHLCV rows and enough history for this model."
        if len(supported) > 3
        else "The local seed currently covers BBCA, TLKM, and ASII only. Broader coverage requires approved market data."
    )
    limitations = [
        coverage_note,
        "Future market sessions can behave differently from the historical test period.",
    ]
    model = repo.get_model(BASELINE_MODEL_ID, BASELINE_MODEL_VERSION)
    if model:
        model.update(
            {
                "model_name": BASELINE_MODEL_NAME,
                "description": "Logistic regression model that looks up to five trading days ahead with ATR triple-barrier labels.",
                "supported_universe_id": BASELINE_UNIVERSE_ID,
                "evaluation_period_start": backtest["evaluation_period_start"],
                "evaluation_period_end": backtest["evaluation_period_end"],
                "evidence_available": True,
                "evidence_load_status": "loaded",
                "limitations": limitations,
                "mlflow_model_uri": BASELINE_ARTIFACT_URI,
            }
        )
        repo.upsert_model(model)
    repo.upsert_evidence(
        {
            "evidence_id": "evidence-idx-direction-baseline-2026.05",
            "model_id": BASELINE_MODEL_ID,
            "model_version": BASELINE_MODEL_VERSION,
            "evidence_type": "backtest",
            "evaluation_period_start": backtest["evaluation_period_start"],
            "evaluation_period_end": backtest["evaluation_period_end"],
            "key_metrics": [
                {
                    "name": "Triple-barrier accuracy",
                    "value": f"{backtest['directional_accuracy']:.0%}",
                    "interpretation": "Share of held-out upward, downward, or neutral near-term labels classified correctly in chronological testing.",
                },
                {
                    "name": "Average return after cost",
                    "value": f"{backtest['average_next_session_return_after_cost']:.2%}",
                    "interpretation": "Average simulated return after a 0.25% round-trip cost assumption when the model produced an upward signal.",
                },
                {
                    "name": "Neutral share",
                    "value": f"{backtest['neutral_share']:.0%}",
                    "interpretation": "Share of held-out predictions where the model did not identify a clear barrier direction.",
                },
                {
                    "name": "Coverage",
                    "value": f"{len(supported)} IDX stocks",
                    "interpretation": "Training and testing use a pooled model across tickers with approved data and sufficient history.",
                },
            ],
            "performance_summary": "Historical evidence uses a five-trading-day barrier test and should be interpreted cautiously.",
            "supported_universe": supported,
            "limitations": limitations,
            "data_quality_notes": [
                f"Uses {data_source_label} rows through {latest_price_date or 'the latest available date'}.",
                "Corporate-action handling depends on the downloaded OHLCV adjustment fields and remains documented for reviewer inspection.",
            ],
            "historical_performance_caveat": "Historical performance may not generalize to future market sessions.",
            "evidence_status": "complete",
            "evidence_load_status": "loaded",
            "evidence_as_of": now,
            "data_source_mode": "approved",
            "barrier_config": _baseline_barrier_config(),
            "paper_trading_summary": "No paper-trading evidence is available yet.",
        }
    )
    return {
        "supported_tickers": len(supported),
        "latest_price_date": latest_price_date,
        "evaluation_period_start": backtest["evaluation_period_start"],
        "evaluation_period_end": backtest["evaluation_period_end"],
        "directional_accuracy": backtest["directional_accuracy"],
    }


def _supported_baseline_tickers(repo: Repository) -> list[str]:
    return [
        stock["ticker"]
        for stock in repo.search_stocks(BASELINE_UNIVERSE_ID)
        if stock["support_status"] == "supported"
    ]


def _baseline_barrier_config() -> dict:
    return {
        "method": "atr_triple_barrier",
        "horizon": "Looks up to 5 IDX trading sessions ahead.",
        "entry": "Uses the next session open after the signal date.",
        "volatility_measure": f"{ATR_WINDOW}-day ATR",
        "profit_barrier": f"Upward barrier at +{BARRIER_ATR_MULTIPLE:g}x ATR from entry.",
        "stop_barrier": f"Downward barrier at -{BARRIER_ATR_MULTIPLE:g}x ATR from entry.",
        "neutral_policy": "Neutral when neither barrier is reached within 5 trading sessions, or when daily OHLC cannot prove which barrier was reached first.",
        "vertical_barrier_sessions": VERTICAL_BARRIER_SESSIONS,
        "atr_window": ATR_WINDOW,
        "barrier_atr_multiple": BARRIER_ATR_MULTIPLE,
    }


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
        for stock_index, (ticker, _) in enumerate(stocks):
            ticker_seed = sum(ord(char) for char in ticker)
            base = bases.get(ticker, 1200.0 + (ticker_seed % 90) * 75.0)
            offset = offsets.get(ticker, 0.7 + stock_index * 0.83)
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
