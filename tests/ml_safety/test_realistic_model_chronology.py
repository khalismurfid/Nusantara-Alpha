from ml.backtesting.realistic import build_supervised_frame, build_triple_barrier_events, signal_from_target
from storage.seed_local_demo import _sample_market_prices


def test_supervised_target_uses_future_triple_barrier_window_without_feature_leakage():
    rows = _sample_market_prices([("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk")])
    supervised = build_supervised_frame(rows)
    sample = supervised[supervised["ticker"] == "BBCA"].iloc[0]

    assert sample["entry_date"] > sample["price_date"]
    assert sample["barrier_end_date"] >= sample["entry_date"]
    assert sample["barrier_hit"] in {"profit_take", "stop_loss", "vertical", "ambiguous"}
    assert sample["target"] in {-1, 0, 1}
    assert sample["atr_window"] == 20
    assert sample["barrier_atr_multiple"] == 1.0
    assert sample["upper_barrier"] > sample["entry_price"]
    assert sample["lower_barrier"] < sample["entry_price"]


def test_triple_barrier_can_label_neutral_when_no_barrier_is_hit():
    rows = []
    for day in range(28):
        rows.append(
            {
                "ticker": "BBCA",
                "price_date": f"2026-01-{day + 1:02d}",
                "open": 100.0,
                "high": 100.4,
                "low": 99.6,
                "close": 100.1,
                "volume": 1_000_000,
                "source": "test",
                "fetched_at": "2026-01-20T00:00:00+00:00",
            }
        )

    events = build_triple_barrier_events(rows, atr_window=3, barrier_atr_multiple=10, vertical_barrier_sessions=3)

    assert 0 in set(events["target"])
    assert set(events["barrier_hit"]) == {"vertical"}


def test_same_day_upper_and_lower_barrier_hit_is_neutral_because_order_is_unknown():
    rows = []
    for day in range(25):
        rows.append(
            {
                "ticker": "BBCA",
                "price_date": f"2026-02-{day + 1:02d}",
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 1_000_000,
                "source": "test",
                "fetched_at": "2026-03-01T00:00:00+00:00",
            }
        )
    rows.append(
        {
            "ticker": "BBCA",
            "price_date": "2026-02-26",
            "open": 100.0,
            "high": 103.0,
            "low": 97.0,
            "close": 100.0,
            "volume": 1_000_000,
            "source": "test",
            "fetched_at": "2026-03-01T00:00:00+00:00",
        }
    )

    events = build_triple_barrier_events(rows, atr_window=3, barrier_atr_multiple=0.5, vertical_barrier_sessions=1)
    ambiguous = events[events["barrier_hit"] == "ambiguous"]

    assert not ambiguous.empty
    assert set(ambiguous["target"]) == {0}


def test_signal_mapping_keeps_neutral_as_first_class_output():
    assert signal_from_target(1) == "up"
    assert signal_from_target(0) == "neutral"
    assert signal_from_target(-1) == "down"


def test_feature_builder_drops_non_finite_volume_change_rows():
    rows = _sample_market_prices([("BBCA", "Bank Central Asia Tbk"), ("TLKM", "Telkom Indonesia Tbk")])
    for row in rows:
        if row["ticker"] == "BBCA":
            row["volume"] = 0

    supervised = build_supervised_frame(rows)

    assert not supervised.empty
    assert "BBCA" not in set(supervised["ticker"])
