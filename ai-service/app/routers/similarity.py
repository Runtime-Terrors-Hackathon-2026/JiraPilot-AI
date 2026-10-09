from fastapi import APIRouter
from app.models.schemas import SimilarityRequest, SimilarityResponse
from app.services.similarity_engine import find_similar_incidents

router = APIRouter(prefix="/analyze", tags=["Similarity"])

@router.post("/similarity", response_model=SimilarityResponse)
async def check_similarity(req: SimilarityRequest):
    return find_similar_incidents(req.currentTicket, req.limit or 3)
