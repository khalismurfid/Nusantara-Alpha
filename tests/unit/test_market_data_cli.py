from pathlib import Path

from ml.market_data.cli import build_parser


def test_yfinance_ingestion_cli_parses_required_arguments():
    args = build_parser().parse_args(
        [
            "--universe",
            "data/approved_idx_universe.csv",
            "--source",
            "approved-public-idx-list",
            "--start",
            "2018-01-01",
            "--model-id",
            "idx-direction-baseline",
            "--universe-id",
            "idx-liquid-demo",
        ]
    )

    assert args.universe == Path("data/approved_idx_universe.csv")
    assert args.source == "approved-public-idx-list"
    assert args.start == "2018-01-01"
    assert args.model_id == "idx-direction-baseline"
    assert args.universe_id == "idx-liquid-demo"
