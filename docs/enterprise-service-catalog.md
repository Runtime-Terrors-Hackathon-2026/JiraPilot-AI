# Northstar Digital Systems - Enterprise Service Catalog

> **CONFIDENTIALITY & SYNTHETIC DATA NOTICE**  
> All services, hostnames, identifiers, and schemas described in this catalog are 100% fictional simulations invented for the **JiraPilot AI** demonstration platform at **Northstar Digital Systems** (`northstar-labs`). They do not represent, replicate, or map to any actual enterprise internal production systems or proprietary infrastructure.

---

## Catalog Overview

| Functional Domain | Group Name | Number of Services | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Operations** | Service Operations Group | 3 | Customer request ingestion, end-to-end workflow execution, and semantic payload validation. |
| **Infrastructure** | Network Resource Group | 3 | Hardware/virtual resource provisioning, capacity forecast modeling, and topological dependency mapping. |
| **Integration** | Integration Platform Group | 3 | Centralized API gateway routing, reliable asynchronous event delivery, and third-party partner ingress. |
| **Reliability** | Reliability Engineering Group | 3 | Anomaly triage, distributed correlation, and automated self-healing remediation coordination. |

---

## 1. Service Operations Group

### 1.1 `service-request-api`
* **Service ID:** `service-request-api`
* **Display Name:** Service Request Intake API
* **Tier:** Tier-1
* **Owner Team:** Core Operations Engineering (`team-core-ops@internal.northstar.example.com`)
* **Base Path:** `http://service-request-api.internal.northstar.example.com:8081/api/v1`
* **Health Check:** `GET /actuator/health`
* **Purpose:** Single entry point for enterprise clients and portals to submit, update, and query the status of digital service lifecycle requests.
* **Dependencies:** `request-validation-engine`, `workflow-orchestrator`, `topology-registry`
* **Failure Modes:**
  * Request payload validation timeout (`HTTP 504`)
  * Downstream queue backlog / capacity throttled (`HTTP 429`)
  * Database lock timeout during high concurrent order submissions (`HTTP 500`)

#### Endpoints
* **`POST /api/v1/requests`**
  * *Summary:* Create a new digital service provisioning request.
  * *Request Body:*
    ```json
    {
      "customerId": "DEMO-CUST-8041",
      "requestType": "PROVISION_CIRCUIT",
      "serviceTier": "PREMIUM",
      "parameters": {
        "bandwidthMbps": 1000,
        "region": "us-east-zone-1"
      }
    }
    ```
  * *Response Body (201 Created):*
    ```json
    {
      "requestId": "REQ-DEMO-9001",
      "status": "VALIDATED",
      "trackingCorrelationId": "CORR-DEMO-8910",
      "createdAt": "2026-10-09T10:00:00Z"
    }
    ```
* **`GET /api/v1/requests/{requestId}`**
  * *Summary:* Retrieve current status and workflow progression of a request.
  * *Response Body (200 OK):*
    ```json
    {
      "requestId": "REQ-DEMO-9001",
      "status": "PROCESSING",
      "activeStep": "RESOURCE_ALLOCATION",
      "percentComplete": 45
    }
    ```

---

### 1.2 `workflow-orchestrator`
* **Service ID:** `workflow-orchestrator`
* **Display Name:** Distributed Workflow Orchestrator
* **Tier:** Tier-1
* **Owner Team:** Automation & Orchestration Squad (`team-orchestration@internal.northstar.example.com`)
* **Base Path:** `http://workflow-orchestrator.internal.northstar.example.com:8082/api/v1`
* **Health Check:** `GET /healthz`
* **Purpose:** State machine engine that coordinates multi-step business transactions across network resource systems and integration pipelines.
* **Dependencies:** `resource-inventory-service`, `event-delivery-service`, `recovery-coordinator`
* **Failure Modes:**
  * SAGA compensation step timeout
  * Redis distributed lock lease expiration
  * Unhandled step exception causing stuck workflow state

#### Endpoints
* **`POST /api/v1/workflows/start`**
  * *Summary:* Launch an asynchronous multi-stage orchestration pipeline.
  * *Request Body:*
    ```json
    {
      "workflowType": "CIRCUIT_LIFECYCLE",
      "initiatorId": "REQ-DEMO-9001",
      "steps": ["VALIDATE", "ALLOCATE_IP", "PROVISION_PORT", "NOTIFY"]
    }
    ```
  * *Response Body (202 Accepted):*
    ```json
    {
      "executionId": "WF-EXEC-5021",
      "status": "RUNNING"
    }
    ```

