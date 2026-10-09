package com.jirapilot.controller;

import com.jirapilot.model.dto.CreateIssueRequest;
import com.jirapilot.model.dto.IssueResponseDto;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.repository.JiraIssueRepository;
import com.jirapilot.service.IssueService;
import com.jirapilot.service.LogAttachmentService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/demo")
@RequiredArgsConstructor
public class DemoController {

    private final IssueService issueService;
    private final LogAttachmentService logAttachmentService;
    private final JiraIssueRepository jiraIssueRepository;

    @PostMapping("/load-data")
    public ResponseEntity<Map<String, Object>> loadDemoData() {
        log.info("[DEMO] Populating comprehensive demo dataset (NOVA-101 to NOVA-105 and HACK scenarios)...");
        List<CreateIssueRequest> demoTickets = createDemoTicketsList();
        List<IssueResponseDto> results = new ArrayList<>();

        for (CreateIssueRequest ticket : demoTickets) {
            IssueResponseDto dto = issueService.createOrUpdateIssue(ticket);
            results.add(dto);

            // Auto-attach corresponding sample log file if available
            attachSampleLogForTicket(ticket.getKey());
        }

        return ResponseEntity.ok(Map.of(
                "status", "SUCCESS",
                "message", "Demo dataset and microservice incident logs loaded successfully",
                "loadedCount", results.size()
        ));
    }

    @PostMapping("/simulate-issue")
    public ResponseEntity<IssueResponseDto> simulateIssue(@RequestBody CreateIssueRequest request) {
        return ResponseEntity.ok(issueService.createOrUpdateIssue(request));
    }

    private void attachSampleLogForTicket(String jiraKey) {
        String logFileName = switch (jiraKey) {
            case "NOVA-101" -> "NOVA-101-resource-inventory-conflict.log";
            case "NOVA-102" -> "NOVA-102-workflow-orchestrator-timeout.log";
            case "NOVA-103" -> "NOVA-103-integration-gateway-ratelimit.log";
            case "NOVA-104" -> "NOVA-104-request-validation-engine-schema.json";
            case "NOVA-105" -> "NOVA-105-capacity-planning-shortage.log";
            case "HACK-1001" -> "duplicate-resource-error.log";
            case "HACK-1003" -> "downstream-timeout.json";
            default -> null;
        };

        if (logFileName == null) return;

        Path logPath = Paths.get("demo-data", "logs", logFileName);
        if (!Files.exists(logPath)) {
            logPath = Paths.get("..", "demo-data", "logs", logFileName);
        }

        if (Files.exists(logPath)) {
            try {
                byte[] rawBytes = Files.readAllBytes(logPath);
                JiraIssue issue = jiraIssueRepository.findByJiraKey(jiraKey).orElse(null);
                if (issue != null) {
                    String mimeType = logFileName.endsWith(".json") ? "application/json" : "text/plain";
                    logAttachmentService.processLogContent(issue, logFileName, rawBytes, mimeType, "demo-att-" + jiraKey);
                    log.info("[DEMO] Attached and analyzed sample log {} for ticket {}", logFileName, jiraKey);
                }
            } catch (Exception e) {
                log.warn("[DEMO] Could not attach log file {} to {}: {}", logFileName, jiraKey, e.getMessage());
            }
        }
    }

