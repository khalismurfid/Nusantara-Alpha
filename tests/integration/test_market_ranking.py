from backend.services.ranking_service import RankingService


def test_market_ranking_returns_supported_universe_scores(seeded_repo):
    response = RankingService(seeded_repo).get_rankings("idx-direction-baseline", "2026.05")

    rankings = response["rankings"]
    assert {row["ticker"] for row in rankings} == {"BBCA", "TLKM", "ASII"}
    assert [row["rank"] for row in rankings] == [1, 2, 3]
    assert rankings[0]["ranking_score"] >= rankings[-1]["ranking_score"]
    assert "not financial advice" in response["disclaimer"].lower()


def test_market_ranking_fails_closed_for_large_runtime_universe(seeded_repo, monkeypatch):
    for index in range(101):
        seeded_repo.upsert_stock(
            {
                "ticker": f"X{index:03d}",
                "name": f"Large Universe {index}",
                "exchange": "IDX",
                "universe_id": "idx-approved-universe",
                "support_status": "supported",
                "unavailable_reason": None,
                "data_as_of": "2026-05-29T09:00:00+00:00",
                "freshness_status": "current",
                "market_data_flags": [],
            }
        )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("large runtime rankings must not load market prices for retraining")

    monkeypatch.setattr(seeded_repo, "list_market_prices", fail_if_called)

    response = RankingService(seeded_repo).get_rankings("idx-direction-baseline", "2026.05")

    assert response["rankings"] == []
