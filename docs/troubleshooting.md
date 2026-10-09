# JiraPilot AI — Troubleshooting Guide

## Common Issues & Resolutions

### 1. Attachment Processing Failed or Quarantined
- **Symptom**: Attachment status shows `NEEDS_REVIEW` or `Quarantined (Sensitive Key Pattern Detected)`.
- **Cause**: The redactor detected private key headers (`-----BEGIN RSA PRIVATE KEY-----`, etc.) or high-entropy credentials.
- **Resolution**: Quarantined logs are prohibited from being sent to external LLMs. Inspect the file locally. If safe, remove the private key text and re-upload the file.

---

### 2. File Upload Rejected (`File exceeds limit` or `Decompression limit exceeded`)
- **Symptom**: HTTP 400 with error `File size exceeds maximum allowed limit (10MB)` or `Gzip decompression exceeded limit`.
- **Cause**: Uploaded file exceeds 10MB or is a nested/compressed gzip bomb.
- **Resolution**: Truncate logs before uploading or extract only the relevant incident window (e.g. 5 minutes before and after failure). The system enforces a maximum of 1,000 parsed lines.

---

### 3. NVIDIA NIM Status: Deterministic Fallback Active
- **Symptom**: Dashboard navbar displays "Deterministic AI Fallback" instead of "NVIDIA NIM Active".
- **Cause**: `NVIDIA_API_KEY` is not set or the external service returned 401/429.
- **Resolution**: Check `GET http://localhost:8000/api/v1/nvidia/status`. Ensure `NVIDIA_API_KEY` starts with `nvapi-` and is exported in the environment. JiraPilot AI continues functioning normally in deterministic mode.

---

### 4. Jira Webhooks Not Ingesting Attachments
- **Symptom**: Issue updates in Jira Cloud do not reflect new attachments in JiraPilot AI.
- **Cause**: Jira webhook payload contains metadata only; Jira REST credentials (`JIRA_EMAIL` and `JIRA_API_TOKEN`) may be missing or lack attachment download permissions.
- **Resolution**:
  1. Verify `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` in `.env`.
  2. Verify that the Jira user has the **Browse Projects** and **Manage Attachments** permissions in the `NOVA` project.
  3. Use the dashboard's manual upload or paste modal on the ticket detail page for immediate offline triage.

---

### 5. EmailJS Dispatches Showing `MOCK_SUCCESS`
- **Symptom**: Alerts appear in internal drawer but no real email arrives in personal inbox.
- **Cause**: System is operating in simulation mode because `EMAILJS_PUBLIC_KEY` is not configured or `EMAILJS_ENABLED=false`.
- **Resolution**: Configure `EMAILJS_SERVICE_ID`, `EMAILJS_TEMPLATE_ID`, and `EMAILJS_PUBLIC_KEY` in `.env`. Ensure the recipient domain matches `EMAILJS_ALLOWED_RECIPIENTS`.
