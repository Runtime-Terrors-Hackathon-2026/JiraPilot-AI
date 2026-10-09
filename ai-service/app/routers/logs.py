from fastapi import APIRouter
from app.models.schemas import LogParseRequest, LogParseResponse
from app.services.log_parser import parse_logs

router = APIRouter(prefix="/analyze", tags=["Logs"])

@router.post("/logs", response_model=LogParseResponse)
async def parse_log_text(req: LogParseRequest):
    return parse_logs(req.logs)