    private List<CreateIssueRequest> createDemoTicketsList() {
        return List.of(
                // Scenario 1: NOVA-101 - Resource Inventory Service 409 Conflict
                CreateIssueRequest.builder()
                        .key("NOVA-101")
                        .summary("Duplicate resource allocation collision in ResourceInventoryService")
                        .description("Automated allocation failed with HTTP 409 Conflict during circuit provisioning in STAGING-US-EAST.")
                        .reporter("siva.architect@northstar.example")
                        .environment("STAGING-US-EAST")
                        .apiDetails("POST /api/v1/resources/allocate")
                        .requestPayload("{\n  \"resourceId\": \"DEMO-RESOURCE-1001\",\n  \"site\": \"SITE-NYC-01\",\n  \"bandwidth\": 1000\n}")
                        .responsePayload("{\n  \"timestamp\": \"2026-10-09T10:14:22Z\",\n  \"status\": 409,\n  \"error\": \"Conflict\",\n  \"message\": \"Pre-existing allocation detected for resource ID: DEMO-RESOURCE-1001\"\n}")
                        .errorMessage("org.springframework.dao.DataIntegrityViolationException: Pre-existing allocation detected")
                        .expectedBehavior("HTTP 201 Created with reserved resource record")
                        .actualBehavior("HTTP 409 Conflict with unique constraint violation on synthetic_resources")
                        .replicationSteps("1. Allocate resource DEMO-RESOURCE-1001\n2. Attempt duplicate reservation in site SITE-NYC-01")
                        .build(),

                // Scenario 2: NOVA-102 - Workflow Orchestrator 504 Timeout
                CreateIssueRequest.builder()
                        .key("NOVA-102")
                        .summary("SAGA transaction timeout in Workflow Orchestrator calling Inventory")
                        .description("SagaStepExecutor timed out waiting for socket read from downstream resource-inventory-service.")
                        .reporter("alex.mercer@northstar.example")
                        .environment("PROD-NORTHSTAR-01")
                        .apiDetails("POST /api/v1/workflows/start")
                        .requestPayload("{\n  \"sagaId\": \"SAGA-99120\",\n  \"serviceType\": \"CLOUD_CIRCUIT\",\n  \"resourceId\": \"DEMO-RESOURCE-1002\"\n}")
                        .errorMessage("java.net.SocketTimeoutException: Read timed out after 5000ms")
                        .expectedBehavior("HTTP 200 OK saga completion within 2500ms")
                        .actualBehavior("HTTP 504 Gateway Timeout after 5000ms socket read failure")
                        .replicationSteps("1. Trigger SAGA-99120\n2. Simulate downstream delay > 5000ms")
                        .build(),

                // Scenario 3: NOVA-103 - Integration Gateway 429 Rate Limit
                CreateIssueRequest.builder()
                        .key("NOVA-103")
                        .summary("Rate limit 429 exhaustion on Integration Gateway partner routes")
                        .description("Partner client exceeded provisioned transactions per second quota on route /api/v1/gateway/dispatch.")
                        .reporter("devops.oncall@northstar.example")
                        .environment("GATEWAY-EDGE-PROD")
                        .apiDetails("POST /api/v1/gateway/dispatch")
                        .errorMessage("org.springframework.web.server.ResponseStatusException: 429 TOO_MANY_REQUESTS")
                        .expectedBehavior("HTTP 200 OK payload dispatched to partner queue")
                        .actualBehavior("HTTP 429 Too Many Requests token bucket exhausted")
                        .build(),

                // Scenario 4: NOVA-104 - Request Validation Engine 400 Bad Request
                CreateIssueRequest.builder()
                        .key("NOVA-104")
                        .summary("Schema validation rejection for missing bandwidth parameter")
                        .description("Request validation engine rejected payload because mandatory field 'bandwidthMbps' was omitted.")
                        .reporter("qa.automated@northstar.example")
                        .environment("DEV-INTEGRATION")
                        .apiDetails("POST /api/v1/validation/evaluate")
                        .requestPayload("{\n  \"serviceType\": \"CLOUD_CIRCUIT\",\n  \"site\": \"SITE-BOS-02\"\n}")
                        .errorMessage("SchemaValidationException: Mandatory field 'bandwidthMbps' cannot be null")
                        .expectedBehavior("HTTP 200 OK contract validated")
                        .actualBehavior("HTTP 400 Bad Request missing mandatory field bandwidthMbps")
                        .build(),

                // Scenario 5: NOVA-105 - Capacity Planning API 500 Shortage
                CreateIssueRequest.builder()
                        .key("NOVA-105")
                        .summary("Insufficient capacity error during 10Gbps pipeline reservation")
                        .description("Capacity reservation failed on node NODE-DENVER-01 due to insufficient allocatable reserve.")
                        .reporter("network.planner@northstar.example")
                        .environment("PROD-DENVER-CORE")
                        .apiDetails("POST /api/v1/capacity/reserve")
                        .errorMessage("InsufficientCapacityException: Node NODE-DENVER-01 is exhausted. Available: 3400Mbps, Requested: 10000Mbps")
                        .expectedBehavior("HTTP 200 OK capacity reserved on NODE-DENVER-01")
                        .actualBehavior("HTTP 500 Insufficient Capacity available 3400Mbps < requested 10000Mbps")
                        .build(),

                // Backward-compatible Hackathon Scenario: HACK-1001
                CreateIssueRequest.builder()
                        .key("HACK-1001")
                        .summary("Circuit creation API failing")
                        .description("Circuit creation fails intermittently during provisioning in SANDBOX environment.")
                        .reporter("alice.engineer@example.com")
                        .environment("SANDBOX")
                        .apiDetails("POST /api/circuit/provision")
                        .logs("2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001\n" +
                              "2026-10-08 10:31:43 ERROR [WFM] Downstream request failed status=500 endpoint=/api/circuit/provision correlationId=CORR-1001")
                        .requestPayload("{\n  \"circuitId\": \"TEST-CKT-1001\",\n  \"customerId\": \"TEST-CUST-8821\",\n  \"nfid\": \"TEST-NFID-1001\",\n  \"bandwidthMbps\": 1000\n}")
                        .errorMessage("HTTP 500 Internal Server Error: Duplicate NFID detected")
                        .expectedBehavior("HTTP 201 Created with provisioned circuit object")
                        .actualBehavior("HTTP 500 with SQL unique constraint violation on PEDS")
                        .replicationSteps("1. Send POST request to /api/circuit/provision\n2. Supply NFID TEST-NFID-1001\n3. Observe duplicate rejection")
                        .build(),

                // Backward-compatible Hackathon Scenario: HACK-1002 (Incomplete Ticket)
                CreateIssueRequest.builder()
                        .key("HACK-1002")
                        .summary("API is failing. Please check.")
                        .description("API is failing. Please check why circuits are not being created.")
                        .reporter("bob.developer@example.com")
                        .environment("DEV")
                        .build()
        );
    }
}
