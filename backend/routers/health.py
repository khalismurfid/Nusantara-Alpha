from backend.routers._compat import APIRouter
from backend.schemas.contracts import HealthResponse

router = APIRouter()


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")

