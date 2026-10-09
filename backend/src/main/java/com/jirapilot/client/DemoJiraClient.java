package com.jirapilot.client;

import com.jirapilot.model.dto.CreateIssueRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Component("demoJiraClient")
public class DemoJiraClient implements JiraClient {

    private final Map<String, List<Map<String, Object>>> issueComments = new ConcurrentHashMap<>();

    @Override
    public CreateIssueRequest getIssue(String issueKey) {
        log.info("[DEMO JIRA] Fetching synthetic issue details for {}", issueKey);
        return CreateIssueRequest.builder()
                .key(issueKey)
                .summary("Circuit creation API failing intermittently")
                .description("Circuit creation fails during provisioning in SANDBOX environment.")
                .reporter("engineer@example.com")
                .environment("SANDBOX")
                .apiDetails("POST /api/circuit/provision")
                .logs("2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001")
                .requestPayload("{\"circuitId\":\"TEST-1001\",\"customerId\":\"TEST-CUST-001\",\"nfid\":\"TEST-NFID-1001\"}")
                .errorMessage("HTTP 500 Duplicate NFID")
                .expectedBehavior("201 Created with active circuit state")
                .actualBehavior("500 Internal Server Error from PEDS service")
                .build();
    }

    @Override
    public boolean addComment(String issueKey, String commentBody) {
        log.info("[DEMO JIRA] Simulated Jira comment added to issue {}:\n{}", issueKey, commentBody);
        issueComments.computeIfAbsent(issueKey, k -> new ArrayList<>()).add(Map.of(
                "id", UUID.randomUUID().toString(),
                "author", "JiraPilot AI Agent",
                "body", commentBody,
                "created", new Date().toString()
        ));
        return true;
    }

    @Override
    public boolean updateIssueStatus(String issueKey, String statusName) {
        log.info("[DEMO JIRA] Simulated Jira issue {} transitioned to status: {}", issueKey, statusName);
        return true;
    }

    @Override
    public List<Map<String, Object>> getComments(String issueKey) {
        return issueComments.getOrDefault(issueKey, Collections.emptyList());
    }

    @Override
    public List<String> getProjectIssueKeys(String projectKey) {
        return List.of("HACK-1001", "HACK-1002", "HACK-1003", "HACK-1004");
    }
}