---

### 1.3 `request-validation-engine`
* **Service ID:** `request-validation-engine`
* **Display Name:** Policy & Request Validation Engine
* **Tier:** Tier-2
* **Owner Team:** Governance & Policy Squad (`team-governance@internal.northstar.example.com`)
* **Base Path:** `http://request-validation-engine.internal.northstar.example.com:8083/api/v1`
* **Health Check:** `GET /health`
* **Purpose:** Evaluates contract conformity, schema compliance, SLA entitlements, and policy checks prior to orchestration.
* **Dependencies:** `topology-registry`
* **Failure Modes:**
  * Outdated schema definition cache
  * Policy rule evaluation stack overflow on deep recursive JSON rules

#### Endpoints
* **`POST /api/v1/validate`**
  * *Summary:* Execute validation checks against defined enterprise policy rules.
  * *Request Body:*
    ```json
    {
      "entityType": "SERVICE_ORDER",
      "payload": { "bandwidthMbps": -50 }
    }
    ```
  * *Response Body (400 Bad Request):*
    ```json
    {
      "valid": false,
      "errors": ["bandwidthMbps must be a positive integer >= 10"]
    }
    ```

---

## 2. Network Resource Group

### 2.1 `resource-inventory-service`
* **Service ID:** `resource-inventory-service`
* **Display Name:** Core Network Resource Inventory
* **Tier:** Tier-1
* **Owner Team:** Network Infrastructure Team (`team-net-infra@internal.northstar.example.com`)
* **Base Path:** `http://resource-inventory-service.internal.northstar.example.com:8084/api/v1`
* **Health Check:** `GET /actuator/health`
* **Purpose:** Authoritative inventory database storing allocation states of network nodes, IP ranges, port assignments, and virtual circuits.
* **Dependencies:** `topology-registry`, `capacity-planning-api`
* **Failure Modes:**
  * Duplicate resource allocation conflict (`HTTP 409 Conflict`)
  * Database connection pool exhaustion (`503 Service Unavailable`)
  * Stale cache reads leading to double-booking of IP blocks

#### Endpoints
* **`POST /api/v1/resources/allocate`**
  * *Summary:* Allocate a synthetic network asset or virtual circuit.
  * *Request Body:*
    ```json
    {
      "resourceType": "VIRTUAL_CIRCUIT",
      "siteId": "SITE-NYC-01",
      "requestedCapacityGbps": 10
    }
    ```
  * *Response Body (200 OK):*
    ```json
    {
      "resourceId": "DEMO-RESOURCE-1001",
      "allocatedPort": "ETH-1/0/4",
      "status": "RESERVED"
    }
    ```

---

### 2.2 `capacity-planning-api`
* **Service ID:** `capacity-planning-api`
* **Display Name:** Capacity Planning & Forecast API
* **Tier:** Tier-3
* **Owner Team:** Capacity Analytics Group (`team-capacity@internal.northstar.example.com`)
* **Base Path:** `http://capacity-planning-api.internal.northstar.example.com:8085/api/v1`
* **Health Check:** `GET /status`
* **Purpose:** Computes headroom forecasts, utilization thresholds, and congestion predictions across fictional network regions.
* **Dependencies:** `resource-inventory-service`
* **Failure Modes:**
  * Heavy compute model memory saturation (`OOMKilled`)
  * Matrix calculation timeout during global topology recalculation

---

### 2.3 `topology-registry`
* **Service ID:** `topology-registry`
* **Display Name:** Network Topology Graph Registry
* **Tier:** Tier-2
* **Owner Team:** Graph & Network Architecture (`team-topology@internal.northstar.example.com`)
* **Base Path:** `http://topology-registry.internal.northstar.example.com:8086/api/v1`
* **Health Check:** `GET /health`
* **Purpose:** Graph representation of interconnected nodes, edge routers, transits, and inter-datacenter links.
* **Dependencies:** *None (Authoritative Graph Core)*
* **Failure Modes:**
  * Graph traversal cycle detection failure
  * Read replica lag exceeding 5 seconds

---

## 3. Integration Platform Group

