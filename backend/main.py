"""FastAPI application construction."""

from __future__ import annotations

from backend.routers import demo, evidence, health, models, predictions, rankings, stocks, unsupported_stock_interest

try:
    from fastapi import FastAPI  # type: ignore
except Exception:
    FastAPI = None  # type: ignore


def create_app():
    if FastAPI is None:
        return {
            "title": "Nusantara Alpha API",
            "routers": [health.router, demo.router, models.router, evidence.router, stocks.router, unsupported_stock_interest.router, predictions.router, rankings.router],
        }
    app = FastAPI(title="Nusantara Alpha API", version="0.1.0")
    for router in [health.router, demo.router, models.router, evidence.router, stocks.router, unsupported_stock_interest.router, predictions.router, rankings.router]:
        app.include_router(router)
    return app


app = create_app()
