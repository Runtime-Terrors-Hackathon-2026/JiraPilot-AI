package com.jirapilot.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.client.PythonAiClient;
import com.jirapilot.model.entity.Investigation;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.repository.InvestigationRepository;
import com.jirapilot.repository.JiraIssueRepository;
import com.jirapilot.service.AuditService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Collections;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/issues")
@RequiredArgsConstructor
public class CodeInvestigationController {

    private final JiraIssueRepository issueRepository;
    private final InvestigationRepository investigationRepository;
    private final PythonAiClient aiClient;
    private final AuditService auditService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @PostMapping("/{key}/code-investigation/run")
    public ResponseEntity<Map<String, Object>> runCodeInvestigation(
            @PathVariable String key,
            @RequestParam(required = false) String repositoryId,
            @RequestParam(required = false) String serviceName
    ) {
        long startTime = System.currentTimeMillis();
        JiraIssue issue = issueRepository.findByJiraKey(key)
                .orElseThrow(() -> new IllegalArgumentException("Issue not found: " + key));

        log.info("[CODE INVESTIGATION] Triggering code-level investigation for issue {}", key);
        Map<String, Object> report = aiClient.runCodeInvestigation(issue, repositoryId, serviceName);

        // Persist code investigation report in Investigation entity
        Investigation investigation = issue.getInvestigation();
        if (investigation == null) {
            investigation = Investigation.builder().jiraIssue(issue).build();
        }

        try {
            investigation.setCodeInvestigationJson(objectMapper.writeValueAsString(report));
            investigation.setCodeInvestigationStatus((String) report.getOrDefault("status", "READY_FOR_REVIEW"));
            investigation.setMatchedRepository((String) report.getOrDefault("repositoryId", repositoryId));
            investigation.setInspectedRevision((String) report.getOrDefault("revision", "a9b47e2f"));
            investigationRepository.save(investigation);
            issue.setInvestigation(investigation);
            issueRepository.save(issue);
        } catch (Exception e) {
            log.warn("Failed to persist code investigation json: {}", e.getMessage());
        }

        auditService.recordEvent(
                issue,
                "CODE_INVESTIGATION_COMPLETED",
                "CODE_ANALYSIS",
                "Inspected source repository " + report.getOrDefault("repositoryName", "") + " and traced execution path.",
                "SUCCESS",
                System.currentTimeMillis() - startTime
        );

        return ResponseEntity.ok(report);
    }

    @GetMapping("/{key}/code-investigation")
    public ResponseEntity<Map<String, Object>> getCodeInvestigation(@PathVariable String key) {
        JiraIssue issue = issueRepository.findByJiraKey(key)
                .orElseThrow(() -> new IllegalArgumentException("Issue not found: " + key));

        Investigation inv = issue.getInvestigation();
        if (inv != null && inv.getCodeInvestigationJson() != null && !inv.getCodeInvestigationJson().isBlank()) {
            try {
                Map<String, Object> cached = objectMapper.readValue(inv.getCodeInvestigationJson(), Map.class);
                return ResponseEntity.ok(cached);
            } catch (Exception e) {
                log.warn("Failed to deserialize cached code investigation: {}", e.getMessage());
            }
        }

        // Run fresh on demand
        return runCodeInvestigation(key, null, null);
    }

    @PostMapping("/{key}/code-investigation/generate-diff")
    public ResponseEntity<Map<String, Object>> generateDiff(
            @PathVariable String key,
            @RequestBody Map<String, String> payload
    ) {
        String investigationId = payload.getOrDefault("investigationId", "INV-CODE-" + key);
        String repositoryId = payload.getOrDefault("repositoryId", "REPO-RES-INV");
        String filePath = payload.getOrDefault("filePath", "src/main/java/com/northstar/inventory/service/ResourceAllocationService.java");
        String targetMethod = payload.getOrDefault("targetMethod", "reserveCircuit");

        Map<String, Object> diff = aiClient.generateCodeDiff(investigationId, repositoryId, filePath, targetMethod);
        return ResponseEntity.ok(diff);
    }

    @PostMapping("/{key}/code-investigation/run-tests")
    public ResponseEntity<Map<String, Object>> runRecommendedTests(
            @PathVariable String key,
            @RequestBody Map<String, Object> payload
    ) {
        long startTime = System.currentTimeMillis();
        String command = (String) payload.getOrDefault("command", "mvn test -Dtest=ResourceAllocationServiceTest");
        String testClass = (String) payload.getOrDefault("testClass", "ResourceAllocationServiceTest");

        Map<String, Object> testResult = aiClient.runRecommendedTests(command, testClass);

        issueRepository.findByJiraKey(key).ifPresent(issue ->
                auditService.recordEvent(
                        issue,
                        "TESTS_EXECUTED",
                        "TESTING",
                        "Executed test suite " + testClass + " via isolated test runner: " + command,
                        (Boolean) testResult.getOrDefault("passed", true) ? "SUCCESS" : "FAILED",
                        System.currentTimeMillis() - startTime
                )
        );

        return ResponseEntity.ok(testResult);
    }

    @GetMapping("/repository/{repoId}/file")
    public ResponseEntity<Map<String, Object>> getRepositoryFile(
            @PathVariable String repoId,
            @RequestParam String path
    ) {
        Map<String, Object> fileData = aiClient.getRepositoryFile(repoId, path);
        if (fileData.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(fileData);
    }
}
