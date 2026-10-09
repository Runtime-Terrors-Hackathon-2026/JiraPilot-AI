# JiraPilot AI - Security, Confidentiality & Privacy Policy
**Fictional Organization:** Northstar Digital Systems (`northstar-labs`)  
**Product:** JiraPilot AI  
**Scope:** Security safeguards, synthetic data architecture, masking policies, and automated compliance.

---

## 1. Zero-Confidentiality & Public-Safety Guarantee

This project is an independently developed, public-safe engineering demonstration created from scratch for hackathon and open-source demonstration purposes.

### Strict Confidentiality Guardrails:
* **No Real Employer or Client Data:** No internal code, internal infrastructure hostnames, real customer records, private service names, proprietary architectures, internal documentation, or internal incident logs from any employer or commercial entity are used or referenced.
* **No Internal Mappings:** There is strictly zero mapping between fictional Northstar Digital Systems components and real enterprise production systems.
* **Fictional Enterprise Entity:** All systems, organizations, teams, and architectures belong to the fictional entity **Northstar Digital Systems** (`northstar-labs`).
* **No Metric Exaggeration:** No claims of actual enterprise production savings, real production MTTR reductions, or proprietary ROI metrics are made. All telemetry is purely illustrative.

---

## 2. Synthetic Data Conventions

To ensure zero risk of data leakage, all datasets in this repository follow strict synthetic naming standards:

| Entity Type | Synthetic Format Standard | Example |
| :--- | :--- | :--- |
| **Resource IDs** | `DEMO-RESOURCE-[0-9]{4}` | `DEMO-RESOURCE-1001` |
| **Correlation IDs**| `CORR-DEMO-[0-9]{4}` | `CORR-DEMO-1001` |
| **Trace IDs** | `trace-demo-[0-9]{5}` | `trace-demo-88102` |
| **User Identifiers**| `demo-user-[0-9]{2}` / `demo-sre-[0-9]{2}` | `demo-sre-02` |
| **Email Addresses**| `*@northstar.example.com` / `*@example.com` | `demo-operator-01@northstar.example.com` |
| **Domain Names** | `*.internal.northstar.example.com` / `*.example.com` | `resource-inventory-service.internal.northstar.example.com` |
| **IP Addresses** | RFC 5737 Test Networks (`192.0.2.0/24`, `198.51.100.0/24`) | `198.51.100.24` |

---

## 3. Secret Management & Sensitive Data Masking

### 3.1 Environment Variable Isolation
* No production credentials, Atlassian API tokens, SMTP passwords, or OpenAI/Gemini API keys are checked into source control.
* All sensitive parameters are injected through environment variables defined in `.env.example` templates.
* Sample configuration files only contain benign placeholders: `your-api-token-here`.

### 3.2 Output & Telemetry Masking
The Python AI engine and Java logging interceptors apply automated regex sanitizers to mask sensitive credentials before persistence or Jira comment generation:
* **Bearer Tokens / JWTs:** Sanitized as `Bearer [REDACTED_JWT]`
* **Sensitive Credentials:** Sanitized in logs as `credential_field: [MASKED]`
* **API Keys:** Sanitized as `[REDACTED_API_KEY]`

---

## 4. Automated Compliance Scanning & Limitations

### 4.1 Scanner Utility
The repository includes an automated compliance and secret scanner at [`scripts/scan_secrets_and_compliance.py`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/scripts/scan_secrets_and_compliance.py). This script checks for:
* High-entropy secret patterns (AWS access keys, unencrypted private keys, GitHub tokens, Slack webhook tokens).
* Hardcoded password assignments.
* Disallowed proprietary organizational keywords.

Execute the compliance scan anytime using:
```powershell
python scripts/scan_secrets_and_compliance.py
```

### 4.2 Disclaimer & Limitation of Automation
> [!CAUTION]
> **DISCLAIMER & LIMITATION OF AUTOMATION:**  
> Automated scanning scripts and regex heuristics **cannot guarantee** that all confidential, proprietary, or sensitive information has been eliminated. Static analysis tools cannot understand human semantic context or detect obfuscated identifiers. **Human peer review is mandatory** before any branch or artifact is shared externally.
