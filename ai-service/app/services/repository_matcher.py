"""
Repository Discovery and Codebase Matcher for JiraPilot AI (Northstar Digital Systems)
Correlates identified API endpoints, service names, and stack-trace packages with approved repositories.
Generates copyable git clone commands and transparent matching justifications.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

CATALOG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "demo-data" / "repositories.json"

def load_repository_catalog() -> List[Dict[str, Any]]:
    """Loads approved repository metadata from demo-data/repositories.json."""
    if not CATALOG_PATH.exists():
        return []
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def match_repositories(
    service_name: Optional[str] = None,
    endpoints: Optional[List[str]] = None,
    stack_trace_packages: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Ranks approved repositories based on multi-signal matching:
    1. Exact service name match (weight 0.40)
    2. Endpoint path / pattern match (weight 0.35)
    3. Stack-trace package prefix match (weight 0.25)
    """
    catalog = load_repository_catalog()
    if not catalog:
        return []

    endpoints = endpoints or []
    stack_trace_packages = stack_trace_packages or []
    matched_results = []

    for repo in catalog:
        if not repo.get("isApproved", False):
            continue

        score = 0.0
        match_reasons = []
        matched_endpoints = []
        matched_packages = []

        # 1. Service name match
        repo_svc = (repo.get("serviceName") or "").lower()
        if service_name and service_name.lower() in repo_svc:
            score += 0.40
            match_reasons.append(f"Direct service ownership match for '{service_name}'")

        # 2. Endpoint pattern match
        repo_endpoints = [ep.lower() for ep in repo.get("supportedEndpoints", [])]
        repo_patterns = repo.get("endpointPatterns", [])

        for ep in endpoints:
            ep_clean = ep.lower().split("?")[0].strip()
            # Direct match
            if ep_clean in repo_endpoints:
                score += 0.35
                matched_endpoints.append(ep)
                match_reasons.append(f"Verified API endpoint contract: '{ep}'")
                break
            # Pattern match
            matched_pattern = False
            for pat in repo_patterns:
                if re.match(pat, ep_clean, re.IGNORECASE):
                    score += 0.30
                    matched_endpoints.append(ep)
                    match_reasons.append(f"Endpoint matches route pattern '{pat}'")
                    matched_pattern = True
                    break
            if matched_pattern:
                break

        # 3. Stack trace package prefix match
        repo_prefixes = repo.get("packagePrefixes", [])
        for pkg in stack_trace_packages:
            for prefix in repo_prefixes:
                if pkg.startswith(prefix) or prefix in pkg:
                    score += 0.25
                    matched_packages.append(pkg)
                    match_reasons.append(f"Stack trace package '{pkg}' matches prefix '{prefix}'")
                    break
            if matched_packages:
                break

        # Only include if there is at least one verified signal
        if score > 0.0:
            # Determine confidence category
            if score >= 0.65:
                confidence_category = "HIGH"
            elif score >= 0.35:
                confidence_category = "MEDIUM"
            else:
                confidence_category = "LOW"

            clone_url = repo.get("approvedCloneUrl")
            default_branch = repo.get("defaultBranch", "main")

            matched_results.append({
                "repositoryId": repo.get("repositoryId"),
                "displayName": repo.get("displayName"),
                "serviceName": repo.get("serviceName"),
                "ownerGroup": repo.get("ownerGroup"),
                "approvedCloneUrl": clone_url,
                "defaultBranch": default_branch,
                "cloneCommand": f"git clone {clone_url}",
                "cloneBranchCommand": f"git clone --branch {default_branch} {clone_url}",
                "score": round(min(score, 1.0), 2),
                "confidenceCategory": confidence_category,
                "matchReason": "; ".join(match_reasons),
                "matchedEndpoints": matched_endpoints,
                "matchedPackages": matched_packages,
                "verifiedModules": repo.get("verifiedModules", []),
                "description": repo.get("description", "")
            })

    # Sort descending by score
    matched_results.sort(key=lambda x: x["score"], reverse=True)
    return matched_results
