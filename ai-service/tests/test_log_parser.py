import pytest
from app.services.log_parser import parse_logs

def test_parse_synthetic_logs_with_correlation():
    sample_logs = """
2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001
2026-10-08 10:31:43 ERROR [WFM] Downstream request failed status=500 endpoint=/api/circuit/provision correlationId=CORR-1001
    """
    res = parse_logs(sample_logs)
    assert len(res.entries) == 2
    assert "PEDS" in res.detectedServices
    assert "WFM" in res.detectedServices
    assert "CORR-1001" in res.correlatedIdGroups
    assert len(res.correlatedIdGroups["CORR-1001"]) == 2
    assert "/api/circuit/provision" in res.detectedEndpoints

def test_empty_logs():
    res = parse_logs("")
    assert len(res.entries) == 0
    assert res.probableErrorSummary == "No logs provided."
