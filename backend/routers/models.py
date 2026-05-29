from backend.dependencies import get_repository, get_runtime_context
from backend.routers._compat import APIRouter
from backend.services.model_service import ModelService

router = APIRouter()


@router.get("/models")
def list_models():
    return ModelService(get_repository(), runtime_context=get_runtime_context()).list_models()
