# JiraPilot AI — EmailJS Notifications Setup & Verification

## 1. Overview
JiraPilot AI integrates with [EmailJS](https://www.emailjs.com/) to send high-priority incident triage alerts and log analysis reports to engineering on-call teams.

---

## 2. Step-by-Step Account Setup

1. Create a free account at [emailjs.com](https://www.emailjs.com/).
2. Under **Email Services**, click **Add New Service** (e.g. Gmail, Outlook, or Personal SMTP) and note your **Service ID** (e.g., `service_jirapilot`).
3. Under **Email Templates**, click **Create New Template**:
   - Template Name: `JiraPilot Incident RCA`
   - Subject: `[{{issue_key}}] {{alert_title}}`
   - Content Variables to include:
     - `{{to_email}}` — Recipient email
     - `{{issue_key}}` — Jira ticket key (e.g., NOVA-101)
     - `{{summary}}` — Incident summary
     - `{{service_name}}` — Affected microservice
     - `{{root_cause}}` — Identified probable root cause
     - `{{confidence}}` — Confidence score
     - `{{repo_url}}` — Matched GitHub repository URL
     - `{{clone_command}}` — Suggested git clone command
     - `{{evidence_snippet}}` — Line-referenced log excerpt
   - Save the template and note the **Template ID** (e.g., `template_rca_alert`).
4. In your EmailJS Account Settings, locate your **Public Key** (`user_xxx` or alphanumeric key) and **Private Key** (under Security settings).

---

## 3. Configuration & Allowlist Filtering

Configure your environment variables in `.env`:
```bash
EMAILJS_ENABLED=true
EMAILJS_SERVICE_ID=service_jirapilot
EMAILJS_TEMPLATE_ID=template_rca_alert
EMAILJS_PUBLIC_KEY=your_public_key
EMAILJS_PRIVATE_KEY=your_private_key
EMAILJS_DEFAULT_RECIPIENT=oncall@example.com

# Strict allowlist protection (comma-separated domains or exact emails)
EMAILJS_ALLOWED_RECIPIENTS=example.com,northstar.io,developer@example.com
```

### Safety & Simulation Mode:
- **Simulation Fallback**: If `EMAILJS_ENABLED=false` or keys are not provided, JiraPilot AI automatically runs in `SIMULATED` mode. All outgoing notifications are recorded in the internal database and visible in the dashboard email drawer without calling external APIs.
- **Recipient Allowlist**: If an email recipient does not match `EMAILJS_ALLOWED_RECIPIENTS`, dispatch is blocked with a security audit event to prevent accidental notifications to external parties.

---

## 4. Verification & Testing

You can test email delivery directly from the backend or React dashboard:
```bash
# Test Email Dispatch API
curl -X POST http://localhost:8080/api/notifications/test-email \
  -H "Content-Type: application/json" \
  -d '{"recipient": "oncall@example.com"}'
```
Response:
```json
{
  "status": "MOCK_SUCCESS",
  "recipient": "oncall@example.com",
  "provider": "EmailJS (Simulation Mode)",
  "message": "Simulated dispatch succeeded. Configure EMAILJS_PUBLIC_KEY for live sending."
}
```
In the React UI, navigate to any ticket, open the **Log Intelligence & Attachment Center**, click **Send Email Alert**, review the live HTML/Text preview, and dispatch with a single click.
