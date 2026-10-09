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
    private final LogAttachmentService attachmentService;
    private final com.jirapilot.client.JiraClientFactory jiraClientFactory;
    private final Map<String, Long> processedEvents = new ConcurrentHashMap<>();

    @org.springframework.beans.factory.annotation.Value("${jirapilot.jira.project-key:KAN}")
    private String configuredProjectKey;

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

        // Validate project key
        if (issueKey != null && configuredProjectKey != null && !configuredProjectKey.isBlank()) {
            String issueProject = issueKey.contains("-") ? issueKey.split("-")[0] : "";
            if (!issueProject.equalsIgnoreCase(configuredProjectKey) && !issueProject.equalsIgnoreCase("NOVA") && !issueProject.equalsIgnoreCase("KAN")) {
                log.info("[WEBHOOK] Ignoring webhook for issue {} as it does not match configured project ({})", issueKey, configuredProjectKey);
                return null;
            }
        }

        log.info("[WEBHOOK] Processing Jira event '{}' for ticket {}", eventType, issueKey);

        String summary = payload.getIssue().getFields() != null ? payload.getIssue().getFields().getSummary() : "Jira Webhook Issue";
        String description = "";
        if (payload.getIssue().getFields() != null && payload.getIssue().getFields().getDescription() != null) {
            description = payload.getIssue().getFields().getDescription().toString();
        }

        String reporter = "sshankaran202@gmail.com";
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
        JiraIssue issue = workflowService.processNewOrUpdatedIssue(request, isUpdate);

        // Detect and process any newly uploaded attachments
        try {
            var client = jiraClientFactory.getClient();
            var attachments = client.getIssueAttachments(issueKey);
            for (var att : attachments) {
                String filename = att.get("filename");
                String contentUrl = att.get("contentUrl");
                String attId = att.get("id");
                String mimeType = att.get("mimeType");

                if (filename != null && (filename.endsWith(".log") || filename.endsWith(".txt") || filename.endsWith(".json") || filename.endsWith(".gz"))) {
                    log.info("[WEBHOOK ATTACHMENT] Found log attachment '{}' for issue {}", filename, issueKey);
                    byte[] bytes = client.getAttachmentBytes(contentUrl);
                    if (bytes != null && bytes.length > 0) {
                        attachmentService.processLogContent(issue, filename, bytes, mimeType, attId);
                    }
                }
            }
        } catch (Exception e) {
            log.warn("[WEBHOOK ATTACHMENT] Failed to ingest attachments for {}: {}", issueKey, e.getMessage());
        }

        return issue;
    }
}
