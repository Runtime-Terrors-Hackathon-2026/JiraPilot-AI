package com.jirapilot.client;

import com.jirapilot.model.dto.CreateIssueRequest;

import java.util.List;
import java.util.Map;

public interface JiraClient {
    CreateIssueRequest getIssue(String issueKey);
    boolean addComment(String issueKey, String commentBody);
    boolean updateIssueStatus(String issueKey, String statusName);
    List<Map<String, Object>> getComments(String issueKey);
    List<String> getProjectIssueKeys(String projectKey);
}
