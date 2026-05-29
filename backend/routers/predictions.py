from backend.dependencies import get_repository, get_runtime_context
from backend.routers._compat import APIRouter
from backend.schemas.contracts import PredictionRequest
from backend.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/predictions")
def request_prediction(request: PredictionRequest):
    return PredictionService(get_repository(), runtime_context=get_runtime_context()).request_prediction(request)
