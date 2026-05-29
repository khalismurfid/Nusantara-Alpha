"""Small HTTP client used by Streamlit presentation code."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@dataclass
class APIClient:
    base_url: str

    def get_health(self) -> dict[str, Any]:
        return self._get("/health")

    def get_demo_status(self) -> dict[str, Any]:
        return self._get("/demo/status")

    def list_models(self) -> dict[str, Any]:
        return self._get("/models")

    def get_evidence(self, model_id: str) -> dict[str, Any]:
        return self._get(f"/models/{model_id}/evidence")

    def list_stocks(self, model_id: str, query: str = "") -> dict[str, Any]:
        suffix = f"?query={query}" if query else ""
        return self._get(f"/models/{model_id}/stocks{suffix}")

    def record_unsupported_stock_interest(self, ticker: str, reason: str, model_id: str | None = None) -> dict[str, Any]:
        payload = {"ticker": ticker, "reason": reason, "model_id": model_id}
        return self._post("/unsupported-stock-interest", payload)

    def request_prediction(self, model_id: str, model_version: str, tickers: list[str]) -> dict[str, Any]:
        return self._post(
            "/predictions",
            {
                "model_id": model_id,
                "model_version": model_version,
                "tickers": tickers,
                "target": "next_market_session_direction",
            },
        )

    def _get(self, path: str) -> dict[str, Any]:
        with urlopen(f"{self.base_url}{path}", timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            return json.loads(body) if body else {"error_code": str(exc.code), "message": exc.reason}

