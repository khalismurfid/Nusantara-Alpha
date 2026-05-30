from backend.services.ranking_service import RankingService


def test_market_ranking_returns_supported_universe_scores(seeded_repo):
    response = RankingService(seeded_repo).get_rankings("idx-direction-baseline", "2026.05")

    rankings = response["rankings"]
    assert {row["ticker"] for row in rankings} == {"BBCA", "TLKM", "ASII"}
    assert [row["rank"] for row in rankings] == [1, 2, 3]
    assert rankings[0]["ranking_score"] >= rankings[-1]["ranking_score"]
    assert "not financial advice" in response["disclaimer"].lower()
