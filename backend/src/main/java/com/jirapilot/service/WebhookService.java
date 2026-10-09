package com.jirapilot.service;

import com.jirapilot.model.dto.CreateIssueRequest;
import com.jirapilot.model.dto.JiraWebhookPayload;
import com.jirapilot.model.entity.JiraIssue;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
@RequiredArgsConstructor
public class WebhookService {

    private final TriageWorkflowService workflowService;
    private final Map<String, Long> processedEvents = new ConcurrentHashMap<>();

    public JiraIssue handleJiraWebhook(JiraWebhookPayload payload) {
        if (payload == null || payload.getIssue() == null) {
            log.warn("[WEBHOOK] Received invalid or empty Jira webhook payload");
            return null;
        }

        String eventId = payload.getWebhookEvent() + ":" + payload.getIssue().getKey() + ":" + payload.getTimestamp();
        if (processedEvents.putIfAbsent(eventId, System.currentTimeMillis()) != null) {
            log.info("[WEBHOOK] Idempotent ignore: event {} already processed recently", eventId);
            return null;
        }

        String eventType = payload.getWebhookEvent();
        String issueKey = payload.getIssue().getKey();
        log.info("[WEBHOOK] Processing Jira event '{}' for ticket {}", eventType, issueKey);

        String summary = payload.getIssue().getFields() != null ? payload.getIssue().getFields().getSummary() : "Jira Webhook Issue";
        String description = "";
        if (payload.getIssue().getFields() != null && payload.getIssue().getFields().getDescription() != null) {
            description = payload.getIssue().getFields().getDescription().toString();
        }

        String reporter = "reporter@jira.com";
        if (payload.getIssue().getFields() != null && payload.getIssue().getFields().getReporter() != null) {
            reporter = payload.getIssue().getFields().getReporter().getEmailAddress();
        }

        CreateIssueRequest request = CreateIssueRequest.builder()
                .key(issueKey)
                .summary(summary)
                .description(description)
                .reporter(reporter)
                .build();

        boolean isUpdate = "jira:issue_updated".equalsIgnoreCase(eventType);
        return workflowService.processNewOrUpdatedIssue(request, isUpdate);
    }
}
