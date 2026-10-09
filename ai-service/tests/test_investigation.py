import pytest
from app.models.schemas import TicketPayload
from app.services.investigation_engine import run_investigation

def test_investigation_duplicate_nfid():
    ticket = TicketPayload(
        key="HACK-1001",
        summary="Circuit creation API failing",
        description="Circuit creation fails intermittently during provisioning.",
        apiDetails="POST /api/circuit/provision",
        logs="2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001",
        requestPayload='{"circuitId": "TEST-1001", "nfid": "TEST-NFID-1001"}'
    )
    res = run_investigation(ticket)
    assert res.rca.probableRootCause is not None
    assert "Duplicate NFID" in res.rca.probableRootCause
    assert res.rca.rootCauseConfidence == 94
    assert res.rca.confidenceLevel == "HIGH"
    assert len(res.rca.supportingEvidence) >= 3
    assert len(res.rca.serviceGraphNodes) == 5
    assert len(res.generatedTestCases) >= 4
    assert "curl" in res.reproductionCurl
