from fastapi import APIRouter
from app.models.schemas import ReproductionRequest, ReproductionResponse
from app.services.reproduction_engine import generate_reproduction

router = APIRouter(prefix="/analyze", tags=["Reproduction"])

@router.post("/reproduction", response_model=ReproductionResponse)
async def create_reproduction(req: ReproductionRequest):
    return generate_reproduction(req.ticket, req.apiFinding)
