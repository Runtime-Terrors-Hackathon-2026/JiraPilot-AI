package com.jirapilot.controller;

import com.jirapilot.model.dto.IssueResponseDto;
import com.jirapilot.model.dto.JiraWebhookPayload;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.service.IssueService;
import com.jirapilot.service.WebhookService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/webhooks")
@RequiredArgsConstructor
public class WebhookController {

    private final WebhookService webhookService;
    private final IssueService issueService;

    @PostMapping("/jira")
    public ResponseEntity<Map<String, Object>> handleJiraWebhook(@RequestBody JiraWebhookPayload payload) {
        JiraIssue processedIssue = webhookService.handleJiraWebhook(payload);
        if (processedIssue != null) {
            IssueResponseDto dto = issueService.mapToDto(processedIssue);
            return ResponseEntity.ok(Map.of(
                    "status", "PROCESSED",
                    "jiraKey", processedIssue.getJiraKey(),
                    "issueStatus", processedIssue.getStatus().name()
            ));
        }
        return ResponseEntity.ok(Map.of("status", "IGNORED_OR_DUPLICATE"));
    }
}
