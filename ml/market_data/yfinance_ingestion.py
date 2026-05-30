"""yfinance ingestion helpers for approved IDX market data."""

from __future__ import annotations

import csv
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from storage.repositories import Repository


def idx_to_yahoo_symbol(ticker: str) -> str:
    normalized = ticker.strip().upper()
    return normalized if normalized.endswith(".JK") else f"{normalized}.JK"


def yahoo_to_idx_ticker(symbol: str) -> str:
    return symbol.strip().upper().removesuffix(".JK")


def load_universe_csv(path: str | Path, source: str, source_date: str | None = None) -> list[dict[str, Any]]:
    records = []
    with Path(path).open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ticker = (row.get("ticker") or row.get("code") or "").strip().upper()
            if not ticker:
                continue
            records.append(
                {
                    "ticker": ticker,
                    "company_name": (row.get("company_name") or row.get("name") or ticker).strip(),
                    "yahoo_symbol": (row.get("yahoo_symbol") or idx_to_yahoo_symbol(ticker)).strip().upper(),
                    "active": str(row.get("active", "1")).strip().lower() not in {"0", "false", "no"},
                    "source": source,
                    "source_date": source_date or date.today().isoformat(),
                }
            )
    return records


def fetch_yfinance_ohlcv(symbols: Iterable[str], start: str, end: str | None = None) -> pd.DataFrame:
    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover - exercised only when dependency is absent.
        raise RuntimeError("yfinance is required for live market-data ingestion.") from exc
    return yf.download(
        list(symbols),
        start=start,
        end=end,
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        repair=True,
        threads=True,
        progress=False,
    )


def normalize_yfinance_frame(frame: pd.DataFrame, symbols: list[str], fetched_at: str | None = None) -> list[dict[str, Any]]:
    fetched_at = fetched_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows: list[dict[str, Any]] = []
    for symbol in symbols:
        if isinstance(frame.columns, pd.MultiIndex):
            if symbol not in frame.columns.get_level_values(0):
                continue
            symbol_frame = frame[symbol].copy()
        else:
            symbol_frame = frame.copy()
        symbol_frame = symbol_frame.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )
        if not all(required in symbol_frame for required in ["open", "high", "low", "close", "volume"]):
            continue
        for price_date, values in symbol_frame.dropna(subset=["open", "high", "low", "close"]).iterrows():
            rows.append(
                {
                    "ticker": yahoo_to_idx_ticker(symbol),
                    "price_date": price_date.date().isoformat(),
                    "open": float(values["open"]),
                    "high": float(values["high"]),
                    "low": float(values["low"]),
                    "close": float(values["close"]),
                    "adj_close": float(values["adj_close"]) if "adj_close" in values and pd.notna(values["adj_close"]) else None,
                    "volume": float(values["volume"]) if pd.notna(values["volume"]) else 0.0,
                    "source": "yfinance",
                    "fetched_at": fetched_at,
                }
            )
    return rows


def ingest_yfinance_to_repository(
    repo: Repository,
    universe: list[dict[str, Any]],
    start: str,
    end: str | None = None,
    model_id: str | None = None,
    universe_id: str | None = None,
) -> dict[str, Any]:
    for record in universe:
        repo.upsert_idx_universe(record)
    symbols = [record["yahoo_symbol"] for record in universe if record.get("active", True)]
    frame = fetch_yfinance_ohlcv(symbols, start=start, end=end)
    rows = normalize_yfinance_frame(frame, symbols)
    repo.upsert_market_prices(rows)
    latest_by_ticker = {}
    for row in rows:
        latest_by_ticker[row["ticker"]] = max(row["price_date"], latest_by_ticker.get(row["ticker"], ""))
    if universe_id:
        for record in universe:
            ticker = record["ticker"]
            latest = latest_by_ticker.get(ticker)
            repo.upsert_stock(
                {
                    "ticker": ticker,
                    "name": record["company_name"],
                    "exchange": "IDX",
                    "universe_id": universe_id,
                    "support_status": "supported" if latest else "temporarily_unavailable",
                    "unavailable_reason": None if latest else "No usable yfinance OHLCV rows were downloaded for this ticker.",
                    "data_as_of": f"{latest}T00:00:00+00:00" if latest else None,
                    "freshness_status": "fresh" if latest else "missing",
                    "market_data_flags": [] if latest else ["missing_yfinance_rows"],
                }
            )
            if model_id:
                repo.upsert_data_availability(
                    {
                        "model_id": model_id,
                        "ticker": ticker,
                        "required_period_start": start,
                        "required_period_end": latest,
                        "data_as_of": f"{latest}T00:00:00+00:00" if latest else None,
                        "feature_generation_timestamp": f"{latest}T00:00:00+00:00" if latest else None,
                        "freshness_status": "fresh" if latest else "missing",
                        "chronology_status": "valid",
                        "quality_flags": [] if latest else ["missing_yfinance_rows"],
                        "blocking_reason": None if latest else "missing_data",
                    }
                )
    return {
        "requested_symbols": len(symbols),
        "stored_rows": len(rows),
        "latest_price_date": repo.latest_market_price_date(),
    }
