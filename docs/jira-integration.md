# JiraPilot AI — Jira Cloud Integration & Webhook Ingestion

## 1. Architecture & Project Scope

JiraPilot AI integrates with Jira Cloud via Atlassian REST APIs (v3) and incoming webhooks for the synthetic enterprise project key **`NOVA`** (or configured `JIRA_PROJECT_KEY`).

### Core Responsibilities:
- **Webhook Receiver**: Listens at `POST /api/webhooks/jira` for issue creation and update events.
- **Attachment Detection**: Identifies newly added attachments, extracts metadata, and downloads binary streams securely using Jira Basic Authentication or scoped API tokens.
- **Idempotency**: Computes SHA-256 digests for each attachment, preventing reprocessing if Jira fires multiple webhook triggers.
- **Comment Posting**: Posts standardized, 7-section markdown root-cause investigation reports directly back to the Jira issue via `POST /rest/api/3/issue/{issueKey}/comment`.

---

## 2. Standardized 7-Section Jira Comment Format

When an incident investigation completes, JiraPilot AI compiles a structured markdown comment following this precise 7-section structure:

1. **Header & Investigation Overview**: Key, severity, affected service, confidence percentage.
2. **Probable Root Cause**: Clear technical summary of failure mechanism.
3. **Line-Referenced Evidence Base**: Exact log line numbers, timestamps, and error excerpts.
4. **Matched Synthetic Repository & Git Commands**:
   ```bash
   git clone https://github.com/northstar-labs/<service-name>.git
   git clone --branch main https://github.com/northstar-labs/<service-name>.git
   ```
5. **Immediate Remediation Recommendation**: Developer fix recommendation.
6. **Reproduction cURL & Postman Steps**: Executable reproduction cURL snippet.
7. **Compliance & Synthetic Disclaimer**:
   > *Disclaimer: JiraPilot AI operates exclusively on synthetic demo data for Northstar Digital Systems. No production data or internal systems are accessed or referenced.*

---

## 3. Webhook Configuration Guide

To configure Jira Cloud to send events to JiraPilot AI:
1. Navigate to **Jira Settings** $\rightarrow$ **System** $\rightarrow$ **Webhooks**.
2. Click **Create a Webhook**.
3. **URL**: `https://<your-jirapilot-domain>/api/webhooks/jira`
4. **Issue Related Events**:
   - Issue: created, updated.
   - JQL Filter: `project = NOVA`
5. Save the webhook.

In local development or demo mode, synthetic webhooks can be simulated directly via the dashboard using the "Simulate Jira Issue" modal or via the backend endpoint:
```bash
POST /api/webhooks/jira
Content-Type: application/json

{
  "webhookEvent": "jira:issue_updated",
  "issue": {
    "key": "NOVA-101",
    "fields": {
      "summary": "Capacity check timeout",
      "attachment": [
        {
          "id": "1001",
          "filename": "server-error.log",
          "mimeType": "text/plain",
          "size": 4096,
          "content": "http://localhost:8080/demo-data/logs/sample.log"
        }
      ]
    }
  }
}
```
