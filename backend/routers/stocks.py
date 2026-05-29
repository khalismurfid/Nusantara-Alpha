from backend.dependencies import get_repository
from backend.routers._compat import APIRouter
from backend.services.stock_service import StockService

router = APIRouter()


@router.get("/models/{model_id}/stocks")
def list_stocks(model_id: str, query: str = "", model_version: str | None = None):
    repo = get_repository()
    if model_version is None:
        model = repo.get_model(model_id)
        model_version = model["model_version"] if model else ""
    return StockService(repo).list_stocks(model_id, model_version, query)
