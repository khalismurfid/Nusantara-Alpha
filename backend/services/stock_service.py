"""Supported-stock lookup service."""

from __future__ import annotations

from backend.schemas.contracts import StockAvailability
from storage.repositories import Repository


class StockService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def list_stocks(self, model_id: str, model_version: str, query: str = "") -> dict:
        model = self.repo.get_model(model_id, model_version)
        if not model:
            return {"stocks": []}
        stocks = self.repo.search_stocks(model["supported_universe_id"], query)
        if query and not stocks:
            stocks = [
                {
                    "ticker": query.upper(),
                    "name": query.upper(),
                    "exchange": "IDX",
                    "support_status": "unsupported",
                    "unavailable_reason": f"This model has not been reviewed for {query.upper()} yet.",
                    "data_as_of": None,
                    "freshness_status": "missing",
                    "market_data_flags": ["unsupported_universe"],
                }
            ]
        return {"stocks": [StockAvailability(**self._public_stock(stock)).model_dump(mode="json") for stock in stocks]}

    def get_supported_stock(self, model: dict, ticker: str) -> dict | None:
        stock = self.repo.get_stock(model["supported_universe_id"], ticker)
        if not stock or stock["support_status"] != "supported":
            return None
        return stock

    def _public_stock(self, stock: dict) -> dict:
        return {
            key: value
            for key, value in stock.items()
            if key
            in {
                "ticker",
                "name",
                "exchange",
                "support_status",
                "unavailable_reason",
                "data_as_of",
                "freshness_status",
                "market_data_flags",
            }
        }
