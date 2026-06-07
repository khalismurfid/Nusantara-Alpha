"""Prediction orchestration service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app_streamlit.copy.disclaimers import DISCLAIMER_VERSION, EDUCATIONAL_DISCLAIMER, assert_copy_safe
from backend.schemas.contracts import BlockedPrediction, PredictionOutput, PredictionRequest, PredictionResponse
from backend.services.evidence_service import EvidenceService, EvidenceUnavailableError
from backend.services.prediction_logging_service import PredictionLoggingService
from backend.services.stock_service import StockService

from ml.backtesting.realistic import fit_pooled_logistic_model, load_pooled_model
from ml.features.generation import generate_features
from ml.loading.model_loader import LoadedModel, load_model
from ml.prediction.engine import EnginePrediction, predict_next_session
from ml.validation.chronology import parse_datetime, validate_prediction_timestamps
from ml.validation.market_data import assess_market_data
from model_registry.approval import reconcile_model
from model_registry.conflict_log import log_conflict
from storage.repositories import Repository

CANONICAL_PREDICTION_TARGET = "near_term_barrier_signal"


class PredictionService:
    def __init__(self, repo: Repository, runtime_context: str = "local"):
        self.repo = repo
        self.runtime_context = runtime_context
        self.evidence_service = EvidenceService(repo)
        self.stock_service = StockService(repo)
        self.logging_service = PredictionLoggingService(repo)
        self._pooled_model_cache = {}

    def request_prediction(self, request: PredictionRequest) -> dict:
        request_id = str(uuid4())
        prediction_timestamp = datetime.now(timezone.utc).replace(microsecond=0)
        model = self.repo.get_model(request.model_id, request.model_version)
        if not model:
            return self._blocked_response(request_id, request, "unavailable_model", "The selected model is unavailable.", prediction_timestamp)
        approval = reconcile_model(model, None, self.runtime_context)
        if not approval.prediction_allowed:
            if approval.conflict_type:
                log_conflict(
                    self.repo,
                    model["model_id"],
                    model["model_version"],
                    approval.conflict_type,
                    "sqlite",
                    "mlflow",
                    approval.user_message or "Model unavailable.",
                )
            reason = self._approval_reason_to_blocked_reason(approval.reason)
            return self._blocked_response(request_id, request, reason, approval.user_message or "The selected model is unavailable.", prediction_timestamp)
        if self.runtime_context == "public_demo" and model["model_origin"] != "real":
            return self._blocked_response(request_id, request, "mock_model_blocked_in_public_demo", "Public demo predictions require a real approved model.", prediction_timestamp)
        try:
            evidence = self.evidence_service.require_loaded_evidence(request.model_id, request.model_version)
        except EvidenceUnavailableError as exc:
            return self._blocked_response(request_id, request, exc.reason, exc.message, prediction_timestamp)

        outputs = []
        blocked = []
        for ticker in request.tickers:
            stock = self.stock_service.get_supported_stock(model, ticker)
            if not stock:
                self.repo.record_unsupported_interest(ticker, "unsupported_for_selected_model", model["model_id"])
                blocked.append(self._blocked(ticker, "unsupported_stock", f"This model has not been reviewed for {ticker.upper()} yet.", "Choose one of the supported tickers for this model."))
                continue
            data_state = self.repo.get_data_availability(model["model_id"], ticker)
            if not data_state:
                blocked.append(self._blocked(ticker, "missing_data", "The latest required data is not available for this ticker yet.", "Choose another supported ticker or try again after data is refreshed."))
                continue
            if data_state.get("chronology_status") != "valid":
                blocked.append(self._blocked(ticker, "chronology_violation", "This output is paused because the available data cannot be matched safely to the prediction time.", "Use data available at or before the prediction time."))
                continue
            if not data_state.get("feature_generation_timestamp"):
                blocked.append(self._blocked(ticker, "missing_feature_timestamp", "The feature timestamp is missing, so this prediction cannot be traced safely.", "Regenerate features with valid timestamps."))
                continue
            market = assess_market_data(data_state.get("freshness_status"), data_state.get("quality_flags"))
            if not market.allowed:
                blocked.append(self._blocked(ticker, market.blocking_reason or "unreliable_or_untraceable", "Required market data cannot support a reliable or traceable output.", "Review data availability or choose another ticker."))
                continue
            data_as_of = parse_datetime(data_state.get("data_as_of"))
            if data_as_of is None:
                blocked.append(self._blocked(ticker, "missing_data", "The data timestamp is missing, so this prediction cannot be traced safely.", "Review data availability."))
                continue
            state_feature_ts = parse_datetime(data_state.get("feature_generation_timestamp"))
            feature_payload = generate_features(ticker, data_as_of, state_feature_ts)
            chronology = validate_prediction_timestamps(
                data_as_of,
                feature_payload.feature_generation_timestamp,
                prediction_timestamp,
            )
            if not chronology.valid:
                reason = "missing_feature_timestamp" if chronology.reason == "missing_feature_timestamp" else "invalid_feature_timestamp"
                blocked.append(self._blocked(ticker, reason, "Feature timing is missing or later than the prediction time.", "Regenerate features with valid timestamps."))
                continue
            try:
                engine_prediction = self._invoke_prediction(model, ticker, feature_payload, evidence)
                output = self._build_output(
                    request_id,
                    ticker,
                    self._canonical_target(request.target),
                    model,
                    evidence,
                    engine_prediction,
                    data_as_of,
                    feature_payload.feature_generation_timestamp,
                    prediction_timestamp,
                )
                assert_copy_safe(str(output.model_dump()))
                outputs.append(output)
                self.logging_service.log(
                    {
                        "request_id": request_id,
                        "prediction_id": output.prediction_id,
                        "model_id": model["model_id"],
                        "model_version": model["model_version"],
                        "tickers": [ticker.upper()],
                        "data_as_of_timestamp": output.data_as_of_timestamp.isoformat(),
                        "feature_generation_timestamp": output.feature_generation_timestamp.isoformat(),
                        "prediction_timestamp": output.prediction_timestamp.isoformat(),
                        "prediction_output": output.model_dump(mode="json"),
                        "confidence": output.confidence_category,
                        "disclaimer_version": DISCLAIMER_VERSION,
                        "status": "success",
                        "error_message": None,
                        "runtime_context": self.runtime_context,
                    }
                )
            except Exception as exc:
                blocked.append(self._blocked(ticker, "invalid_prediction_response", "Prediction generation failed or returned an invalid response.", "Try again later or choose another ticker."))
                self.logging_service.log(
                    {
                        "request_id": request_id,
                        "prediction_id": None,
                        "model_id": model["model_id"],
                        "model_version": model["model_version"],
                        "tickers": [ticker.upper()],
                        "data_as_of_timestamp": data_as_of.isoformat(),
                        "feature_generation_timestamp": feature_payload.feature_generation_timestamp.isoformat(),
                        "prediction_timestamp": prediction_timestamp.isoformat(),
                        "prediction_output": None,
                        "confidence": None,
                        "disclaimer_version": DISCLAIMER_VERSION,
                        "status": "failed",
                        "error_message": str(exc),
                        "runtime_context": self.runtime_context,
                    }
                )
        response = PredictionResponse(
            request_id=request_id,
            predictions=outputs,
            blocked=blocked,
            disclaimer=EDUCATIONAL_DISCLAIMER,
        )
        return response.model_dump(mode="json")

    def _invoke_prediction(self, model: dict, ticker: str, feature_payload, evidence: dict) -> EnginePrediction:
        loaded = load_model(model)
        pooled = self._load_pooled_model(model)
        loaded = LoadedModel(
            model_id=loaded.model_id,
            model_version=loaded.model_version,
            model_name=loaded.model_name,
            artifact_uri=loaded.artifact_uri,
            raw=pooled,
        )
        return predict_next_session(loaded, feature_payload, evidence.get("limitations"))

    def _load_pooled_model(self, model: dict):
        cache_key = (model["model_id"], model["model_version"])
        if cache_key not in self._pooled_model_cache:
            artifact = self._load_local_artifact(model)
            if artifact is not None:
                self._pooled_model_cache[cache_key] = artifact
            else:
                supported = self._supported_tickers_for_model(model)
                price_rows = self.repo.list_market_prices(tickers=supported or None)
                self._pooled_model_cache[cache_key] = fit_pooled_logistic_model(price_rows)
        return self._pooled_model_cache[cache_key]

    def _load_local_artifact(self, model: dict):
        uri = model.get("mlflow_model_uri")
        if not uri or not str(uri).startswith("file:"):
            return None
        path = Path(str(uri).removeprefix("file:"))
        if not path.exists():
            return None
        artifact = load_pooled_model(path)
        supported = self._supported_tickers_for_model(model)
        if supported and set(artifact.trained_tickers) != set(supported):
            return None
        return artifact

    def _supported_tickers_for_model(self, model: dict) -> list[str]:
        return [
            stock["ticker"]
            for stock in self.repo.search_stocks(model["supported_universe_id"])
            if stock["support_status"] == "supported"
        ]

    def _build_output(self, request_id: str, ticker: str, target: str, model: dict, evidence: dict, prediction: EnginePrediction, data_as_of: datetime, feature_ts: datetime, prediction_ts: datetime) -> PredictionOutput:
        return PredictionOutput(
            prediction_id=str(uuid4()),
            ticker=ticker.upper(),
            prediction_target=target,
            model_signal=prediction.model_signal,
            confidence_category=prediction.confidence_category,
            numeric_confidence=prediction.numeric_confidence,
            confidence_explanation=prediction.confidence_explanation,
            context_summary=prediction.context_summary,
            limitation_summary=prediction.limitation_summary,
            model_name=model["model_name"],
            model_id=model["model_id"],
            model_version=model["model_version"],
            data_as_of_timestamp=data_as_of,
            feature_generation_timestamp=feature_ts,
            prediction_timestamp=prediction_ts,
            evaluation_context=f"{evidence['evaluation_period_start']} to {evidence['evaluation_period_end']}",
            evidence_reference=evidence["evidence_id"],
            disclaimer_text=EDUCATIONAL_DISCLAIMER,
            disclaimer_version=DISCLAIMER_VERSION,
            rank=prediction.rank,
            rank_universe_size=prediction.rank_universe_size,
            ranking_score=prediction.ranking_score,
        )

    def _blocked_response(self, request_id: str, request: PredictionRequest, reason: str, message: str, prediction_timestamp: datetime) -> dict:
        blocked = [self._blocked(ticker, reason, message, "Review the model, evidence, stock, or data availability state.") for ticker in request.tickers]
        self.logging_service.log(
            {
                "request_id": request_id,
                "prediction_id": None,
                "model_id": request.model_id,
                "model_version": request.model_version,
                "tickers": request.tickers,
                "data_as_of_timestamp": None,
                "feature_generation_timestamp": None,
                "prediction_timestamp": prediction_timestamp.isoformat(),
                "prediction_output": None,
                "confidence": None,
                "disclaimer_version": DISCLAIMER_VERSION,
                "status": "blocked",
                "error_message": message,
                "runtime_context": self.runtime_context,
            }
        )
        return PredictionResponse(request_id=request_id, predictions=[], blocked=blocked, disclaimer=EDUCATIONAL_DISCLAIMER).model_dump(mode="json")

    def _blocked(self, ticker: str, reason: str, message: str, next_step: str | None = None) -> BlockedPrediction:
        return BlockedPrediction(ticker=ticker.upper(), reason=reason, user_message=message, next_step=next_step)

    def _approval_reason_to_blocked_reason(self, reason: str | None) -> str:
        return {
            "registry_conflict": "registry_conflict",
            "sync_stale": "registry_sync_stale",
            "sync_incomplete": "registry_sync_incomplete",
            "public_demo_eligibility": "public_demo_model_unavailable",
            "artifact_uri": "public_demo_release_gate_failed",
        }.get(reason or "", "unavailable_model")

    def _canonical_target(self, target: str) -> str:
        if target == "next_market_session_direction":
            return CANONICAL_PREDICTION_TARGET
        return target
