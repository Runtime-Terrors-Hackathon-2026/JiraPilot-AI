"""
Repository Catalog and Codebase Discovery Router for JiraPilot AI (Northstar Digital Systems)
Exposes endpoints to query approved repositories and match codebases for debugging.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.services.repository_matcher import load_repository_catalog, match_repositories

router = APIRouter(prefix="/api/v1/repositories", tags=["Repositories"])

class RepositoryMatchRequest(BaseModel):
    serviceName: Optional[str] = Field(None, description="Fictional service identifier")
    endpoints: Optional[List[str]] = Field(default_factory=list, description="Extracted API endpoint paths")
    stackTracePackages: Optional[List[str]] = Field(default_factory=list, description="Class/package names from stack trace")

@router.get("")
async def list_repositories():
    """Lists all approved synthetic repositories in Northstar Digital Systems."""
    catalog = load_repository_catalog()
    return catalog

@router.get("/{repository_id}")
async def get_repository(repository_id: str):
    """Retrieves metadata for an approved repository by ID."""
    catalog = load_repository_catalog()
    for repo in catalog:
        if repo.get("repositoryId", "").lower() == repository_id.lower():
            return repo
    raise HTTPException(status_code=404, detail=f"Repository '{repository_id}' not found in approved catalog.")

@router.post("/match")
async def match_codebases(request: RepositoryMatchRequest):
    """
    Ranks and suggests approved repositories using multi-signal matching
    against service names, endpoints, and stack-trace packages.
    """
    matches = match_repositories(
        service_name=request.serviceName,
        endpoints=request.endpoints,
        stack_trace_packages=request.stackTracePackages
    )
    return {
        "matchedCount": len(matches),
        "suggestions": matches
    }
