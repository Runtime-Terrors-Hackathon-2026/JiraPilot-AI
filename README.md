# JiraPilot AI — Autonomous Jira Triage & Root Cause Investigation Platform

[![Spring Boot 3.x](https://img.shields.io/badge/Spring%20Boot-3.2.5-brightgreen)](https://spring.io/projects/spring-boot)
[![Java 21](https://img.shields.io/badge/Java-21%20LTS-orange)](https://adoptium.net)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.2-61dafb)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8)](https://tailwindcss.com)

**JiraPilot AI** is an enterprise-grade autonomous engineering operations and incident triage platform. When a new Jira issue is created or updated, JiraPilot AI automatically determines whether the issue contains sufficient diagnostic context (logs, API endpoints, request/response payloads, environment, error messages).

- If critical diagnostics are missing: It calculates a weighted readiness score, adds an intelligent comment to Jira, notifies the reporter by email, and pauses in a `WAITING_FOR_INFORMATION` state. When updated, it automatically re-evaluates.
- If sufficient diagnostic information exists: It transitions the ticket to `READY`, executes automated root cause analysis (RCA), correlates downstream microservice dependencies, pinpoints the failure point, synthesizes safe reproduction commands (cURL & Postman), generates regression test suites (JUnit 5 & API), detects similar historical incidents, and posts a structured investigation report to Jira.

---

## 🏗️ Architecture

```
                                 ┌─────────────────────────────────┐
                                 │      Atlassian Jira Cloud       │
                                 │   (Webhooks & REST API v3)      │
                                 └────────────────┬────────────────┘
                                                  │ Webhook / REST
                                                  ▼
┌──────────────────────┐      REST        ┌─────────────────────────────────┐
│                      │ ◄──────────────► │       Spring Boot Backend       │
│  React 18 Dashboard  │                  │         (Port 8080)             │
│  - Linear / Notion   │                  │  - Workflow Orchestration       │
│    Design System     │                  │  - Jira Webhook Idempotency     │
│  - Service Graph     │                  │  - State Management             │
│  - Mock Email Inbox  │                  │  - Persistence & Audit Events   │
│  - Recharts & Alerts │                  └────────────────┬────────────────┘
└──────────────────────┘                                   │ REST (JSON)
                                                           ▼
                                          ┌─────────────────────────────────┐
                                          │     Python AI / Data Service    │
                                          │         (Port 8000)             │
                                          │  - Log Correlation & Parsing    │
                                          │  - Readiness Scoring Engine     │
                                          │  - RCA & Dependency Mapping     │
                                          │  - Similarity Matcher (TF-IDF)  │
                                          │  - Test Suite & Curl Generator  │
                                          └─────────────────────────────────┘
```

---

## ⚡ Features

1. **Deterministic & Contextual Ticket Readiness Engine**:
   - Evaluates 9 diagnostic dimensions (Logs, API Details, Payloads, Environment, Error Pattern, Expected vs Actual, etc.).
   - Configurable weighted policy (Total = 100).
2. **Autonomous Log Analysis & Multi-Service Correlation**:
   - Parses timestamps, log levels, service tags, exception types, HTTP endpoints, status codes, and correlates by `correlationId`.
3. **Automated Root Cause Diagnosis (RCA)**:
   - High/Medium/Low confidence scoring (e.g. 94% confidence for duplicate NFID conflicts).
   - Traceable evidence base, developer investigation steps, and recommended remediation.
4. **Service Dependency Graph**:
   - Visualizes request topology across microservice boundaries (Gateway → Circuit Service → WFM → PEDS → DB) and highlights the failing node.
5. **Safe Reproduction Suite**:
   - Generates executable, 100% synthetic safe `cURL` commands and Postman collection definitions.
6. **Automated Test Case Generation**:
   - Synthesizes 5 structured test cases (Unit, Integration, API) including Java JUnit 5 & Mockito test skeletons.
7. **Similar Incident Detection & Incident Memory**:
   - Matches incoming incident signatures against historical resolved incidents with similarity percentage and resolution explanations.
8. **Automated Jira Comments & Reporter Email Notifications**:
   - Posts formatted triage and investigation comments to Jira.
   - Dispatches email alerts with built-in Mock Email Viewer for presentation without live SMTP.

---

## 🔒 Security & Safe Synthetic Data Policy

For hackathons and prototyping, JiraPilot AI strictly complies with security boundaries:
- **Zero Real Data**: Uses ONLY synthetic data and sanitized test identifiers (`TEST-NFID-1001`, `TEST-CKT-1001`, `CORR-1001`).
- **Zero Hardcoded Secrets**: All credentials and API tokens are dynamically read from environment variables or `.env`.
- **Sensitive Data Masking**: Automatic redacting of potential keys, tokens, or personal identifiers in telemetry.

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

## 🐳 Running with Docker Compose

```bash
docker compose up --build
```

Access:
- **Frontend Dashboard**: `http://localhost:3000`
- **Backend API**: `http://localhost:8080`
- **Python AI Service**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432`

---

## 🎯 Step-by-Step Hackathon Demonstration Script

### Step 1: Open Dashboard
Navigate to `http://localhost:3000`. You will see the **AI Engineering Operations Dashboard** with live KPI stat cards and visual analytics.

### Step 2: Load Demo Dataset
Click the **"Load Demo Data"** button in the top navigation bar. Four synthetic incident tickets (`HACK-1001` to `HACK-1004`) will be populated.

### Step 3: Inspect Complete Incident (HACK-1001 — Duplicate NFID)
1. Click on **HACK-1001** (`Circuit creation API failing`).
2. Notice:
   - **Readiness Score**: `100/100` (Status: `READY` → `INVESTIGATED`).
   - **Root Cause**: `Duplicate NFID received from upstream NTLS integration causing unique constraint violation in PEDS DB.` (Confidence: `94%`).
   - **Service Graph**: Highlights `PEDS Service` as the failure point.
   - **Reproduction**: Copy synthetic `cURL` command with 1-click.
   - **Generated Test Cases**: Review `TC-001` through `TC-005` with Java JUnit 5 code snippet.
   - **Similar Historical Incidents**: Shows match with `HACK-102` (91% similarity).
   - **Jira Comment**: View structured investigation comment and click **"Post to Jira"**.

### Step 4: Inspect Incomplete Incident (HACK-1002 — Missing Diagnostics)
1. Navigate back and click on **HACK-1002** (`API is failing. Please check.`).
2. Notice:
   - **Readiness Score**: `30/100` (Status: `WAITING_FOR_INFORMATION`).
   - Diagnostic checklist shows missing **Logs**, **API Details**, and **Request Payload**.
   - **Jira Comment**: Formatted warning comment asking reporter for missing items.
   - Open **Mock Email Viewer** (Mail icon in navbar) to inspect the email notification dispatched to `bob.developer@example.com`.

### Step 5: Live Autonomous Re-Triage & Recovery
1. Inside **HACK-1002**, click **"Add Missing Diagnostics to Resume"**.
2. Click **"Fill Sample Diagnostic Logs"** and click **"Submit & Trigger Autonomous Re-Triage"**.
3. Watch the system automatically re-validate the issue, elevate readiness to `100%`, transition state to `READY`, and trigger root cause analysis!

---

## ⚙️ Real Atlassian Jira Cloud Integration

To connect to a live Jira Cloud instance instead of demo mode:

1. In `.env`, set:
   ```ini
   DEMO_MODE=false
   JIRA_BASE_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-atlassian-api-token
   JIRA_PROJECT_KEY=HACK
   ```
2. In Atlassian Jira Cloud:
   - Navigate to **Settings > System > Webhooks**.
   - Create Webhook URL pointing to: `https://your-public-url/api/webhooks/jira`
   - Select Events: `Issue created`, `Issue updated`.

---

## 🧪 Test Execution Verification

- **Python AI Service Tests**:
  ```powershell
  cd ai-service
  pytest tests/
  ```
  *(6/6 passed)*

- **Java Spring Boot Tests**:
  ```powershell
  cd backend
  mvn test
  ```
  *(6/6 passed)*

- **Frontend Build**:
  ```powershell
  cd frontend
  npm run build
  ```
  *(Built without errors)*
