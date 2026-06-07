from storage.database import connect, initialize
from storage.repositories import Repository


def test_has_market_prices_uses_presence_check(temp_db_path):
    conn = connect(temp_db_path)
    initialize(conn)
    repo = Repository(conn)

    assert not repo.has_market_prices()

    repo.upsert_market_prices(
        [
            {
                "ticker": "BBCA",
                "price_date": "2026-05-29",
                "open": 5700.0,
                "high": 5800.0,
                "low": 5600.0,
                "close": 5750.0,
                "adj_close": 5750.0,
                "volume": 1_000_000,
                "source": "test",
                "fetched_at": "2026-06-01T00:00:00+00:00",
            }
        ]
    )

    assert repo.has_market_prices()
    conn.close()
