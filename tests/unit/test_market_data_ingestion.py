import pandas as pd

from ml.market_data.yfinance_ingestion import idx_to_yahoo_symbol, normalize_yfinance_frame, yahoo_to_idx_ticker


def test_idx_yahoo_symbol_mapping():
    assert idx_to_yahoo_symbol("bbca") == "BBCA.JK"
    assert idx_to_yahoo_symbol("TLKM.JK") == "TLKM.JK"
    assert yahoo_to_idx_ticker("ASII.JK") == "ASII"


def test_yfinance_frame_normalizes_to_market_price_rows():
    dates = pd.to_datetime(["2026-05-27", "2026-05-28"])
    frame = pd.DataFrame(
        {
            ("BBCA.JK", "Open"): [9000, 9050],
            ("BBCA.JK", "High"): [9100, 9125],
            ("BBCA.JK", "Low"): [8950, 9000],
            ("BBCA.JK", "Close"): [9075, 9060],
            ("BBCA.JK", "Adj Close"): [9075, 9060],
            ("BBCA.JK", "Volume"): [1000000, 1100000],
        },
        index=dates,
    )

    rows = normalize_yfinance_frame(frame, ["BBCA.JK"], fetched_at="2026-05-29T09:00:00Z")

    assert rows[0]["ticker"] == "BBCA"
    assert rows[0]["price_date"] == "2026-05-27"
    assert rows[0]["open"] == 9000.0
    assert rows[0]["source"] == "yfinance"
