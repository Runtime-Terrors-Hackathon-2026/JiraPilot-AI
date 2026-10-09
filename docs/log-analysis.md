# JiraPilot AI — Log Intelligence Engine

## 1. Overview
JiraPilot AI provides an enterprise-grade, deterministic-first log analysis engine designed specifically for microservices architectures at Northstar Digital Systems. It ingests server logs, extracts line-level diagnostic evidence, performs secret redaction, correlates services and HTTP errors, and matches the failure against approved synthetic repositories.

---

## 2. Ingestion Pipeline & Supported Formats

The ingestion engine supports the following text-based formats:
- `.log` (Plain application logs, Logback, Log4j2, JSON lines)
- `.txt` (Text traces, console dumps, cURL response dumps)
- `.json` (Structured JSON log files and batch log arrays)
- `.jsonl` (Newline-delimited JSON log streams)
- `.log.gz` (Safely decompressed gzip files with decompression bomb protection)

### Ingestion Safety Constraints:
- **Max File Size**: 10 MB raw upload limit.
- **Decompression Limit**: 20 MB uncompressed cap with a maximum expansion ratio of 10x to prevent gzip bombs.
- **Line Limit**: 1,000 maximum parsed lines per file to prevent memory exhaustion and token bloat.
- **Processing Timeout**: 15 seconds per attachment analysis.
- **Idempotency**: Every attachment is hashed via SHA-256 before processing. Re-uploading the same file returns the existing analysis without duplicate execution.

---

## 3. Secret Redaction & Quarantine Policy

Before any log content is analyzed or transmitted to AI reasoning providers, it passes through the Redaction Engine (`ai-service/app/services/redaction.py`):
1. **Quarantine Triggers**:
   - If raw private keys (`-----BEGIN RSA PRIVATE KEY-----`, EC, DSA, OpenSSH) are discovered in the log payload, analysis is **quarantined immediately**.
   - Quarantined logs are marked `NEEDS_REVIEW`, flagged with a warning banner, and **never sent to external AI providers (NVIDIA NIM)**.
2. **Deterministic Redaction**:
   - Authorization Bearer tokens are masked: `Bearer [REDACTED_TOKEN]`
   - JSON Web Tokens (JWT) are masked: `eyJ[REDACTED_JWT]`
   - Passwords and secrets in JSON/query strings: `password=[REDACTED_SECRET]`
   - API keys and tokens: `[REDACTED_KEY]`

---

## 4. Evidence Extraction & Line Referencing

Unlike generic LLM summaries that fabricate line numbers or log messages:
- Every piece of evidence extracted references the exact line number where the issue occurred:
  ```json
  {
    "line": 42,
    "timestamp": "2026-10-09T10:14:22.109Z",
    "level": "ERROR",
    "service": "resource-inventory-service",
    "message": "Duplicate allocation request detected for resourceId=DEMO-RES-1044",
    "correlation_id": "CORR-DEMO-1002"
  }
  ```
- **Error Patterns Detected**:
  - `RESOURCE_CONFLICT` (HTTP 409, duplicate unique constraints, primary key violations)
  - `DOWNSTREAM_TIMEOUT` (HTTP 504, `SocketTimeoutException`, `Gateway Timeout`)
  - `UPSTREAM_AUTH_FAILURE` (HTTP 401/403, invalid tokens, signature validation failures)
  - `RATE_LIMIT_EXCEEDED` (HTTP 429, token bucket exhaustion)
  - `SCHEMA_VALIDATION_ERROR` (HTTP 400, missing mandatory fields)
  - `SERVICE_UNAVAILABLE` (HTTP 502/503, connection refused)

---

## 5. Confidence Scoring Model

Confidence scores are deterministically calculated using weighted heuristic criteria rather than model hallucination:
- **Base Score**: 50 points.
- **Correlation ID present**: +10 points.
- **Explicit HTTP status code extracted**: +10 points.
- **Recognized Northstar service matched**: +15 points.
- **Stack trace or root exception matched**: +15 points.
- **Categorization**:
  - `HIGH`: Confidence $\ge$ 80%
  - `MEDIUM`: Confidence 60% – 79%
  - `LOW`: Confidence $<$ 60%
