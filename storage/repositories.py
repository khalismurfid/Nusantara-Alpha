"""SQLite repositories for catalogue, evidence, stock, logs, and demo metadata."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    if value in (None, ""):
        return default
    return json.loads(value)


class Repository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_model(self, model: dict[str, Any]) -> None:
        now = utc_now_iso()
        payload = {
            **model,
            "public_demo_eligible": int(bool(model.get("public_demo_eligible", False))),
            "evidence_available": int(bool(model.get("evidence_available", False))),
            "limitations_json": _json(model.get("limitations", [])),
            "created_at": model.get("created_at", now),
            "updated_at": now,
        }
        self.conn.execute(
            """
            INSERT OR REPLACE INTO model_catalogue (
                model_id, model_version, model_name, description, status, model_origin,
                public_demo_eligible, supported_universe_id, evaluation_period_start,
                evaluation_period_end, evidence_available, evidence_load_status,
                limitations_json, mlflow_run_id, mlflow_model_uri,
                sqlite_catalogue_revision, mlflow_registry_revision,
                registry_sync_status, registry_conflict_reason, created_at, updated_at
            ) VALUES (
                :model_id, :model_version, :model_name, :description, :status, :model_origin,
                :public_demo_eligible, :supported_universe_id, :evaluation_period_start,
                :evaluation_period_end, :evidence_available, :evidence_load_status,
                :limitations_json, :mlflow_run_id, :mlflow_model_uri,
                :sqlite_catalogue_revision, :mlflow_registry_revision,
                :registry_sync_status, :registry_conflict_reason, :created_at, :updated_at
            )
            """,
            payload,
        )

    def get_model(self, model_id: str, model_version: str | None = None) -> dict[str, Any] | None:
        if model_version:
            row = self.conn.execute(
                "SELECT * FROM model_catalogue WHERE model_id=? AND model_version=?",
                (model_id, model_version),
            ).fetchone()
        else:
            row = self.conn.execute(
                "SELECT * FROM model_catalogue WHERE model_id=? ORDER BY updated_at DESC LIMIT 1",
                (model_id,),
            ).fetchone()
        return self._model_from_row(row)

    def list_models(self, runtime_context: str = "local") -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM model_catalogue WHERE status='approved' ORDER BY model_name"
        ).fetchall()
        models = [self._model_from_row(row) for row in rows]
        models = [m for m in models if m and m["registry_sync_status"] == "current"]
        if runtime_context == "public_demo":
            models = [
                m
                for m in models
                if m["model_origin"] == "real" and bool(m["public_demo_eligible"])
            ]
        return models

    def upsert_evidence(self, evidence: dict[str, Any]) -> None:
        payload = {
            **evidence,
            "key_metrics_json": _json(evidence.get("key_metrics", [])),
            "supported_universe_json": _json(evidence.get("supported_universe", [])),
            "known_limitations_json": _json(evidence.get("limitations", [])),
            "data_quality_notes_json": _json(evidence.get("data_quality_notes", [])),
        }
        self.conn.execute(
            """
            INSERT OR REPLACE INTO model_evidence (
                evidence_id, model_id, model_version, evidence_type,
                evaluation_period_start, evaluation_period_end, key_metrics_json,
                performance_summary, supported_universe_json, known_limitations_json,
                data_quality_notes_json, historical_performance_caveat, evidence_status,
                evidence_load_status, evidence_as_of, data_source_mode, paper_trading_summary
            ) VALUES (
                :evidence_id, :model_id, :model_version, :evidence_type,
                :evaluation_period_start, :evaluation_period_end, :key_metrics_json,
                :performance_summary, :supported_universe_json, :known_limitations_json,
                :data_quality_notes_json, :historical_performance_caveat, :evidence_status,
                :evidence_load_status, :evidence_as_of, :data_source_mode, :paper_trading_summary
            )
            """,
            payload,
        )

    def get_evidence(self, model_id: str, model_version: str, evidence_type: str | None = None) -> dict[str, Any] | None:
        if evidence_type:
            row = self.conn.execute(
                """
                SELECT * FROM model_evidence
                WHERE model_id=? AND model_version=? AND evidence_type=?
                ORDER BY evidence_as_of DESC LIMIT 1
                """,
                (model_id, model_version, evidence_type),
            ).fetchone()
        else:
            row = self.conn.execute(
                """
                SELECT * FROM model_evidence
                WHERE model_id=? AND model_version=? AND evidence_type!='paper_trading'
                ORDER BY evidence_as_of DESC LIMIT 1
                """,
                (model_id, model_version),
            ).fetchone()
        return self._evidence_from_row(row)

    def list_evidence(self, model_id: str, model_version: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM model_evidence WHERE model_id=? AND model_version=? ORDER BY evidence_type",
            (model_id, model_version),
        ).fetchall()
        return [self._evidence_from_row(row) for row in rows]

    def upsert_stock(self, stock: dict[str, Any]) -> None:
        payload = {**stock, "market_data_flags_json": _json(stock.get("market_data_flags", []))}
        self.conn.execute(
            """
            INSERT OR REPLACE INTO supported_stocks (
                ticker, name, exchange, universe_id, support_status,
                unavailable_reason, data_as_of, freshness_status, market_data_flags_json
            ) VALUES (
                :ticker, :name, :exchange, :universe_id, :support_status,
                :unavailable_reason, :data_as_of, :freshness_status, :market_data_flags_json
            )
            """,
            payload,
        )

    def search_stocks(self, universe_id: str, query: str = "") -> list[dict[str, Any]]:
        like = f"%{query.upper()}%"
        rows = self.conn.execute(
            """
            SELECT * FROM supported_stocks
            WHERE universe_id=? AND (UPPER(ticker) LIKE ? OR UPPER(name) LIKE ?)
            ORDER BY support_status, ticker
            """,
            (universe_id, like, like),
        ).fetchall()
        return [self._stock_from_row(row) for row in rows]

    def get_stock(self, universe_id: str, ticker: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM supported_stocks WHERE universe_id=? AND UPPER(ticker)=UPPER(?)",
            (universe_id, ticker),
        ).fetchone()
        return self._stock_from_row(row)

    def upsert_data_availability(self, state: dict[str, Any]) -> None:
        payload = {**state, "quality_flags_json": _json(state.get("quality_flags", []))}
        self.conn.execute(
            """
            INSERT OR REPLACE INTO data_availability (
                model_id, ticker, required_period_start, required_period_end, data_as_of,
                feature_generation_timestamp, freshness_status, chronology_status,
                quality_flags_json, blocking_reason
            ) VALUES (
                :model_id, :ticker, :required_period_start, :required_period_end, :data_as_of,
                :feature_generation_timestamp, :freshness_status, :chronology_status,
                :quality_flags_json, :blocking_reason
            )
            """,
            payload,
        )

    def get_data_availability(self, model_id: str, ticker: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM data_availability WHERE model_id=? AND UPPER(ticker)=UPPER(?)",
            (model_id, ticker),
        ).fetchone()
        if row is None:
            return None
        data = dict(row)
        data["quality_flags"] = _loads(data.pop("quality_flags_json"), [])
        return data

    def upsert_disclaimer(self, disclaimer: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO disclaimers
            (disclaimer_id, version, text, placement, effective_date)
            VALUES (:disclaimer_id, :version, :text, :placement, :effective_date)
            """,
            disclaimer,
        )

    def get_active_disclaimer(self) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM disclaimers ORDER BY effective_date DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    def log_prediction(self, record: dict[str, Any]) -> str:
        log_id = record.get("log_id", str(uuid4()))
        payload = {
            **record,
            "log_id": log_id,
            "tickers_json": _json(record.get("tickers", [])),
            "prediction_output_json": _json(record.get("prediction_output")) if record.get("prediction_output") is not None else None,
        }
        self.conn.execute(
            """
            INSERT INTO prediction_logs (
                log_id, request_id, prediction_id, model_id, model_version, tickers_json,
                data_as_of_timestamp, feature_generation_timestamp, prediction_timestamp,
                prediction_output_json, confidence, disclaimer_version, status,
                error_message, runtime_context
            ) VALUES (
                :log_id, :request_id, :prediction_id, :model_id, :model_version, :tickers_json,
                :data_as_of_timestamp, :feature_generation_timestamp, :prediction_timestamp,
                :prediction_output_json, :confidence, :disclaimer_version, :status,
                :error_message, :runtime_context
            )
            """,
            payload,
        )
        return log_id

    def list_prediction_logs(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM prediction_logs ORDER BY prediction_timestamp").fetchall()
        out = []
        for row in rows:
            data = dict(row)
            data["tickers"] = _loads(data.pop("tickers_json"), [])
            data["prediction_output"] = _loads(data.pop("prediction_output_json"), None)
            out.append(data)
        return out

    def record_unsupported_interest(self, ticker: str, reason: str, model_id: str | None = None) -> None:
        now = utc_now_iso()
        self.conn.execute(
            """
            INSERT INTO unsupported_stock_interest
            (ticker, model_id, reason, count, first_seen_at, last_seen_at)
            VALUES (?, ?, ?, 1, ?, ?)
            ON CONFLICT(ticker, model_id, reason)
            DO UPDATE SET count=count+1, last_seen_at=excluded.last_seen_at
            """,
            (ticker.upper(), model_id, reason, now, now),
        )

    def get_unsupported_interest(self, ticker: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM unsupported_stock_interest WHERE UPPER(ticker)=UPPER(?)",
            (ticker,),
        ).fetchone()
        return dict(row) if row else None

    def record_registry_conflict(self, conflict: dict[str, Any]) -> str:
        conflict_id = conflict.get("conflict_id", str(uuid4()))
        payload = {**conflict, "conflict_id": conflict_id, "detected_at": conflict.get("detected_at", utc_now_iso())}
        self.conn.execute(
            """
            INSERT OR REPLACE INTO registry_conflicts
            (conflict_id, model_id, model_version, conflict_type, sqlite_value, mlflow_value,
             detected_at, resolution_status, user_message)
            VALUES (:conflict_id, :model_id, :model_version, :conflict_type, :sqlite_value, :mlflow_value,
                    :detected_at, :resolution_status, :user_message)
            """,
            payload,
        )
        return conflict_id

    def list_open_registry_conflicts(self, model_id: str | None = None) -> list[dict[str, Any]]:
        if model_id:
            rows = self.conn.execute(
                "SELECT * FROM registry_conflicts WHERE model_id=? AND resolution_status='open'",
                (model_id,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM registry_conflicts WHERE resolution_status='open'"
            ).fetchall()
        return [dict(row) for row in rows]

    def upsert_deployable_asset(self, asset: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO deployable_data_assets
            (asset_id, asset_type, classification, data_as_of, limitations, approval_reference)
            VALUES (:asset_id, :asset_type, :classification, :data_as_of, :limitations, :approval_reference)
            """,
            asset,
        )

    def list_public_demo_assets(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM deployable_data_assets WHERE classification='public_demo_allowed'"
        ).fetchall()
        return [dict(row) for row in rows]

    def _model_from_row(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        data = dict(row)
        data["public_demo_eligible"] = bool(data["public_demo_eligible"])
        data["evidence_available"] = bool(data["evidence_available"])
        data["limitations"] = _loads(data.pop("limitations_json"), [])
        return data

    def _evidence_from_row(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        data = dict(row)
        data["key_metrics"] = _loads(data.pop("key_metrics_json"), [])
        data["supported_universe"] = _loads(data.pop("supported_universe_json"), [])
        data["limitations"] = _loads(data.pop("known_limitations_json"), [])
        data["data_quality_notes"] = _loads(data.pop("data_quality_notes_json"), [])
        return data

    def _stock_from_row(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        data = dict(row)
        data["market_data_flags"] = _loads(data.pop("market_data_flags_json"), [])
        return data

