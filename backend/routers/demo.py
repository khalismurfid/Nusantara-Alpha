from backend.config import get_settings
from backend.dependencies import get_repository, get_runtime_context
from backend.routers._compat import APIRouter
from backend.services.demo_status_service import DemoStatusService

router = APIRouter()


@router.get("/demo/status")
def demo_status():
    settings = get_settings()
    return DemoStatusService(
        get_repository(),
        runtime_context=get_runtime_context(),
        public_demo_url=settings.public_demo_url,
    ).get_status()

