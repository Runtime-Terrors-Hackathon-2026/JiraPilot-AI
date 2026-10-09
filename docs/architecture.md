# JiraPilot AI - Architecture & System Design
**Fictional Organization:** Northstar Digital Systems (`northstar-labs`)  
**Product:** JiraPilot AI (Synthetic Jira Project: `NOVA`)  
**Document Version:** 1.0.0 (Public-Safe Synthetic Architecture)

---

## 1. System Vision & Overview

**JiraPilot AI** is an autonomous engineering productivity and incident triage platform built for **Northstar Digital Systems**. When Jira issues are filed against simulated enterprise services (such as `resource-inventory-service` or `workflow-orchestrator`), JiraPilot AI:

1. **Evaluates Ticket Readiness:** Parses the issue to ensure sufficient investigation data exists (logs, payloads, API endpoints, errors, expected vs. actual behaviors).
2. **Autonomous Clarification Loop:** If critical information is missing, it calculates a readiness score, posts a structured triage comment to Jira, and places the ticket into `WAITING_FOR_INFO`.
3. **Deep AI Investigation:** If sufficient data exists, it correlates distributed logs, identifies affected APIs, analyzes payloads, synthesizes root causes with high confidence, produces developer reproduction curl commands, and outputs an enterprise Root Cause Analysis (RCA).
4. **Interactive Dashboard:** Streams investigation telemetry and real-time status to an enterprise operations console.

---

## 2. High-Level Architecture (C4 Model)

```mermaid
flowchart TB
    subgraph Users["Engineers & Systems"]
        Engineer["Software Engineer / SRE"]
        Reporter["Incident Reporter / QA"]
        JiraCloud["Atlassian Jira Cloud (Project NOVA)"]
    end

    subgraph JiraPilotPlatform["JiraPilot AI Platform"]
        UI["React Web Console\n(Vite + Tailwind, Port 3000)"]
        
        subgraph BackendTier["Orchestration Engine (Java 21 Spring Boot, Port 8080)"]
            JiraAdapter["Jira Webhook & REST Adapter"]
            TriageOrchestrator["Triage & Investigation Orchestrator"]
            AuditService["Audit & Notification Service"]
            DataRepo["Spring Data JPA Repository"]
        end

        subgraph AITier["AI Intelligence Engine (Python 3.12 FastAPI, Port 8000)"]
            Validator["Payload & Contract Validator"]
            LogCorrelator["Log Parser & Correlation Engine"]
            RCAEngine["Root Cause Synthesizer & LLM Agent"]
            SimilaritySearch["Historical Incident Vector Index"]
        end

        subgraph Storage["Storage Tier"]
            Postgres[("PostgreSQL / H2 Database")]
        end
    end

    subgraph NorthstarServices["Simulated Northstar Digital Systems Services"]
        SvcOps["Service Operations Group\n(service-request-api, workflow-orchestrator)"]
        NetRes["Network Resource Group\n(resource-inventory-service, topology-registry)"]
        Integ["Integration Platform Group\n(integration-gateway, event-delivery-service)"]
        RelEng["Reliability Engineering Group\n(log-correlation-engine, recovery-coordinator)"]
    end

    Reporter -->|File issue / comment| JiraCloud
    JiraCloud -->|Webhook / Polling| JiraAdapter
    JiraAdapter --> TriageOrchestrator
    TriageOrchestrator -->|REST Ingestion| Validator
    TriageOrchestrator -->|REST Investigation| RCAEngine
    Validator --> LogCorrelator
    RCAEngine --> SimilaritySearch
    TriageOrchestrator --> DataRepo
    DataRepo --> Postgres
    TriageOrchestrator -->|Post Triage / RCA Comment| JiraCloud
    TriageOrchestrator --> AuditService
    Engineer -->|Review & Action| UI
    UI -->|REST API| TriageOrchestrator
    LogCorrelator -.->|Ingests Telemetry| NorthstarServices
```

---

## 3. Sequence & Data Flow

### 3.1 Workflow A: Incomplete Ticket Triage

