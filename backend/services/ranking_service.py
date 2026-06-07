"""Model ranking service for the current approved IDX universe."""

from __future__ import annotations

from datetime import datetime, timezone

from app_streamlit.copy.disclaimers import EDUCATIONAL_DISCLAIMER
from backend.schemas.contracts import RankingItem, RankingResponse
from backend.services.evidence_service import EvidenceService, EvidenceUnavailableError
from ml.backtesting.realistic import fit_pooled_logistic_model, predict_scores
from ml.features.generation import generate_features
from model_registry.approval import reconcile_model
from storage.repositories import Repository


class RankingService:
    def __init__(self, repo: Repository, runtime_context: str = "local"):
        self.repo = repo
        self.runtime_context = runtime_context
        self.evidence_service = EvidenceService(repo)

    def get_rankings(self, model_id: str, model_version: str) -> dict:
        generated_at = datetime.now(timezone.utc).replace(microsecond=0)
        model = self.repo.get_model(model_id, model_version)
        if not model:
            return self._empty(model_id, model_version, generated_at)
        approval = reconcile_model(model, None, self.runtime_context)
        if not approval.prediction_allowed:
            return self._empty(model_id, model_version, generated_at)
        try:
            self.evidence_service.require_loaded_evidence(model_id, model_version)
        except EvidenceUnavailableError:
            return self._empty(model_id, model_version, generated_at)
        price_rows = self.repo.list_market_prices()
        try:
            pooled = fit_pooled_logistic_model(price_rows)
        except ValueError:
            return self._empty(model_id, model_version, generated_at)
        scores = predict_scores(pooled)
        stocks = {
            stock["ticker"]: stock
            for stock in self.repo.search_stocks(model["supported_universe_id"])
            if stock["support_status"] == "supported"
        }
        rankings = []
        for _, row in scores.iterrows():
            ticker = str(row["ticker"])
            if ticker not in stocks:
                continue
            feature_payload = generate_features(
                ticker,
                datetime.combine(row["price_date"].date(), datetime.min.time(), tzinfo=timezone.utc),
                generated_at,
            )
            rankings.append(
                RankingItem(
                    ticker=ticker,
                    name=stocks[ticker].get("name"),
                    rank=int(row["rank"]),
                    model_signal=str(row["model_signal"]),
                    confidence_category=str(row["confidence_category"]),
                    ranking_score=round(float(row["ranking_score"]), 4),
                    data_as_of_timestamp=feature_payload.data_as_of_timestamp,
                    feature_generation_timestamp=feature_payload.feature_generation_timestamp,
                    context_summary=f"Ranked {int(row['rank'])} of {len(scores)} by upside barrier probability.",
                )
            )
        data_as_of = rankings[0].data_as_of_timestamp if rankings else generated_at
        return RankingResponse(
            model_id=model_id,
            model_version=model_version,
            generated_at=generated_at,
            data_as_of_timestamp=data_as_of,
            rankings=rankings,
            disclaimer=EDUCATIONAL_DISCLAIMER,
        ).model_dump(mode="json")

    def _empty(self, model_id: str, model_version: str, generated_at: datetime) -> dict:
        return RankingResponse(
            model_id=model_id,
            model_version=model_version,
            generated_at=generated_at,
            data_as_of_timestamp=generated_at,
            rankings=[],
            disclaimer=EDUCATIONAL_DISCLAIMER,
        ).model_dump(mode="json")
