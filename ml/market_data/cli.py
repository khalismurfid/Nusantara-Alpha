"""Command-line utilities for approved IDX market-data ingestion."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from ml.market_data.yfinance_ingestion import ingest_yfinance_to_repository, load_universe_csv
from storage.database import connect, initialize
from storage.repositories import Repository
from storage.seed_local_demo import BASELINE_ARTIFACT_PATH, refresh_baseline_artifact, refresh_baseline_evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nusantara-ingest-yfinance",
        description="Fetch approved IDX .JK OHLCV rows from yfinance and store them in SQLite.",
    )
    parser.add_argument("--universe", required=True, type=Path, help="CSV with ticker/code, company_name/name, and optional yahoo_symbol columns.")
    parser.add_argument("--source", required=True, help="Human-readable source name for the approved universe list.")
    parser.add_argument("--source-date", help="Date of the approved universe source, as YYYY-MM-DD.")
    parser.add_argument("--start", required=True, help="First yfinance date to fetch, as YYYY-MM-DD.")
    parser.add_argument("--end", help="Exclusive yfinance end date, as YYYY-MM-DD.")
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=Path(os.getenv("NUSANTARA_SQLITE_PATH", "./.local/nusantara_alpha.sqlite3")),
        help="SQLite database path. Defaults to NUSANTARA_SQLITE_PATH or ./.local/nusantara_alpha.sqlite3.",
    )
    parser.add_argument("--model-id", help="Optional model id whose data availability should be refreshed.")
    parser.add_argument("--universe-id", help="Optional supported-stock universe id to sync after ingestion.")
    parser.add_argument("--chunk-size", type=int, default=80, help="Number of yfinance symbols to fetch per request batch.")
    parser.add_argument(
        "--min-usable-rows",
        type=int,
        default=60,
        help="Minimum downloaded OHLCV rows required before a ticker is marked supported.",
    )
    parser.add_argument(
        "--refresh-baseline-artifact",
        action="store_true",
        help="Retrain and save the local logistic regression artifact from the ingested approved rows.",
    )
    parser.add_argument(
        "--artifact-path",
        type=Path,
        default=BASELINE_ARTIFACT_PATH,
        help="Where to save the refreshed baseline artifact when --refresh-baseline-artifact is used.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    universe = load_universe_csv(args.universe, source=args.source, source_date=args.source_date)
    conn = connect(args.sqlite_path)
    try:
        initialize(conn)
        result = ingest_yfinance_to_repository(
            Repository(conn),
            universe=universe,
            start=args.start,
            end=args.end,
            model_id=args.model_id,
            universe_id=args.universe_id,
            chunk_size=args.chunk_size,
            min_usable_rows=args.min_usable_rows,
        )
        if args.refresh_baseline_artifact:
            refreshed = refresh_baseline_artifact(Repository(conn), args.artifact_path)
            result["refreshed_artifact_path"] = str(args.artifact_path)
            result["refreshed_model_tickers"] = len(refreshed.trained_tickers)
            result["refreshed_training_rows"] = refreshed.training_rows
            result["refreshed_evidence"] = refresh_baseline_evidence(
                Repository(conn),
                f"{args.source} yfinance OHLCV",
            )
        conn.commit()
    finally:
        conn.close()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
