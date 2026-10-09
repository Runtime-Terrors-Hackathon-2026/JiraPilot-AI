package com.jirapilot.client;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class JiraClientFactory {

    private final ApplicationContext applicationContext;

    @Value("${jirapilot.demo-mode:true}")
    private boolean demoMode;

    @Value("${jirapilot.jira.base-url:}")
    private String baseUrl;

    @Value("${jirapilot.jira.api-token:}")
    private String apiToken;

    public JiraClient getClient() {
        if (baseUrl != null && !baseUrl.isBlank() && apiToken != null && !apiToken.isBlank()) {
            return applicationContext.getBean("atlassianJiraClient", JiraClient.class);
        }
        return applicationContext.getBean("demoJiraClient", JiraClient.class);
    }
}
