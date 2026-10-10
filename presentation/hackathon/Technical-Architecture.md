# JiraPilot AI — Technical Architecture & Engineering Specifications

> **Scope**: Comprehensive architectural reference document containing non-technical business overviews, detailed microservice specifications, component responsibilities, Mermaid architecture and sequence diagrams, and Zero-Trust security implementations.

---

## 1. Executive Summary & Architectural Philosophy

JiraPilot AI is engineered as an **enterprise-grade, polyglot microservice system**. Rather than relying on monolithic web servers or fragile all-in-one AI wrappers, the platform divides responsibilities cleanly across three specialized runtime tiers:

1. **User Presentation & Interactive Observability Tier** (React 18 + TypeScript + Vite)
2. **Deterministic Business Logic, Persistence & Orchestration Tier** (Java 21 + Spring Boot 3)
3. **Telemetry Parsing, Repository Matching & AI Synthesis Tier** (Python 3.12 + FastAPI)

### Architectural Design Principles
* **Separation of Determinism and Heuristics**: Exact calculations (scoring checklists, regex parsing, secret masking, HTTP code extraction) are executed deterministically. Large Language Models (LLMs) are used strictly for natural-language synthesis and contextual clarification, never for guessing system facts.
* **Resilience First (Offline-Capable Architecture)**: If external third-party services (such as Jira Cloud, external LLM endpoints, or cloud email providers) experience latency or downtime, the core system continues operating via local JPA persistence and local heuristic fallbacks.
* **Zero-Trust Data Boundaries**: Telemetry logs and ticket contents are sanitized on-premise *before* transmission to downstream reasoning services or external storage.

---

## 2. System Architecture Diagram

```mermaid
graph TD
    subgraph Client Tier ["Client Presentation Tier (Browser)"]
        UI["React 18 + TypeScript SPA<br/>(Tailwind CSS Tokens)"]
        Canvas["Interactive Holographic<br/>API Flow Canvas (SVG)"]
        UI --> Canvas
    end

    subgraph Core Backend ["Enterprise Core Engine (Port 8080)"]
        Gateway["Spring Boot 3.2 Web API"]
        JiraService["Jira Integration Service<br/>(REST API v3)"]
        ScoreEngine["Deterministic Ticket<br/>Readiness Engine"]
        AuditService["Audit & History Ledger<br/>(JPA Repository)"]
        EmailService["EmailJS Notification<br/>Dispatcher"]
        
        Gateway --> ScoreEngine
        Gateway --> JiraService
        Gateway --> AuditService
        Gateway --> EmailService
    end

    subgraph AI Microservice ["AI & Telemetry Engine (Port 8000)"]
        FastAPI["FastAPI Python Microservice"]
        Redactor["Zero-Trust Secret & PII<br/>Redaction Pipeline"]
        LogParser["Log Telemetry Parser<br/>(Regex Extraction)"]
        RepoMatcher["Repository Catalog<br/>Matcher (Heuristic)"]
        LLMAdapter["NVIDIA NIM / LLM<br/>Synthesis Adapter"]
        
        FastAPI --> Redactor
        Redactor --> LogParser
        LogParser --> RepoMatcher
        RepoMatcher --> LLMAdapter
    end

    subgraph External Ecosystem ["Enterprise Integrations"]
        JiraCloud["Atlassian Jira Cloud<br/>(Projects KAN / NOVA)"]
        EmailJSCloud["EmailJS Gateway<br/>(service_1ooa8fh)"]
        GitHost["Enterprise Git Repos<br/>(GitHub / GitLab)"]
        DB[(H2 / PostgreSQL<br/>JPA Database)]
    end

    UI <-->|REST / JSON| Gateway
    Gateway <-->|Internal REST / JSON| FastAPI
    JiraService <-->|HTTPS REST v3| JiraCloud
    EmailService -->|HTTPS Dispatch| EmailJSCloud
    RepoMatcher -.->|Metadata Query| GitHost
    AuditService <-->|JPA / JDBC| DB
```

---

## 3. Tier Responsibilities & Component Specifications

### 3.1 Frontend Presentation Tier (`jira-pilot-ui`)
* **Technology Stack**: React 18.2, TypeScript 5, Vite 5, Tailwind CSS 3.4, Lucide React icons, Recharts.
* **Port**: `http://localhost:3000`
* **Key Responsibilities**:
  * **Operational Dashboard (`App.tsx`)**: Displays active incident queues, readiness scores, and investigation findings.
  * **Holographic API Flow Canvas (`ApiFlowCanvas.tsx`)**: Hardware-accelerated SVG renderer that visualizes microservice request topologies in isometric perspective. Generates animated particle pulses along SVG paths without heavy WebGL overhead.
  * **Synchronized Details & Timeline (`ApiFlowDetailsPanel.tsx`, `ApiFlowTimeline.tsx`)**: Allows instant bidirectional inspection between network nodes and supporting server log lines.
  * **Deterministic State Management**: Uses typed API clients and normalized models (`apiFlowNormalizer.ts`) to ensure reliable rendering even when log schemas vary.

### 3.2 Enterprise Core Backend (`jira-pilot-backend`)
* **Technology Stack**: Java 21 LTS, Spring Boot 3.2.5, Spring Data JPA, H2 In-Memory (Dev) / PostgreSQL (Prod), Maven.
* **Port**: `http://localhost:8080`
* **Key Responsibilities**:
  * **Jira Cloud Synchronization (`JiraClientService.java`)**: Interfaces with Atlassian Cloud REST API v3 to ingest issues, download attachments, and write rich markdown comments.
  * **Readiness Evaluation Engine (`TicketReadinessService.java`)**: Calculates a 100-point ticket completeness score across 5 deterministic criteria (endpoints, environments, reproduction steps, expected vs actual behavior, log attachments).
  * **Email Notification Gateway (`EmailJsService.java`)**: Dispatches executive notification payloads to EmailJS cloud endpoints, handling header serialization, token authorization, and delivery audit logs.
  * **Audit & Investigation Persistence (`InvestigationService.java`)**: Stores historical investigation records, readiness trends, and comment posting logs.

