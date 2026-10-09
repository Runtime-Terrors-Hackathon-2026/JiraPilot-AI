import pytest
from app.models.schemas import TicketPayload
from app.services.readiness_engine import evaluate_readiness

def test_ready_ticket():
    ticket = TicketPayload(
        key="HACK-1001",
        summary="Circuit creation API failing",
        description="Circuit creation fails intermittently during provisioning.",
        apiDetails="POST /api/circuit/provision",
        logs="2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001",
        requestPayload='{"circuitId": "TEST-1001", "nfid": "TEST-NFID-1001"}',
        environment="SANDBOX",
        errorMessage="HTTP 500 Duplicate NFID",
        expectedBehavior="201 Created and circuit provisioned",
        actualBehavior="500 Internal Server Error"
    )
    res = evaluate_readiness(ticket)
    assert res.status == "READY"
    assert res.readinessScore >= 75
    assert "logs" in res.availableInformation
    assert "apiDetails" in res.availableInformation

def test_incomplete_ticket():
    ticket = TicketPayload(
        key="HACK-1002",
        summary="API is failing",
        description="API is failing. Please check."
    )
    res = evaluate_readiness(ticket)
    assert res.status == "NEEDS_INFORMATION"
    assert "logs" in res.missingInformation
    assert "apiDetails" in res.missingInformation
    assert "requestPayload" in res.missingInformation
    assert "⚠️ JiraPilot AI" in res.suggestedJiraComment
