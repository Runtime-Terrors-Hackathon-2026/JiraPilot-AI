# JiraPilot AI - API Contracts & Inter-Service Interfaces
**Fictional Organization:** Northstar Digital Systems  
**Product:** JiraPilot AI  
**Scope:** Stable interface specifications between Java Backend, Python AI Service, React UI, and Jira Adapter.

---

## 1. Architecture Overview & Port Allocation

| Component | Default Port | Base URL | Primary Role |
| :--- | :--- | :--- | :--- |
| **Java Backend** | `8080` | `http://localhost:8080` | Orchestrator, Jira Cloud client, DB persistence |
| **Python AI Service** | `8000` | `http://localhost:8000` | Ticket validation, log parsing, RCA synthesis |
| **React Dashboard** | `3000` | `http://localhost:3000` | Web UI, operator triage console |
| **Jira Cloud** | `443` | `https://siva-shankaran.atlassian.net` | External issue tracker (Project `KAN` / `NOVA`) |

---

## 2. Python AI Service REST Contracts (`http://localhost:8000`)

### 2.1 Health & Status Check
* **Method:** `GET`
* **Path:** `/health`
* **Response:** `200 OK`
```json
{
  "status": "HEALTHY",
  "service": "ai-service",
  "version": "1.0.0"
}
```

### 2.2 Ticket Completeness Validation
* **Method:** `POST`
* **Path:** `/api/v1/validate`
* **Request Header:** `Content-Type: application/json`
* **Request Body:**
```json
{
  "ticket_key": "NOVA-101",
  "title": "HTTP 409 Conflict: Duplicate synthetic resource ID",
  "description": "Attempting to allocate virtual circuit DEMO-RESOURCE-1001 resulted in a 409 Conflict.",
  "api_details": "POST /api/v1/resources/allocate",
  "logs": "2026-10-09T08:14:22.102Z WARN c.n.inventory.service... DataIntegrityViolationException",
  "request_payload": "{\"resourceType\": \"VIRTUAL_CIRCUIT\", \"resourceId\": \"DEMO-RESOURCE-1001\"}",
  "response_payload": "{\"error\": \"RESOURCE_ALREADY_EXISTS\", \"status\": 409}",
  "environment": "staging",
  "error_message": "DataIntegrityViolationException: Pre-existing allocation detected",
  "expected_behavior": "Resource allocation generates distinct synthetic ID",
  "actual_behavior": "Returns HTTP 409",
  "replication_steps": "1. Post resource allocation payload. 2. Observe 409.",
  "reporter_email": "demo-operator-01@northstar.example.com"
}
```
* **Response Body (`200 OK`):**
```json
{
  "ticket_key": "NOVA-101",
  "is_complete": true,
  "readiness_score": 95.0,
  "missing_fields": [],
  "identified_fields": ["logs", "api_details", "request_payload", "response_payload", "environment", "error_message"],
  "comment_template": "All required investigation criteria are present. Commencing root-cause synthesis.",
  "notification_needed": false
}
```