### 3.3 AI & Telemetry Engine (`jira-pilot-ai`)
* **Technology Stack**: Python 3.12, FastAPI, Uvicorn, Pydantic v2, PyYAML, Requests.
* **Port**: `http://localhost:8000`
* **Key Responsibilities**:
  * **Zero-Trust Redaction (`redactor.py`)**: Sanitizes incoming logs and user inputs before processing.
  * **Log Telemetry Parser (`log_parser.py`)**: Uses deterministic regex patterns to extract HTTP verbs (`GET`, `POST`), HTTP status codes (`500`, `503`), endpoints (`/api/v1/checkout/process`), and correlation IDs (`tx-8921-4f`).
  * **Repository Catalog Matcher (`repo_matcher.py`)**: Computes confidence scores between error stack traces and internal repository catalogs using package path analysis and service naming conventions.
  * **LLM Synthesis & Fallback (`nim_adapter.py`)**: Connects to NVIDIA NIM endpoints (e.g. Llama 3) for executive summaries. Automatically switches to local rule-based synthesis if network endpoints are unreachable.

---

## 4. End-to-End Data Flow Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Engineer as On-Call Engineer
    participant UI as React Frontend (:3000)
    participant Spring as Spring Boot Core (:8080)
    participant Python as Python AI Service (:8000)
    participant Jira as Atlassian Jira Cloud
    participant Email as EmailJS Gateway

    Engineer->>UI: Selects Incident NOVA-1001
    UI->>Spring: GET /api/investigations/NOVA-1001
    Spring->>Jira: GET /rest/api/3/issue/NOVA-1001 + Attachments
    Jira-->>Spring: Returns Ticket JSON & Raw Server Logs
    
    Spring->>Python: POST /api/telemetry/parse (Logs + Description)
    Note over Python: 1. Scrub secrets & PII<br/>2. Extract HTTP codes, endpoints, corrId<br/>3. Match target Git repository
    Python-->>Spring: Returns Telemetry Facts & Repo Matches
    
    Note over Spring: Calculate 100-Point Readiness Score<br/>Generate Polite Clarification Comment
    Spring-->>UI: Returns Investigation DTO
    UI->>Engineer: Renders Dashboard & Holographic Flow Map

    Engineer->>UI: Clicks "Post to Jira" & "Dispatch Email"
    UI->>Spring: POST /api/investigations/NOVA-1001/dispatch
    par Update Jira
        Spring->>Jira: POST /rest/api/3/issue/NOVA-1001/comment
        Jira-->>Spring: 201 Created
    and Notify Team
        Spring->>Email: POST /api/v1.0/email/send
        Email-->>Spring: 200 OK
    end
    Spring-->>UI: Dispatch Confirmed (Audit Log Saved)
    UI->>Engineer: Displays Success Badges & Delivered Status
```

---

## 5. Zero-Trust Security & PII Redaction Pipeline

Enterprise incident reports frequently contain unintended sensitive data, including customer credentials, database connection strings, and authorization tokens. JiraPilot AI enforces a **strict multi-pass sanitization filter**:

```mermaid
flowchart LR
    RawLog[Raw Server Logs / Jira Body] --> RegexFilter[Deterministic Regex Masking]
    
    subgraph Redaction Filters
        RegexFilter --> Mask1["Bearer Tokens: Bearer [REDACTED_TOKEN]"]
        RegexFilter --> Mask2["API Keys: api_key=[REDACTED_KEY]"]
        RegexFilter --> Mask3["Passwords: password=[REDACTED_PASSWORD]"]
        RegexFilter --> Mask4["Email/PII: user@***.com"]
    end
    
    Mask1 & Mask2 & Mask3 & Mask4 --> CleanTelemetry[Sanitized Telemetry Buffer]
    CleanTelemetry --> FastAPIService[Python AI & Storage Engine]
```

### Redaction Rules Enforced:
1. **Authorization Headers**: Matches `Bearer [A-Za-z0-9\-\._~\+\/]+=*` and replaces with `Bearer [REDACTED_TOKEN]`.
2. **Access & Secret Keys**: Matches AWS, GCP, and custom API key patterns (`AKIA...`, `ghp_...`, `sk-...`).
3. **Database Credentials**: Replaces connection string URIs (`postgres://user:password@host...`) with sanitized host references.
4. **Personal Identifiable Information (PII)**: Masks credit card Luhn patterns and personal emails before external LLM synthesis.

---

## 6. Deployment & Runtime Environment

| Tier | Runtime | Build Tool | Production Container | Port |
| :--- | :--- | :--- | :--- | :---: |
| **Frontend UI** | Node.js 20+ / Browser | Vite 5 | Nginx Alpine Container | `3000` |
| **Enterprise Backend** | OpenJDK 21 LTS | Maven 3.9 | Eclipse Temurin 21 Container | `8080` |
| **AI Microservice** | Python 3.12 | pip / Uvicorn | Python 3.12-slim Container | `8000` |
| **Database** | Embedded / Dedicated | JPA Hibernate | PostgreSQL 16 Alpine | `5432` |

All services support independent scaling, environment-driven configuration via `.env` and `application.yml`, and container orchestration via standard Docker Compose manifests.
