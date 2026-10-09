from fastapi import APIRouter
from app.models.schemas import InvestigationRequest, InvestigationResponse
from app.services.investigation_engine import run_investigation

router = APIRouter(prefix="/analyze", tags=["Investigation"])

@router.post("/investigate", response_model=InvestigationResponse)
async def investigate_ticket(req: InvestigationRequest):
    return run_investigation(req.ticket, req.parsedLogs)
