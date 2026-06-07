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


def fetch_yfinance_ohlcv(
    symbols: Iterable[str],
    start: str,
    end: str | None = None,
    chunk_size: int = 80,
) -> pd.DataFrame:
    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover - exercised only when dependency is absent.
        raise RuntimeError("yfinance is required for live market-data ingestion.") from exc
    requested = list(symbols)
    frames = []
    for chunk in _chunks(requested, max(1, chunk_size)):
        frame = yf.download(
            chunk,
            start=start,
            end=end,
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            repair=True,
            threads=True,
            progress=False,
        )
        if frame.empty:
            continue
        frames.append(_ensure_symbol_column(frame, chunk))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1).sort_index(axis=1)


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


def _chunks(items: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def _ensure_symbol_column(frame: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        return frame
    if len(symbols) == 1:
        return pd.concat({symbols[0]: frame}, axis=1)
    return frame


def ingest_yfinance_to_repository(
    repo: Repository,
    universe: list[dict[str, Any]],
    start: str,
    end: str | None = None,
    model_id: str | None = None,
    universe_id: str | None = None,
    chunk_size: int = 80,
    min_usable_rows: int = 60,
) -> dict[str, Any]:
    for record in universe:
        repo.upsert_idx_universe(record)
    symbols = [record["yahoo_symbol"] for record in universe if record.get("active", True)]
    frame = fetch_yfinance_ohlcv(symbols, start=start, end=end, chunk_size=chunk_size)
    rows = normalize_yfinance_frame(frame, symbols)
    repo.upsert_market_prices(rows)
    latest_by_ticker = {}
    count_by_ticker = {}
    for row in rows:
        latest_by_ticker[row["ticker"]] = max(row["price_date"], latest_by_ticker.get(row["ticker"], ""))
        count_by_ticker[row["ticker"]] = count_by_ticker.get(row["ticker"], 0) + 1
    if universe_id:
        for record in universe:
            ticker = record["ticker"]
            latest = latest_by_ticker.get(ticker)
            row_count = count_by_ticker.get(ticker, 0)
            support_status = "supported" if latest and row_count >= min_usable_rows else "temporarily_unavailable"
            unavailable_reason = None
            quality_flags = []
            blocking_reason = None
            if not latest:
                unavailable_reason = "No usable yfinance OHLCV rows were downloaded for this ticker."
                quality_flags = ["missing_yfinance_rows"]
                blocking_reason = "missing_data"
            elif row_count < min_usable_rows:
                unavailable_reason = f"Only {row_count} usable OHLCV rows were downloaded; this model requires at least {min_usable_rows} rows."
                quality_flags = ["insufficient_history"]
                blocking_reason = "insufficient_history"
            repo.upsert_stock(
                {
                    "ticker": ticker,
                    "name": record["company_name"],
                    "exchange": "IDX",
                    "universe_id": universe_id,
                    "support_status": support_status,
                    "unavailable_reason": unavailable_reason,
                    "data_as_of": f"{latest}T00:00:00+00:00" if latest else None,
                    "freshness_status": "fresh" if latest and row_count >= min_usable_rows else "missing",
                    "market_data_flags": quality_flags,
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
                        "freshness_status": "fresh" if latest and row_count >= min_usable_rows else "missing",
                        "chronology_status": "valid",
                        "quality_flags": quality_flags,
                        "blocking_reason": blocking_reason,
                    }
                )
    return {
        "requested_symbols": len(symbols),
        "stored_rows": len(rows),
        "supported_tickers": sum(1 for count in count_by_ticker.values() if count >= min_usable_rows),
        "unavailable_tickers": max(0, len(symbols) - sum(1 for count in count_by_ticker.values() if count >= min_usable_rows)),
        "latest_price_date": repo.latest_market_price_date(),
    }
