package com.jirapilot.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.model.dto.JiraWebhookPayload;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.model.enums.IssueStatus;
import com.jirapilot.service.IssueService;
import com.jirapilot.service.WebhookService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(WebhookController.class)
public class WebhookControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private WebhookService webhookService;

    @MockBean
    private IssueService issueService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void shouldHandleWebhookEvent() throws Exception {
        JiraWebhookPayload payload = new JiraWebhookPayload();
        payload.setWebhookEvent("jira:issue_created");
        payload.setTimestamp(System.currentTimeMillis());

        JiraWebhookPayload.IssueInfo issueInfo = new JiraWebhookPayload.IssueInfo();
        issueInfo.setKey("HACK-1001");
        payload.setIssue(issueInfo);

        JiraIssue processed = JiraIssue.builder()
                .jiraKey("HACK-1001")
                .status(IssueStatus.READY)
                .build();

        when(webhookService.handleJiraWebhook(any())).thenReturn(processed);

        mockMvc.perform(post("/api/webhooks/jira")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(payload)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("PROCESSED"))
                .andExpect(jsonPath("$.jiraKey").value("HACK-1001"));
    }
}
