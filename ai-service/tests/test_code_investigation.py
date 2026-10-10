import pytest
from app.models.schemas import TicketPayload
from app.services.code_investigation_service import investigate_codebase, generate_code_diff_patch
from app.services.code_indexer import (
    resolve_repo_path, scan_repository_files, find_symbols_in_repository,
    trace_execution_path_from_evidence, identify_failure_locations_from_code
)
from app.services.repository_matcher import load_repository_catalog

def test_load_repository_catalog_has_mock_repos():
    catalog = load_repository_catalog()
    assert len(catalog) > 0
    inv_repo = next((r for r in catalog if r.get("repositoryId") == "REPO-RES-INV"), None)
    assert inv_repo is not None
    assert inv_repo.get("isApproved") is True
    assert inv_repo.get("localPath") == "mock-repositories/resource-inventory-service"

def test_resolve_repo_path():
    catalog = load_repository_catalog()
    inv_repo = next(r for r in catalog if r.get("repositoryId") == "REPO-RES-INV")
    path = resolve_repo_path(inv_repo)
    assert path is not None
    assert path.exists()
    assert path.is_dir()

def test_scan_repository_files():
    catalog = load_repository_catalog()
    inv_repo = next(r for r in catalog if r.get("repositoryId") == "REPO-RES-INV")
    path = resolve_repo_path(inv_repo)
    files = scan_repository_files(path)
    assert len(files) >= 4
    file_names = [f.name for f in files]
    assert "ResourceController.java" in file_names
    assert "ResourceAllocationService.java" in file_names
    assert "JpaResourceRepository.java" in file_names

def test_find_symbols_in_repository():
    catalog = load_repository_catalog()
    inv_repo = next(r for r in catalog if r.get("repositoryId") == "REPO-RES-INV")
    path = resolve_repo_path(inv_repo)
    symbols = find_symbols_in_repository(path)
    assert len(symbols) >= 3
    controller_sym = next((s for s in symbols if s.className == "ResourceController"), None)
    assert controller_sym is not None
    assert controller_sym.role == "CONTROLLER"

def test_trace_execution_path_and_failure_locations():
    catalog = load_repository_catalog()
    inv_repo = next(r for r in catalog if r.get("repositoryId") == "REPO-RES-INV")
    path = resolve_repo_path(inv_repo)
    
    stack_trace = """2026-10-09T08:14:22.102Z [http-nio-8084-exec-3] WARN  c.n.inventory.service.ResourceAllocationService - [corrId=CORR-DEMO-1001] Resource ID DEMO-RESOURCE-1001 already reserved.
org.springframework.dao.DataIntegrityViolationException: Pre-existing allocation detected for resource ID: DEMO-RESOURCE-1001
\tat com.northstar.inventory.repository.JpaResourceRepository.save(JpaResourceRepository.java:94)
\tat com.northstar.inventory.service.ResourceAllocationService.reserveCircuit(ResourceAllocationService.java:142)"""

    steps = trace_execution_path_from_evidence(
        repo_path=path,
        service_name="resource-inventory-service",
        endpoint="/api/v1/resources/allocate",
        stack_trace=stack_trace
    )
    assert len(steps) >= 2
    
    locations = identify_failure_locations_from_code(
        repo_path=path,
        stack_trace=stack_trace,
        error_message="DataIntegrityViolationException: Pre-existing allocation"
    )
    assert len(locations) >= 2
    assert locations[0].category == "OBSERVED"
    assert "JpaResourceRepository" in locations[0].className
    assert locations[1].category == "PROPAGATED"
    assert "ResourceAllocationService" in locations[1].className

def test_investigate_codebase_full_report():
    ticket = TicketPayload(
        key="NOVA-101",
        summary="HTTP 409 Conflict: Duplicate synthetic resource ID",
        apiDetails="POST /api/v1/resources/allocate",
        errorMessage="DataIntegrityViolationException: Pre-existing allocation detected",
        logs="""org.springframework.dao.DataIntegrityViolationException: Pre-existing allocation detected
\tat com.northstar.inventory.repository.JpaResourceRepository.save(JpaResourceRepository.java:94)
\tat com.northstar.inventory.service.ResourceAllocationService.reserveCircuit(ResourceAllocationService.java:142)"""
    )
    
    report = investigate_codebase(ticket)
    assert report.status == "READY_FOR_REVIEW"
    assert report.repositoryId == "REPO-RES-INV"
    assert len(report.executionPath) >= 2
    assert len(report.failureLocations) >= 2
    assert report.codeDiff is not None
    assert "diff" in report.codeDiff.unifiedDiff or "---" in report.codeDiff.unifiedDiff
    assert len(report.testRecommendations) >= 1
    assert report.confidenceScore >= 80
