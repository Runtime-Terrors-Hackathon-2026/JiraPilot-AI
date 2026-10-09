package com.jirapilot.model.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

import java.util.Map;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class JiraWebhookPayload {
    private String webhookEvent; // jira:issue_created, jira:issue_updated
    private Long timestamp;
    private IssueInfo issue;
    private UserInfo user;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class IssueInfo {
        private String id;
        private String key;
        private Fields fields;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Fields {
        private String summary;
        private Object description;
        private UserInfo reporter;
        private Map<String, Object> environment;
        private Map<String, Object> customfield_10001; // Example custom field
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class UserInfo {
        private String displayName;
        private String emailAddress;
        private String accountId;
    }
}
