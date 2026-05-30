from backend.schemas.contracts import RankingResponse
from backend.services.ranking_service import RankingService


def test_ranking_response_contract(seeded_repo):
    response = RankingService(seeded_repo).get_rankings("idx-direction-baseline", "2026.05")

    parsed = RankingResponse.model_validate(response)

    assert parsed.rankings
    assert parsed.rankings[0].rank == 1
    assert parsed.rankings[0].ranking_score >= 0
