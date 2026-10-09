import pytest
from app.models.schemas import TicketPayload
from app.services.similarity_engine import find_similar_incidents

def test_find_similar_incidents():
    ticket = TicketPayload(
        key="HACK-1001",
        summary="Circuit creation failure with duplicate NFID constraint error",
        description="PEDS rejects circuit provisioning due to duplicate NFID payload.",
        logs="Duplicate NFID detected in PEDS service"
    )
    res = find_similar_incidents(ticket, limit=2)
    assert len(res.similarIncidents) > 0
    top_match = res.similarIncidents[0]
    assert top_match.jiraKey == "HACK-102"
    assert top_match.similarityScore >= 80
    assert "NFID" in top_match.rootCause
