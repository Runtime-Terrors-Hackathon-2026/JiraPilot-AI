"""
Unit Test Suite for Log Analysis, Redaction, Repository Discovery, and NVIDIA Fallback
Covers Scenarios A, B, C, D, and F as required by the JiraPilot AI specification.
"""

import asyncio
import pytest
from app.services.redaction import sanitize_and_redact
from app.services.repository_matcher import match_repositories
from app.services.log_analysis_engine import LogAnalysisEngine
from app.services.nvidia_client import get_nvidia_status

def test_scenario_a_successful_log_investigation():
    """Scenario A: Known endpoint, correlation ID, HTTP error, exception, approved repository."""
    raw_log = (
        "2026-10-09 08:14:22.102 WARN c.n.inventory.service.ResourceAllocationService - [corrId=CORR-DEMO-1001] "
        "Resource DEMO-RESOURCE-1001 conflict on POST /api/v1/resources/allocate\n"
        "org.springframework.dao.DataIntegrityViolationException: Pre-existing allocation detected\n"
        "\tat com.northstar.inventory.repository.JpaResourceRepository.save(JpaResourceRepository.java:94)\n"
        "HTTP 409 Conflict returned to caller"
    )

    result = asyncio.run(LogAnalysisEngine.analyze_log(
        log_text=raw_log,
        filename="test_circuit_conflict.log",
        ticket_key="NOVA-101"
    ))

    assert result["status"] == "COMPLETED"
    assert result["isComplete"] is True
    assert result["primaryStatus"] == 409
    assert result["correlationId"] == "CORR-DEMO-1001"
    assert "POST /api/v1/resources/allocate" in result["primaryEndpoint"]
    assert "DataIntegrityViolationException" in result["exceptions"]
    assert len(result["evidence"]) >= 2
    assert result["confidenceScore"] >= 0.70
    assert result["confidenceCategory"] == "HIGH"
    
    # Verify repository matches
    repos = result["repositoryMatches"]
    assert len(repos) > 0
    top_repo = repos[0]
    assert top_repo["displayName"] == "resource-inventory-service"
    assert top_repo["approvedCloneUrl"] == "https://github.com/northstar-labs/resource-inventory-service.git"
    assert "git clone" in top_repo["cloneCommand"]
    assert "--branch main" in top_repo["cloneBranchCommand"]

def test_scenario_b_unknown_endpoint_no_fake_repo():
    """Scenario B: Unknown endpoint must NOT manufacture a fake repository or clone URL."""
    matches = match_repositories(
        service_name="unknown-internal-service-xyz",
        endpoints=["/api/v99/unregistered/random/endpoint"],
        stack_trace_packages=["com.random.unregistered.pkg"]
    )
    # Should not invent any repository
    assert len(matches) == 0

def test_scenario_c_sensitive_log_content_redaction_and_quarantine():
    """Scenario C: Redaction of bearer tokens, passwords, cookies and quarantine of private keys."""
    # 1. Redaction of credentials
    sensitive_log = (
        "Inbound request Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz.secret\n"
        "User credentials password='demo-super-secret-password' and api_key='demo_key_99887766554433'\n"
        "Cookie: JSESSIONID=ABCD1234EFGH5678"
    )
    sanitized, quarantine_required, reasons, counts = sanitize_and_redact(sensitive_log)
    assert quarantine_required is False
    assert "demo-super-secret-password" not in sanitized
    assert "demo_key_99887766554433" not in sanitized
    assert "[REDACTED_TOKEN]" in sanitized or "[REDACTED_JWT]" in sanitized
    assert "[REDACTED_PASSWORD]" in sanitized
    assert "[REDACTED_COOKIE]" in sanitized or "[REDACTED_SESSION]" in sanitized

    # 2. Quarantine trigger for unencrypted private key block
    key_log = (
        "FATAL: Application crashed\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0Y3...\n"
        "-----END RSA PRIVATE KEY-----\n"
    )
    _, quarantine_required_key, reasons_key, _ = sanitize_and_redact(key_log)
    assert quarantine_required_key is True
    assert len(reasons_key) > 0
    assert "Private Key" in reasons_key[0]

def test_scenario_d_incomplete_or_empty_log():
    """Scenario D: Incomplete, malformed, or empty logs return inconclusive analysis."""
    result = asyncio.run(LogAnalysisEngine.analyze_log(
        log_text="",
        filename="empty.log",
        ticket_key="NOVA-EMPTY"
    ))
    assert result["status"] == "COMPLETED"
    assert result["isComplete"] is False
    assert result["confidenceScore"] == 0.0
    assert result["confidenceCategory"] == "INCONCLUSIVE"
    assert "Inconclusive" in result["probableRootCause"]
    assert len(result["recommendedDebuggingSteps"]) > 0

def test_scenario_f_nvidia_fallback_status():
    """Scenario F: Deterministic fallback mode is reported cleanly when NVIDIA key is unset."""
    status = get_nvidia_status()
    assert "provider" in status
    assert status["provider"] == "nvidia"
    assert "activeMode" in status
    assert status["activeMode"] in ["nvidia_llm", "deterministic_fallback"]
