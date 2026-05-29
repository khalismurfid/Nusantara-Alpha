from backend.dependencies import get_repository
from backend.routers._compat import APIRouter
from backend.schemas.contracts import UnsupportedStockInterestRequest
from backend.services.unsupported_stock_interest_service import UnsupportedStockInterestService

router = APIRouter()


@router.post("/unsupported-stock-interest")
def record_unsupported_stock_interest(request: UnsupportedStockInterestRequest):
    return UnsupportedStockInterestService(get_repository()).record(request.ticker, request.reason, request.model_id)
