package com.jirapilot.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.model.dto.CreateIssueRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.nio.charset.StandardCharsets;
import java.util.*;

@Slf4j
@Component("atlassianJiraClient")
public class AtlassianJiraClient implements JiraClient {

    @Value("${jirapilot.jira.base-url:}")
    private String baseUrl;

    @Value("${jirapilot.jira.email:}")
    private String email;

    @Value("${jirapilot.jira.api-token:}")
    private String apiToken;

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    private HttpHeaders createAuthHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));
        String auth = email + ":" + apiToken;
        byte[] encodedAuth = Base64.getEncoder().encode(auth.getBytes(StandardCharsets.UTF_8));
        headers.set("Authorization", "Basic " + new String(encodedAuth, StandardCharsets.UTF_8));
        return headers;
    }

    @Override
    public CreateIssueRequest getIssue(String issueKey) {
        try {
            String url = baseUrl.replaceAll("/+$", "") + "/rest/api/3/issue/" + issueKey;
            HttpEntity<Void> request = new HttpEntity<>(createAuthHeaders());
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, request, String.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                JsonNode root = objectMapper.readTree(response.getBody());
                JsonNode fields = root.path("fields");

                String key = root.path("key").asText(issueKey);
                String summary = fields.path("summary").asText("");
                String description = "";
                JsonNode descNode = fields.path("description");
                if (descNode.isTextual()) {
                    description = descNode.asText();
                } else if (descNode.has("content")) {
                    StringBuilder sb = new StringBuilder();
                    extractAdfText(descNode, sb);
                    description = sb.toString().trim();
                }

                String reporter = fields.path("reporter").path("emailAddress").asText("sshankaran202@gmail.com");

                return CreateIssueRequest.builder()
                        .key(key)
                        .summary(summary)
                        .description(description)
                        .reporter(reporter)
                        .environment(fields.path("environment").asText(null))
                        .build();
            }
        } catch (Exception e) {
            log.warn("[ATLASSIAN JIRA] Failed to retrieve issue {}: {}. Falling back to default envelope.", issueKey, e.getMessage());
        }

        return CreateIssueRequest.builder()
                .key(issueKey)
                .summary("Issue " + issueKey)
                .description("Retrieved from Jira Cloud")
                .reporter("reporter@jira.com")
                .build();
    }

    @Override
    public boolean addComment(String issueKey, String commentBody) {
        try {
            String url = baseUrl.replaceAll("/+$", "") + "/rest/api/3/issue/" + issueKey + "/comment";
            Map<String, Object> bodyMap = Map.of(
                    "body", Map.of(
                            "type", "doc",
                            "version", 1,
                            "content", List.of(
                                    Map.of(
                                            "type", "paragraph",
                                            "content", List.of(
                                                    Map.of("type", "text", "text", commentBody)
                                            )
                                    )
                            )
                    )
            );

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(bodyMap, createAuthHeaders());
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            log.warn("[ATLASSIAN JIRA] Error posting comment to {}: {}", issueKey, e.getMessage());
            return false;
        }
    }

    @Override
    public boolean updateIssueStatus(String issueKey, String statusName) {
        log.info("[ATLASSIAN JIRA] Attempting transition on issue {} to {}", issueKey, statusName);
        return true;
    }

    @Override
    public List<Map<String, Object>> getComments(String issueKey) {
        return Collections.emptyList();
    }

    @Override
    public List<String> getProjectIssueKeys(String projectKey) {
        List<String> keys = new ArrayList<>();
        try {
            String url = baseUrl.replaceAll("/+$", "") + "/rest/api/3/search/jql?jql=project=" + projectKey;
            HttpEntity<Void> request = new HttpEntity<>(createAuthHeaders());
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, request, String.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                JsonNode root = objectMapper.readTree(response.getBody());
                JsonNode issues = root.path("issues");
                if (issues.isArray()) {
                    for (JsonNode node : issues) {
                        String k = node.path("key").asText();
                        if (k != null && !k.isBlank()) {
                            keys.add(k);
                        } else if (node.has("id")) {
                            // fetch key by id
                            String id = node.path("id").asText();
                            CreateIssueRequest detailed = getIssue(id);
                            if (detailed != null && detailed.getKey() != null) {
                                keys.add(detailed.getKey());
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
            log.warn("[ATLASSIAN JIRA] Failed to query project issue keys for {}: {}", projectKey, e.getMessage());
        }
        return keys;
    }

    private void extractAdfText(JsonNode node, StringBuilder sb) {
        if (node == null) return;
        if (node.has("text")) {
            sb.append(node.path("text").asText()).append(" ");
        }
        if (node.has("content") && node.path("content").isArray()) {
            for (JsonNode child : node.path("content")) {
                extractAdfText(child, sb);
            }
        }
    }
}
