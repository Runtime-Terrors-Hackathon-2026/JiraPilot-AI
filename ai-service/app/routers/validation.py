from fastapi import APIRouter
from app.models.schemas import ValidationRequest, ValidationResponse
from app.services.readiness_engine import evaluate_readiness

router = APIRouter(prefix="/analyze", tags=["Validation"])

@router.post("/validate", response_model=ValidationResponse)
async def validate_ticket(req: ValidationRequest):
    return evaluate_readiness(req.ticket, req.weights)
