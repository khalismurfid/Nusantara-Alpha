"""Small HTTP client used by Streamlit presentation code."""

from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class APIClient:
    base_url: str
    timeout_seconds: int = 10
    transient_retry_attempts: int = 5
    retry_delay_seconds: float = 0.5

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
                "target": "near_term_barrier_signal",
            },
        )

    def get_rankings(self, model_id: str, model_version: str) -> dict[str, Any]:
        return self._get(f"/models/{model_id}/rankings?model_version={model_version}")

    def _get(self, path: str) -> dict[str, Any]:
        with self._open_with_transient_dns_retry(f"{self.base_url}{path}") as response:
            return json.loads(response.read().decode("utf-8"))

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._open_with_transient_dns_retry(request) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            return json.loads(body) if body else {"error_code": str(exc.code), "message": exc.reason}

    def _open_with_transient_dns_retry(self, request_or_url):
        for attempt in range(self.transient_retry_attempts):
            try:
                return urlopen(request_or_url, timeout=self.timeout_seconds)
            except HTTPError:
                raise
            except URLError as exc:
                if not self._is_transient_dns_error(exc) or attempt == self.transient_retry_attempts - 1:
                    raise
                time.sleep(self.retry_delay_seconds)
        raise RuntimeError("unreachable retry loop")

    @staticmethod
    def _is_transient_dns_error(exc: URLError) -> bool:
        reason = exc.reason
        return isinstance(reason, socket.gaierror) and reason.errno == socket.EAI_AGAIN
