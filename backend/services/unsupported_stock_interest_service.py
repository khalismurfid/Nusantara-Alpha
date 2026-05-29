"""Aggregate unsupported-stock interest service."""

from __future__ import annotations

from backend.schemas.contracts import UnsupportedStockInterestResponse
from storage.repositories import Repository


class UnsupportedStockInterestService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def record(self, ticker: str, reason: str, model_id: str | None = None) -> dict:
        self.repo.record_unsupported_interest(ticker, reason, model_id)
        return UnsupportedStockInterestResponse(
            accepted=True,
            message="Unsupported-stock interest recorded as aggregate non-personal product feedback.",
        ).model_dump(mode="json")

