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
    default byte[] getAttachmentBytes(String contentUrl) { return new byte[0]; }
    default List<Map<String, String>> getIssueAttachments(String issueKey) { return java.util.Collections.emptyList(); }
}
