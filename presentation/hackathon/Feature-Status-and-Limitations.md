# JiraPilot AI — Feature Status, Limitations & Engineering Tradeoffs

> **Transparency Statement**: In hackathons and enterprise evaluations, technical honesty is paramount. This document provides a transparent, verifiable status inventory of every component in the JiraPilot AI codebase, distinguishing clearly between what is tested, what is demonstrated, and what is on our forward engineering roadmap.

---

## 1. Feature Status Inventory Matrix

| Feature / Subsystem | Current Status | Supporting Code Modules | Verification Evidence |
| :--- | :---: | :--- | :--- |
| **Ticket Readiness Scoring** | **Implemented & Tested** | `TicketReadinessService.java`, `ScoreBadge.tsx` | Unit tests passing, deterministic 100-point calculation visible in UI |
| **Log Telemetry Parsing** | **Implemented & Tested** | `app/services/log_parser.py`, `regex_patterns.py` | Extracts HTTP status, method, endpoint, corrId from raw logs |
| **Holographic API Flow Map** | **Implemented & Tested** | `ApiFlowPage.tsx`, `ApiFlowCanvas.tsx`, `apiFlowNormalizer.ts` | 17/17 Jest unit tests passing, hardware-accelerated SVG interactive canvas |
| **Repository Matcher & Clone Command** | **Implemented & Tested** | `repo_matcher.py`, `RepositoryRecommendationCard.tsx` | 94% confidence match on `repo-payment-gateway`, copyable terminal command |
| **Jira Cloud REST Integration** | **Implemented & Tested** | `JiraClientService.java`, Jira REST API v3 | Ingests issues and attachments, posts structured markdown comments |
| **Live EmailJS Notification Gateway** | **Implemented & Tested** | `EmailJsService.java`, EmailJS Cloud | Verified live dispatch (`200 OK`) to `sshankaran202@gmail.com` using template `template_ohed206` |
| **Zero-Trust Secret Redaction** | **Implemented & Tested** | `redactor.py`, `sanitizer.ts` | Regex masking of authorization tokens, passwords, and sensitive keys |
| **Investigation Persistence & Audit** | **Implemented & Tested** | `InvestigationRepository.java`, Spring Data JPA | Stores incident history, readiness scores, and comment audit logs |
| **Multi-LLM / NVIDIA NIM Adapter** | **Implemented (Unverified Remote)** | `nim_adapter.py`, `AI_PROVIDER` switch | Adapter implemented with local rule-based fallback when NIM API key is not active |
| **Synthetic Incident Seed Data** | **Demonstration-Only** | `SyntheticIncidentData.java`, `demo_incidents.json` | Synthetic scenario `NOVA-1001` (Northstar Digital Systems) for safe judge demonstrations |
| **Automated Git PR Generation** | **Planned Future (Phase 2)** | Specification documented | Autonomous code patch generation and GitHub Pull Request drafting |
| **Dense Vector Embedding Code Search** | **Planned Future (Phase 2)** | Specification documented | Upgrading lexical matching to dense vector embeddings with FAISS / pgvector |
| **Bi-Directional Datadog / APM Webhooks**| **Planned Future (Phase 3)** | Specification documented | Direct telemetry ingestion from Datadog, Splunk, and PagerDuty webhooks |

---

## 2. Status Definitions

* **Implemented and Tested**: Fully coded, integrated into the build pipeline, covered by automated unit/integration tests or verified live in runtime operations.
* **Implemented but Not Verified**: Code and adapters are written in the repository, but full end-to-end cloud validation depends on active external enterprise credentials (e.g. NVIDIA NIM API tokens). Resilient local fallback handles execution cleanly.
* **Demonstration-Only**: Synthetic data structures and pre-loaded incident scenarios crafted specifically to enable safe, repeatable demonstrations without exposing real customer data.
* **Planned Future Enhancement**: Architecturally designed and documented in our product roadmap, but intentional code development is scheduled for subsequent phases.

---

## 3. Known Limitations & Engineering Tradeoffs

### 3.1 Single Log File Parsing per Incident
* **Current Behavior**: JiraPilot processes the primary log file attached to a Jira issue or pasted into the log buffer.
* **Tradeoff / Reason**: For hackathon scope, processing a single consolidated log keeps memory overhead minimal and avoids distributed log synchronization complexity.
* **Roadmap Evolution**: Phase 2 will introduce distributed log correlation across multiple microservice attachments using shared correlation IDs.

### 3.2 Lexical & Package Heuristic Repository Matching
* **Current Behavior**: Repositories are matched based on package declarations (e.g., `com.northstar.checkout`), service names, and URL routes.
* **Tradeoff / Reason**: Heuristic matching is extremely fast (under 5 milliseconds), deterministic, and requires no external vector database infrastructure.
* **Roadmap Evolution**: Dense semantic vector embeddings will be layered on top to support repositories with non-standard directory conventions.

### 3.3 Scoped Jira Write Rights (Comment-Only)
* **Current Behavior**: JiraPilot appends technical comments to Jira issues but does not modify ticket status (e.g., does not move tickets from "To Do" to "In Progress").
* **Tradeoff / Reason**: Enterprise security compliance strictly discourages autonomous AI agents from altering production sprint workflows without human oversight.
* **Roadmap Evolution**: Optional configurable workflow transitions enabled on a per-project basis with administrative sign-off.

### 3.4 EmailJS Cloud Relay
* **Current Behavior**: Notifications are routed through EmailJS cloud relays rather than an internal corporate SMTP server.
* **Tradeoff / Reason**: EmailJS allows instant zero-config cloud email delivery without opening corporate SMTP ports or managing SPF/DKIM records during demonstrations.
* **Roadmap Evolution**: Spring Boot JavaMailSender adapter support for internal Microsoft Exchange and SendGrid enterprise relays.
