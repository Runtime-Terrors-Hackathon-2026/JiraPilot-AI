# JiraPilot AI — Autonomous Jira Triage, Log Intelligence & RCA Platform

[![Spring Boot 3.x](https://img.shields.io/badge/Spring%20Boot-3.2.5-brightgreen)](https://spring.io/projects/spring-boot)
[![Java 21](https://img.shields.io/badge/Java-21%20LTS-orange)](https://adoptium.net)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.2-61dafb)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8)](https://tailwindcss.com)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA%20NIM-Compatible-76B900)](https://build.nvidia.com)
[![EmailJS](https://img.shields.io/badge/EmailJS-Notifications-FF6C37)](https://www.emailjs.com)

**JiraPilot AI** is an enterprise-grade autonomous engineering operations, log intelligence, and incident triage platform built for the fictional organization **Northstar Digital Systems** (`northstar-labs`, synthetic Jira project `NOVA`).

When an issue is created or updated in Jira, or when server logs (`.log`, `.txt`, `.json`, `.jsonl`, `.log.gz`) are attached, JiraPilot AI automatically inspects diagnostic context, correlates distributed services, redacts credentials, pinpoints root causes with line-referenced evidence, matches approved GitHub repositories, generates copyable `git clone` commands, posts structured 7-section comments back to Jira, and dispatches incident alerts via EmailJS.

---

## 🏗️ Architecture

```
                                 ┌─────────────────────────────────┐
                                 │      Atlassian Jira Cloud       │
                                 │   (Webhooks & REST API v3)      │
                                 └────────────────┬────────────────┘
                                                  │ Webhook / Attachment Stream
                                                  ▼
┌──────────────────────┐      REST        ┌─────────────────────────────────┐
│                      │ ◄──────────────► │       Spring Boot Backend       │
│  React 18 Dashboard  │                  │         (Port 8080)             │
│  - Linear / Notion   │                  │  - Attachment Ingestion & Gzip  │
│    Design System     │                  │  - Jira Webhook Idempotency     │
│  - Log Investigation │                  │  - Comment Formatting (7-Sec)   │
│    Card & Tabs       │                  │  - EmailJS Dispatch & Allowlist │
│  - Service Graph     │                  │  - Persistence & Audit Events   │
│  - Copyable Clones   │                  └────────────────┬────────────────┘
└──────────────────────┘                                   │ REST (JSON)
                                                           ▼
                                          ┌─────────────────────────────────┐
                                          │     Python AI / Data Service    │
                                          │         (Port 8000)             │
                                          │  - Safe Redactor & Quarantine   │
                                          │  - Line-Referenced Evidence     │
                                          │  - Multi-Signal Repo Discovery  │
                                          │  - NVIDIA NIM (Prompt Defense)  │
                                          │  - Deterministic AI Fallback    │
                                          └─────────────────────────────────┘
```

---

## ⚡ Core Features

1. **Autonomous Log Attachment Ingestion & Safety**:
   - Ingests `.log`, `.txt`, `.json`, `.jsonl`, and `.log.gz` via Jira webhook, manual drag-and-drop, or text paste.
   - Guarded with 10MB upload limits, 20MB decompression limits (gzip bomb defense), 1,000 line ceilings, and SHA-256 idempotency.
   - Detects private keys and triggers automatic quarantine (`NEEDS_REVIEW`) to block external exposure.

2. **Line-Referenced Log Intelligence & Evidence Base**:
   - Deterministic log parsing maps exact line numbers, timestamps, log levels, HTTP codes (400, 401, 404, 409, 429, 500, 502, 503, 504), and correlation IDs.
   - Computes weighted confidence scores without synthetic hallucinations.

3. **Approved Repository Discovery & Git Clones**:
   - Multi-signal matching maps failures to 7 approved synthetic Northstar microservice repositories.
   - Generates 1-click copyable `git clone` and `git clone --branch main` commands.

4. **NVIDIA NIM LLM Adapter & Injection Defenses**:
   - Supports OpenAI-compatible completions via NVIDIA Cloud Functions / NIM (e.g. `meta/llama-3.1-70b-instruct`).
   - Hardened with system prompt isolation, injection phrase scrubbing, strict JSON schema output validation, and seamless fallback to deterministic reasoning when offline.

5. **Standardized 7-Section Jira Comment Engine**:
   - Synthesizes formatted Jira markdown reports with executive summary, root cause, line evidence, clone commands, remediation advice, and synthetic disclaimers.

6. **EmailJS Incident Notifications & Allowlist**:
   - Dispatches HTML/Text incident alerts via EmailJS REST API.
   - Protected by recipient domain allowlisting (`EMAILJS_ALLOWED_RECIPIENTS`) and built-in simulation fallback mode.

7. **Interactive Operations Dashboard**:
   - Real-time React 18 UI featuring ticket search, readiness scores, log viewers, live comment posting, and test email dispatches.

---

## 🔒 Confidentiality & Safe Synthetic Data Policy

This project strictly adheres to public-safe hackathon standards:
- **Exclusively Synthetic**: Uses independently created services, mock repositories (`northstar-labs`), and synthetic project key `NOVA`.
- **Zero Real Data**: No proprietary employer or client source code, logs, endpoints, or credentials are used.
- **Zero Committed Secrets**: `.env` is git-ignored, all secrets use placeholders, and the repository is verified using `scripts/scan_secrets_and_compliance.py`.

---

## 🚀 Quick Start (Local Run)

### Prerequisites
- **Java 21 LTS** & **Maven 3.9+**
- **Python 3.12+**
- **Node.js 18+** & **npm**

*(Portable runtimes are bundled directly in `C:\Users\support\tools` on this environment).*

### Option 1: One-Click Startup (Windows PowerShell)

```powershell
.\start-all.ps1
```

### Option 2: Starting Services Individually

1. **Start Python AI Service (Port 8000)**:
   ```powershell
   cd ai-service
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Start Spring Boot Backend (Port 8080)**:
   ```powershell
   cd backend
   mvn spring-boot:run
   ```

3. **Start React Frontend (Port 3000)**:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

Open your browser at **[http://localhost:3000](http://localhost:3000)**.

---

## 📚 Detailed Documentation

- [Log Intelligence & Safety Guide](docs/log-analysis.md)
- [Repository Discovery & Matching Strategy](docs/repository-discovery.md)
- [Jira Cloud Integration & Webhook Ingestion](docs/jira-integration.md)
- [NVIDIA NIM Setup & Injection Defenses](docs/nvidia-setup.md)
- [EmailJS Notifications & Verification](docs/emailjs-setup.md)
- [Troubleshooting & FAQ](docs/troubleshooting.md)
- [Enterprise Service Catalog](docs/enterprise-service-catalog.md)

---

## 🧪 Test Execution & Verification

Run the automated test suites across all layers:

```powershell
# 1. Python AI Service Tests (11/11 tests pass)
cd ai-service
pytest tests/

# 2. Java Spring Boot Unit & Integration Tests (14/14 tests pass)
cd backend
mvn test

# 3. Frontend TypeScript & Production Build
cd frontend
npm run build

# 4. Fixture Validation Script
python scripts/validate_fixtures.py

# 5. Secret & Compliance Security Scan (0 violations)
python scripts/scan_secrets_and_compliance.py
```
