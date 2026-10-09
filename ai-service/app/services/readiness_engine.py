import re
from typing import List, Tuple
from app.models.schemas import TicketPayload, ReadinessScoreWeights, ValidationResponse

def evaluate_readiness(ticket: TicketPayload, weights: ReadinessScoreWeights = None) -> ValidationResponse:
    if weights is None:
        weights = ReadinessScoreWeights()

    missing: List[str] = []
    available: List[str] = []
    total_score = 0
    max_score = (
        weights.description +
        weights.apiDetails +
        weights.logs +
        weights.requestPayload +
        weights.environment +
        weights.errorMessage +
        weights.expectedActualBehavior +
        weights.replicationSteps +
        weights.screenshots
    )

    full_text = f"{ticket.summary or ''} {ticket.description or ''}"
    comments_text = " ".join([c.get("body", "") for c in (ticket.comments or []) if isinstance(c, dict)])
    combined_text = f"{full_text} {comments_text}"

    # 1. Description
    if ticket.description and len(ticket.description.strip()) > 15:
        available.append("description")
        total_score += weights.description
    else:
        missing.append("description")

    # 2. API details (explicit field or in text)
    has_api = False
    if ticket.apiDetails and len(ticket.apiDetails.strip()) > 3:
        has_api = True
    elif re.search(r'\b(GET|POST|PUT|DELETE|PATCH)\s+/[A-Za-z0-9_\-/]+', combined_text, re.IGNORECASE) or re.search(r'/api/[A-Za-z0-9_\-/]+', combined_text, re.IGNORECASE):
        has_api = True

    if has_api:
        available.append("apiDetails")
        total_score += weights.apiDetails
    else:
        missing.append("apiDetails")

    # 3. Logs (explicit field or in description/comments)
    has_logs = False
    if ticket.logs and len(ticket.logs.strip()) > 10:
        has_logs = True
    elif re.search(r'(\d{4}-\d{2}-\d{2}|\bERROR\b|\bWARN\b|Exception|correlationId=|\bstacktrace\b)', combined_text, re.IGNORECASE):
        has_logs = True

    if has_logs:
        available.append("logs")
        total_score += weights.logs
    else:
        missing.append("logs")

    # 4. Request Payload
    has_payload = False
    if ticket.requestPayload and len(ticket.requestPayload.strip()) > 4:
        has_payload = True
    elif re.search(r'\{[\s\S]*"[a-zA-Z0-9_-]+"\s*:[\s\S]*\}', combined_text):
        has_payload = True

    if has_payload:
        available.append("requestPayload")
        total_score += weights.requestPayload
    else:
        missing.append("requestPayload")

    # 5. Environment
    has_env = False
    if ticket.environment and len(ticket.environment.strip()) > 1:
        has_env = True
    elif re.search(r'\b(PROD|STAGE|STAGING|DEV|DEVELOPMENT|QA|UAT|PREPROD|TEST|SANDBOX)\b', combined_text, re.IGNORECASE):
        has_env = True

    if has_env:
        available.append("environment")
        total_score += weights.environment
    else:
        missing.append("environment")

    # 6. Error message / Actual Behavior
    has_error = False
    if ticket.errorMessage and len(ticket.errorMessage.strip()) > 3:
        has_error = True
    elif ticket.actualBehavior and len(ticket.actualBehavior.strip()) > 3:
        has_error = True
    elif re.search(r'\b(500|502|503|504|400|401|403|404|failed|failing|error|exception|crash|timeout)\b', combined_text, re.IGNORECASE):
        has_error = True

    if has_error:
        available.append("errorMessage")
        total_score += weights.errorMessage
    else:
        missing.append("errorMessage")

    # 7. Expected vs Actual Behavior
    has_expected = False
    if ticket.expectedBehavior and len(ticket.expectedBehavior.strip()) > 3:
        has_expected = True
    elif re.search(r'(expected|should return|should succeed|200 OK|201 Created|expected behavior)', combined_text, re.IGNORECASE):
        has_expected = True

    if has_expected:
        available.append("expectedBehavior")
        total_score += weights.expectedActualBehavior
    else:
        missing.append("expectedBehavior")

    # 8. Replication Steps (Optional)
    if (ticket.replicationSteps and len(ticket.replicationSteps.strip()) > 5) or re.search(r'(step 1|reproduce|reproduction steps)', combined_text, re.IGNORECASE):
        available.append("replicationSteps")
        total_score += weights.replicationSteps

    # 9. Screenshots / Attachments (Optional)
    if ticket.screenshots and len(ticket.screenshots) > 0:
        available.append("screenshots")
        total_score += weights.screenshots

    normalized_score = int(round((total_score / max_score) * 100))
    # Threshold for READY is score >= 75 and essential fields (logs, error/api/description) present
    status = "READY" if (normalized_score >= 70 and "logs" in available and "apiDetails" in available) else "NEEDS_INFORMATION"

    # Humanized reason
    if status == "READY":
        reason = f"Ticket contains sufficient diagnostic context (Readiness Score: {normalized_score}/100) including API details, error patterns, and system logs for automated root cause analysis."
    else:
        missing_readable = ", ".join([m.replace("apiDetails", "API Endpoint & Method").replace("requestPayload", "Request Payload JSON").replace("expectedBehavior", "Expected Behavior").capitalize() for m in missing])
        reason = f"Ticket lacks critical diagnostic artifacts ({missing_readable}). Readiness Score: {normalized_score}/100. Automated investigation paused pending reporter update."

    # Jira Comment
    if status == "READY":
        jira_comment = (
            f"h3. 🚀 JiraPilot AI — Ticket Ready for Investigation\n"
            f"*Readiness Score:* {normalized_score}/100 (Status: *READY*)\n"
            f"All critical triage criteria met. Automated log correlation, API dependency tracing, and RCA generation have started."
        )
        email_body = ""
    else:
        missing_bullets = "\n".join([f"* *{m.replace('apiDetails', 'API Endpoint & Method').replace('requestPayload', 'Sample Request Payload (JSON)').replace('expectedBehavior', 'Expected vs Actual Result')}*" for m in missing])
        jira_comment = (
            f"h3. ⚠️ JiraPilot AI — Additional Information Required\n"
            f"Hello [~{ticket.reporter or 'reporter'}],\n\n"
            f"Our automated triage engine analyzed this issue and found a readiness score of *{normalized_score}/100*. To initiate deep root cause investigation, please provide:\n\n"
            f"{missing_bullets}\n\n"
            f"_Once updated, JiraPilot AI will automatically resume validation and begin full root cause diagnosis._"
        )
        email_body = (
            f"Hello,\n\n"
            f"Your Jira issue {ticket.key or 'HACK-TICKET'} ('{ticket.summary or 'Incident'}') requires additional diagnostic details to proceed with automated root cause analysis.\n\n"
            f"Missing Information:\n"
            f"{chr(10).join(['- ' + m for m in missing])}\n\n"
            f"Why this is needed: System log traces and API request payloads allow JiraPilot AI to correlate downstream service bottlenecks and generate automated test reproductions.\n\n"
            f"Please update the ticket directly in Jira.\n\n"
            f"Best regards,\n"
            f"JiraPilot AI Triage Team"
        )

    return ValidationResponse(
        readinessScore=normalized_score,
        status=status,
        missingInformation=missing,
        availableInformation=available,
        reason=reason,
        suggestedJiraComment=jira_comment,
        suggestedEmailBody=email_body
    )
