import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "JiraPilot AI Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "deterministic") # deterministic, nvidia, openai, gemini
    
    # NVIDIA LLM Configuration
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    NVIDIA_TIMEOUT_SECONDS: int = int(os.getenv("NVIDIA_TIMEOUT_SECONDS", "30"))
    NVIDIA_ENABLED: bool = os.getenv("NVIDIA_ENABLED", "false").lower() == "true"

    # OpenAI & Gemini Fallbacks
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
