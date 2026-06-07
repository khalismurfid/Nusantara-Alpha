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
            "idx-approved-universe",
        ]
    )

    assert args.universe == Path("data/approved_idx_universe.csv")
    assert args.source == "approved-public-idx-list"
    assert args.start == "2018-01-01"
    assert args.model_id == "idx-direction-baseline"
    assert args.universe_id == "idx-approved-universe"
    assert not args.refresh_baseline_artifact


def test_yfinance_ingestion_cli_can_request_baseline_artifact_refresh(tmp_path):
    artifact_path = tmp_path / "model.joblib"

    args = build_parser().parse_args(
        [
            "--universe",
            "data/approved_idx_universe.csv",
            "--source",
            "approved-public-idx-list",
            "--start",
            "2018-01-01",
            "--refresh-baseline-artifact",
            "--artifact-path",
            str(artifact_path),
        ]
    )

    assert args.refresh_baseline_artifact
    assert args.artifact_path == artifact_path