### 3.1 `integration-gateway`
* **Service ID:** `integration-gateway`
* **Display Name:** Enterprise Edge Integration Gateway
* **Tier:** Tier-1
* **Owner Team:** Edge Platform Team (`team-gateway@internal.northstar.example.com`)
* **Base Path:** `http://integration-gateway.internal.northstar.example.com:8087`
* **Health Check:** `GET /healthz`
* **Purpose:** Ingress reverse proxy, OAuth2/mTLS token termination, rate limiting, and request sanitization.
* **Dependencies:** `partner-connect-api`, `service-request-api`
* **Failure Modes:**
  * Token expiration/clock skew rejection (`HTTP 401 Unauthorized`)
  * Rate limit bucket exhaust (`HTTP 429 Too Many Requests`)
  * Downstream socket timeout (`HTTP 504 Gateway Timeout`)

---

### 3.2 `event-delivery-service`
* **Service ID:** `event-delivery-service`
* **Display Name:** Reliable Event Delivery Service
* **Tier:** Tier-1
* **Owner Team:** Messaging Platform (`team-messaging@internal.northstar.example.com`)
* **Base Path:** `http://event-delivery-service.internal.northstar.example.com:8088/api/v1`
* **Health Check:** `GET /actuator/health`
* **Purpose:** Kafka/RabbitMQ enterprise bus adapter ensuring at-least-once message delivery, schema registry checks, and dead-letter queues.
* **Dependencies:** *Internal Kafka Brokers*
* **Failure Modes:**
  * Dead-letter queue partition overflow
  * Schema version mismatch deserialization failure (`SerializationException`)

---

### 3.3 `partner-connect-api`
* **Service ID:** `partner-connect-api`
* **Display Name:** Partner & External Carrier Connector
* **Tier:** Tier-2
* **Owner Team:** B2B Integration Squad (`team-b2b@internal.northstar.example.com`)
* **Base Path:** `http://partner-connect-api.internal.northstar.example.com:8089/api/v1`
* **Health Check:** `GET /health`
* **Purpose:** Outbound webhook and API mediation for simulated third-party telecom carriers and hardware vendors.
* **Dependencies:** `integration-gateway`
* **Failure Modes:**
  * External partner SSL handshake failure
  * Partner endpoint intermittent 502 Bad Gateway

---

## 4. Reliability Engineering Group

### 4.1 `incident-intelligence-service`
* **Service ID:** `incident-intelligence-service`
* **Display Name:** Incident Intelligence & AI Triage Engine
* **Tier:** Tier-1
* **Owner Team:** Site Reliability Operations (`team-sre@internal.northstar.example.com`)
* **Base Path:** `http://incident-intelligence.internal.northstar.example.com:8090/api/v1`
* **Health Check:** `GET /health`
* **Purpose:** Real-time semantic analysis of error tickets, log telemetry aggregation, automated readiness assessment, and root cause synthesis.
* **Dependencies:** `log-correlation-engine`, `recovery-coordinator`
* **Failure Modes:**
  * LLM inference timeout (>15 seconds)
  * Vector store similarity search index lock

---

### 4.2 `log-correlation-engine`
* **Service ID:** `log-correlation-engine`
* **Display Name:** Distributed Log & Trace Correlation Engine
* **Tier:** Tier-2
* **Owner Team:** Observability Engineering (`team-observability@internal.northstar.example.com`)
* **Base Path:** `http://log-correlation-engine.internal.northstar.example.com:8091/api/v1`
* **Health Check:** `GET /actuator/health`
* **Purpose:** Ingests distributed trace spans and syslog streams; groups disparate errors under unique correlation IDs (`CORR-DEMO-XXXX`).
* **Dependencies:** `event-delivery-service`
* **Failure Modes:**
  * Trace buffer buffer-overflow drop events
  * Elasticsearch search cluster yellow state during high indexing

---

### 4.3 `recovery-coordinator`
* **Service ID:** `recovery-coordinator`
* **Display Name:** Automated Recovery & Self-Healing Coordinator
* **Tier:** Tier-2
* **Owner Team:** Autonomous Reliability Squad (`team-autorecovery@internal.northstar.example.com`)
* **Base Path:** `http://recovery-coordinator.internal.northstar.example.com:8092/api/v1`
* **Health Check:** `GET /health`
* **Purpose:** Executes safe automated runbooks (circuit breaker resets, pod restarts, cache invalidations) for verified deterministic incidents.
* **Dependencies:** `workflow-orchestrator`, `topology-registry`
* **Failure Modes:**
  * Runbook safety guardrail trigger (aborting restart on cluster instability)
  * Idempotency token mismatch on retry
