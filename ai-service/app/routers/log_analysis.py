"""
Log Analysis and Telemetry Router for JiraPilot AI (Northstar Digital Systems)
Exposes endpoints for log parsing, evidence extraction, repository discovery, and provider status.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.services.log_analysis_engine import LogAnalysisEngine
from app.services.nvidia_client import get_nvidia_status

router = APIRouter(prefix="/api/v1", tags=["Log Analysis"])

# In-memory store for recent analyses
ANALYSIS_CACHE: Dict[str, Dict[str, Any]] = {}

class LogAnalysisRequest(BaseModel):
    logText: str = Field(..., description="Raw log telemetry text to analyze")
    filename: Optional[str] = Field("upload.log", description="Source log filename")
    ticketKey: Optional[str] = Field("NOVA-SIM", description="Target Jira ticket key")
    analysisId: Optional[str] = Field(None, description="Optional custom analysis ID")

@router.post("/log-analysis/analyze")
async def analyze_logs(request: LogAnalysisRequest):
    """
    Executes deep log analysis, deterministic evidence correlation,
    repository matching, and optional NVIDIA LLM reasoning.
    """
    result = await LogAnalysisEngine.analyze_log(
        log_text=request.logText,
        filename=request.filename,
        ticket_key=request.ticketKey,
        analysis_id=request.analysisId
    )
    ANALYSIS_CACHE[result["analysisId"]] = result
    return result

@router.get("/log-analysis/{analysis_id}")
async def get_analysis_by_id(analysis_id: str):
    """Retrieves previously generated analysis report by ID."""
    if analysis_id not in ANALYSIS_CACHE:
        raise HTTPException(status_code=404, detail=f"Analysis with ID '{analysis_id}' not found.")
    return ANALYSIS_CACHE[analysis_id]

@router.get("/log-analysis/{analysis_id}/endpoints")
async def get_analysis_endpoints(analysis_id: str):
    """Retrieves extracted HTTP endpoints for a specific analysis."""
    if analysis_id not in ANALYSIS_CACHE:
        raise HTTPException(status_code=404, detail=f"Analysis with ID '{analysis_id}' not found.")
    analysis = ANALYSIS_CACHE[analysis_id]
    return {
        "analysisId": analysis_id,
        "endpoints": analysis.get("endpoints", []),
        "primaryEndpoint": analysis.get("primaryEndpoint")
    }

@router.get("/log-analysis/{analysis_id}/repositories")
async def get_analysis_repositories(analysis_id: str):
    """Retrieves matched codebases and clone commands for a specific analysis."""
    if analysis_id not in ANALYSIS_CACHE:
        raise HTTPException(status_code=404, detail=f"Analysis with ID '{analysis_id}' not found.")
    analysis = ANALYSIS_CACHE[analysis_id]
    return {
        "analysisId": analysis_id,
        "primaryService": analysis.get("primaryService"),
        "repositories": analysis.get("repositoryMatches", [])
    }

@router.post("/log-analysis/{analysis_id}/retry")
async def retry_analysis(analysis_id: str):
    """Re-executes an analysis on cached telemetry."""
    if analysis_id not in ANALYSIS_CACHE:
        raise HTTPException(status_code=404, detail=f"Analysis with ID '{analysis_id}' not found.")
    previous = ANALYSIS_CACHE[analysis_id]
    # Re-run analysis
    result = await LogAnalysisEngine.analyze_log(
        log_text=previous.get("filename", "") or "synthetic retry",
        filename=previous.get("filename"),
        ticket_key=previous.get("ticketKey"),
        analysis_id=analysis_id
    )
    ANALYSIS_CACHE[analysis_id] = result
    return result

@router.get("/nvidia/status")
async def nvidia_provider_status():
    """Checks NVIDIA NIM LLM provider readiness without revealing secrets."""
    return get_nvidia_status()
