import os
from pathlib import Path
from pydantic import BaseModel

# Automatically load .env if present
for env_path in [Path(".env"), Path("../.env"), Path(__file__).resolve().parents[2] / ".env"]:
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

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
