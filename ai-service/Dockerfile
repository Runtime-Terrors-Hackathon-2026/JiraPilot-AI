# ==============================================================================
# JiraPilot AI - Python 3.12 FastAPI Service Dockerfile for Render / Cloud
# ==============================================================================

FROM python:3.12-slim

WORKDIR /app

# Install curl and git for health checks and repository utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Cache Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and synthetic data catalogs
COPY app ./app
COPY demo-data ./demo-data
COPY mock-repositories ./mock-repositories

# Environment defaults
ENV PORT=8000
ENV ENVIRONMENT=production
ENV DEMO_MODE=true
ENV AI_PROVIDER=deterministic

EXPOSE 8000

# Dynamic port binding for Render ($PORT)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
