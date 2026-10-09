from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import validation, investigation, logs, similarity, testcases, reproduction, health

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Log Analysis, Ticket Readiness, and Root Cause Investigation Service for JiraPilot AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(validation.router)
app.include_router(investigation.router)
app.include_router(logs.router)
app.include_router(similarity.router)
app.include_router(testcases.router)
app.include_router(reproduction.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
