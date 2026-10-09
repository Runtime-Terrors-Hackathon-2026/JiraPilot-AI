import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "JiraPilot AI Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "deterministic") # deterministic, openai, gemini
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
