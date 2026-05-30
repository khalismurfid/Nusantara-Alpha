"""Ranking endpoints."""

from backend.dependencies import get_repository, get_runtime_context
from backend.routers._compat import APIRouter
from backend.services.ranking_service import RankingService

router = APIRouter()


@router.get("/models/{model_id}/rankings")
def get_rankings(model_id: str, model_version: str):
    return RankingService(get_repository(), runtime_context=get_runtime_context()).get_rankings(model_id, model_version)
