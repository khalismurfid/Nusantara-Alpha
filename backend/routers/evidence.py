from backend.dependencies import get_repository
from backend.routers._compat import APIRouter
from backend.services.evidence_service import EvidenceService

router = APIRouter()


@router.get("/models/{model_id}/evidence")
def get_model_evidence(model_id: str, model_version: str | None = None):
    repo = get_repository()
    if model_version is None:
        model = repo.get_model(model_id)
        model_version = model["model_version"] if model else ""
    return EvidenceService(repo).get_model_evidence(model_id, model_version)
