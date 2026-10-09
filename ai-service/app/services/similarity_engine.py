import json
import os
import math
import re
from typing import List
from app.models.schemas import TicketPayload, SimilarIncident, SimilarityResponse

KNOWLEDGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base.json")

def _tokenize(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r'[A-Za-z0-9_\-]+', text) if len(w) > 2]

def _cosine_similarity(vec1: dict, vec2: dict) -> float:
    dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in vec1)
    mag1 = math.sqrt(sum(v * v for v in vec1.values()))
    mag2 = math.sqrt(sum(v * v for v in vec2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)

def find_similar_incidents(ticket: TicketPayload, limit: int = 3) -> SimilarityResponse:
    if not os.path.exists(KNOWLEDGE_FILE):
        return SimilarityResponse(similarIncidents=[])

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        kb = json.load(f)

    query_text = f"{ticket.summary or ''} {ticket.description or ''} {ticket.apiDetails or ''} {ticket.logs or ''} {ticket.errorMessage or ''}"
    query_tokens = _tokenize(query_text)
    query_vec = {}
    for t in query_tokens:
        query_vec[t] = query_vec.get(t, 0) + 1

    results = []
    for item in kb:
        doc_text = f"{item['summary']} {item['affectedService']} {item['affectedApi']} {item['rootCause']} {item['resolution']}"
        doc_tokens = _tokenize(doc_text)
        doc_vec = {}
        for t in doc_tokens:
            doc_vec[t] = doc_vec.get(t, 0) + 1

        sim = _cosine_similarity(query_vec, doc_vec)
        # Boost if service matches or specific root causes match
        service_match = item["affectedService"].lower() in query_text.lower()
        keyword_overlap = sum(1 for t in ["nfid", "timeout", "nullpointer", "duplicate", "circuit"] if t in query_text.lower() and t in doc_text.lower())
        if sim > 0:
            boost = (25 if service_match else 0) + (keyword_overlap * 12)
            score = min(96, max(65, int(round(sim * 60 + boost))))
        else:
            score = 30

        results.append(SimilarIncident(
            jiraKey=item["jiraKey"],
            summary=item["summary"],
            similarityScore=score,
            affectedService=item["affectedService"],
            affectedApi=item["affectedApi"],
            rootCause=item["rootCause"],
            resolution=item["resolution"],
            explanation=item.get("explanation", f"Matched on shared service '{item['affectedService']}' and failure signatures.")
        ))

    results.sort(key=lambda x: x.similarityScore, reverse=True)
    return SimilarityResponse(similarIncidents=results[:limit])
