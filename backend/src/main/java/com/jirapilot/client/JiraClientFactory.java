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

    public JiraClient getClient() {
        if (demoMode) {
            return applicationContext.getBean("demoJiraClient", JiraClient.class);
        } else {
            return applicationContext.getBean("atlassianJiraClient", JiraClient.class);
        }
    }
}