```mermaid
sequenceDiagram
    autonumber
    participant Reporter as Incident Reporter
    participant Jira as Jira Cloud (NOVA)
    participant Java as Java Orchestrator (8080)
    participant Python as Python AI Service (8000)

    Reporter->>Jira: Submits issue NOVA-103 (e.g. "Circuit fails randomly")
    Jira->>Java: Ingests ticket (Webhook / Sync)
    Java->>Python: POST /api/v1/validate (Ticket description & fields)
    Python->>Python: Inspects fields (logs missing, payload missing)
    Python-->>Java: Returns ValidationResponse (readiness: 30%, isComplete: false)
    Java->>Jira: Posts structured comment requesting missing logs & API endpoints
    Java->>Jira: Transitions status to "WAITING_FOR_INFO"
    Java->>Java: Records audit event & dispatches reporter notification
```

### 3.2 Workflow B: Complete Ticket Investigation & RCA Synthesis

```mermaid
sequenceDiagram
    autonumber
    participant Reporter as Incident Reporter
    participant Jira as Jira Cloud (NOVA)
    participant Java as Java Orchestrator (8080)
    participant Python as Python AI Service (8000)

    Reporter->>Jira: Submits complete issue NOVA-101 (Logs, Payloads, Stack trace)
    Jira->>Java: Ingests ticket
    Java->>Python: POST /api/v1/validate
    Python-->>Java: Returns ValidationResponse (readiness: 95%, isComplete: true)
    Java->>Java: Sets status to "INVESTIGATING"
    Java->>Python: POST /api/v1/investigate
    Python->>Python: Parses Spring Boot stack traces & correlation IDs
    Python->>Python: Identifies affected service (resource-inventory-service)
    Python->>Python: Matches historical incidents (NOVA-122 deadlock, NOVA-118 collision)
    Python->>Python: Generates reproduction curl & developer steps
    Python-->>Java: Returns InvestigationResponse (RCA document, confidence: 0.95)
    Java->>Jira: Posts comprehensive technical RCA comment
    Java->>Jira: Transitions status to "INVESTIGATION_COMPLETED"
    Java->>Java: Persists investigation details to database
```

---

## 4. Component Responsibilities

### 4.1 Java Backend Orchestrator (`backend/`)
* **Technology:** Java 21, Spring Boot 3.2.5, Maven, Spring Data JPA, Spring Web.
* **Responsibilities:**
  * Jira Cloud REST API integration (issue fetch, comment post, status transition).
  * Webhook listener and scheduled poller.
  * State lifecycle management (`OPEN`, `WAITING_FOR_INFO`, `INVESTIGATING`, `COMPLETED`).
  * Inter-service REST orchestration with the Python AI service.
  * Audit logging and email notification workflows.
  * Dashboard REST endpoints (`/api/tickets`, `/api/tickets/{key}`, `/api/audit-logs`).

### 4.2 Python AI Intelligence Service (`ai-service/`)
* **Technology:** Python 3.12, FastAPI, Pydantic, httpx, jsonschema.
* **Responsibilities:**
  * Semantic ticket completeness validation (`/api/v1/validate`).
  * Distributed log parsing, regex timestamp alignment, and stack trace parsing (`/api/v1/logs/parse`).
  * Microservice API endpoint mapping from Northstar Service Catalog.
  * RCA synthesis and synthetic reproduction payload generation (`/api/v1/investigate`).
  * Vector similarity search across synthetic historical incidents (`/api/v1/incidents/similar`).

### 4.3 Frontend Web Console (`frontend/`)
* **Technology:** React 18, TypeScript, Vite, Tailwind CSS, Lucide icons.
* **Responsibilities:**
  * Clean, high-density enterprise dashboard (inspired by Linear and Notion).
  * Real-time ticket table with readiness scores, service badges, and status pills.
  * Deep-dive investigation view (stack traces, reproduction curl, historical incident comparisons).
  * Manual trigger controls: "Sync Jira", "Run AI Investigation", "Notify Reporter".
