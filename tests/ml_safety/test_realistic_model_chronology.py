from ml.backtesting.realistic import build_supervised_frame
from storage.seed_local_demo import _sample_market_prices


def test_supervised_target_uses_next_session_open_to_close():
    rows = _sample_market_prices([("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk")])
    supervised = build_supervised_frame(rows)
    sample = supervised[supervised["ticker"] == "BBCA"].iloc[0]
    ticker_rows = [row for row in rows if row["ticker"] == "BBCA"]
    current_index = next(index for index, row in enumerate(ticker_rows) if row["price_date"] == sample["price_date"].date().isoformat())
    next_row = ticker_rows[current_index + 1]

    expected_return = (next_row["close"] / next_row["open"]) - 1

    assert round(sample["target_next_return"], 10) == round(expected_return, 10)
    assert next_row["price_date"] > sample["price_date"].date().isoformat()
