from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return {
        "status": "UP",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "provider": settings.AI_PROVIDER,
        "demoMode": settings.DEMO_MODE
    }