### 2.3 Incident Investigation & RCA Synthesis
* **Method:** `POST`
* **Path:** `/api/v1/investigate`
* **Request Body:** Same schema as `/api/v1/validate`.
* **Response Body (`200 OK`):**
```json
{
  "ticket_key": "NOVA-101",
  "summary": "Database constraint collision on resourceId DEMO-RESOURCE-1001 in resource-inventory-service",
  "apis_involved": ["POST /api/v1/resources/allocate"],
  "services_affected": ["resource-inventory-service"],
  "probable_failure_point": "JpaResourceRepository.save() on table synthetic_resources",
  "probable_root_cause": "Primary key collision during concurrent reservation requests due to non-unique synthetic ID generation.",
  "confidence_score": 0.95,
  "reproduction_curl": "curl -X POST 'http://localhost:8084/api/v1/resources/allocate' -H 'Content-Type: application/json' -d '{\"resourceType\":\"VIRTUAL_CIRCUIT\",\"resourceId\":\"DEMO-RESOURCE-1001\"}'",
  "reproduction_steps": [
    "Send POST request to /api/v1/resources/allocate with static resourceId DEMO-RESOURCE-1001",
    "Observe DataIntegrityViolationException returned with HTTP 409"
  ],
  "developer_investigation_steps": [
    "Check JpaResourceRepository for missing optimistic locking (@Version annotation)",
    "Verify UUID generator bean configuration in ResourceAllocationService"
  ],
  "suggested_test_cases": [
    "testConcurrentResourceAllocation_shouldNotCollide()",
    "testDuplicateResourceId_returnsIdempotentOkOrCleanConflict()"
  ],
  "similar_incidents": [
    {
      "incident_id": "NOVA-122",
      "similarity_score": 0.88,
      "summary": "Database deadlock during concurrent circuit reservation",
      "resolution": "Acquire table locks in deterministic sorted resource ID order"
    }
  ],
  "rca_document": "### Root Cause Analysis (RCA)\n- **Incident:** NOVA-101\n- **Impact:** Circuit provisioning halted\n- **Root Cause:** Race condition in synthetic ID assignment.",
  "jira_comment_markdown": "🤖 *JiraPilot AI Investigation Report*\n\n**Probable Root Cause:** Primary key collision in resource-inventory-service.\n**Confidence:** 95%"
}
```

---

## 3. Java Backend REST Contracts (`http://localhost:8080`)

### 3.1 Health Check
* **Method:** `GET`
* **Path:** `/api/health`
* **Response Body (`200 OK`):**
```json
{
  "status": "UP",
  "service": "JiraPilot AI Orchestrator Backend",
  "demoMode": false,
  "aiServiceUrl": "http://localhost:8000",
  "timestamp": 1791543913852
}
```

### 3.2 Fetch All Issues
* **Method:** `GET`
* **Path:** `/api/issues`
* **Response Body (`200 OK`):**
```json
[
  {
    "id": 1,
    "jiraKey": "NOVA-101",
    "summary": "HTTP 409 Conflict: Duplicate synthetic resource ID",
    "status": "INVESTIGATION_COMPLETED",
    "service": "resource-inventory-service",
    "environment": "staging",
    "readinessScore": 95.0,
    "isComplete": true,
    "confidenceScore": 0.95,
    "probableRootCause": "Primary key collision during concurrent reservation requests",
    "reporterEmail": "demo-operator-01@northstar.example.com",
    "createdAt": "2026-10-09T08:14:22Z"
  }
]
```

### 3.3 Fetch Issue Detail
* **Method:** `GET`
* **Path:** `/api/issues/{key}`
* **Response Body (`200 OK`):** Full issue record including logs, payloads, reproduction curl, and investigation report.

### 3.4 Revalidate Issue
* **Method:** `POST`
* **Path:** `/api/issues/{key}/validate`
* **Response Body (`200 OK`):** Evaluation result with updated readiness score and missing fields checklist.

### 3.5 Run AI Investigation
* **Method:** `POST`
* **Path:** `/api/issues/{key}/investigate`
* **Response Body (`200 OK`):** Full investigation results, developer reproduction steps, and synthesized RCA.

### 3.6 Trigger Sync with Jira Cloud
* **Method:** `POST`
* **Path:** `/api/tickets/sync`
* **Response Body (`200 OK`):**
```json
{
  "syncedCount": 5,
  "status": "SUCCESS",
  "timestamp": "2026-10-09T10:30:00Z"
}
```

### 3.4 Ingest Jira Cloud Webhook
* **Method:** `POST`
* **Path:** `/api/webhooks/jira`
* **Request Header:** `X-Atlassian-Webhook-Identifier: ...`
* **Behavior:** Extracts `issue.key`, fields, and comments, asynchronously triggering validation and investigation pipeline.

### 3.5 System Audit Log Telemetry
* **Method:** `GET`
* **Path:** `/api/audit-logs`
* **Response Body (`200 OK`):** List of state transitions, comments posted to Jira, and email dispatch records.
