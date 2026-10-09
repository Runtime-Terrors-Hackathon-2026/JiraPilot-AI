package com.jirapilot.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.model.entity.IssueAttachment;
import com.jirapilot.model.entity.JiraIssue;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class JiraCommentTemplateService {

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Builds the standardized Jira investigation report comment from an analyzed attachment.
     */
    public String buildInvestigationComment(JiraIssue issue, IssueAttachment attachment) {
        if (attachment.isQuarantined()) {
            return buildQuarantineComment(issue, attachment);
        }

        String issueKey = issue.getJiraKey();
        String analysisStatus = attachment.getStatus().name();
        String shortSummary = attachment.getAnalysisSummary() != null ? attachment.getAnalysisSummary() : "Automated log investigation completed.";
        String httpMethod = "";
        String endpoint = attachment.getPrimaryEndpoint() != null ? attachment.getPrimaryEndpoint() : "Not detected";
        if (endpoint.contains(" ")) {
            String[] parts = endpoint.split(" ", 2);
            httpMethod = parts[0];
            endpoint = parts[1];
        } else {
            httpMethod = "HTTP";
        }

        String serviceName = attachment.getPrimaryService() != null ? attachment.getPrimaryService() : "Unknown service";
        String observedError = attachment.getPrimaryStatus() != null ? "HTTP " + attachment.getPrimaryStatus() : "Application Exception";
        String correlationId = attachment.getCorrelationId() != null ? attachment.getCorrelationId() : "Not found in telemetry";
        String rootCause = attachment.getProbableRootCause() != null ? attachment.getProbableRootCause() : "Inconclusive - insufficient diagnostic telemetry.";
        String confidenceLabel = attachment.getConfidenceCategory() != null ? attachment.getConfidenceCategory() : "MEDIUM";
        String repoName = attachment.getRecommendedRepo() != null ? attachment.getRecommendedRepo() : "No verified repository match found.";
        String cloneCmd = attachment.getCloneCommand() != null ? attachment.getCloneCommand() : "git clone https://github.com/northstar-labs/" + serviceName + ".git";

        // Parse evidence and steps from analysisJson if available
        List<String> evidenceLines = new ArrayList<>();
        List<String> debugSteps = new ArrayList<>();
        List<String> testCases = new ArrayList<>();
        String matchReason = "Direct service identifier and endpoint route match.";
        String limitations = "Findings generated deterministically from provided synthetic log excerpt.";

        if (attachment.getAnalysisJson() != null) {
            try {
                JsonNode root = objectMapper.readTree(attachment.getAnalysisJson());
                JsonNode evArr = root.path("evidence");
                if (evArr.isArray()) {
                    for (JsonNode ev : evArr) {
                        int line = ev.path("line").asInt(1);
                        String detail = ev.path("detail").asText("");
                        evidenceLines.add(String.format("* [Line %d] %s", line, detail));
                    }
                }
                JsonNode dbArr = root.path("recommendedDebuggingSteps");
                if (dbArr.isArray()) {
                    int stepNum = 1;
                    for (JsonNode st : dbArr) {
                        debugSteps.add(String.format("%d. %s", stepNum++, st.asText("")));
                    }
                }
                JsonNode tcArr = root.path("suggestedTestCases");
                if (tcArr.isArray()) {
                    for (JsonNode tc : tcArr) {
                        testCases.add(String.format("* `%s`", tc.asText("")));
                    }
                }
                JsonNode repos = root.path("repositoryMatches");
                if (repos.isArray() && repos.size() > 0) {
                    matchReason = repos.get(0).path("matchReason").asText(matchReason);
                }
                limitations = root.path("limitations").asText(limitations);
            } catch (Exception e) {
                log.warn("[TEMPLATE] Failed to parse analysis JSON for comment: {}", e.getMessage());
            }
        }

        if (evidenceLines.isEmpty()) {
            evidenceLines.add("* Telemetry log excerpt parsed without explicit stack trace lines.");
        }
        if (debugSteps.isEmpty()) {
            debugSteps.add("1. Inspect service logs corresponding to correlation ID.");
            debugSteps.add("2. Verify downstream API availability and network route.");
        }
        if (testCases.isEmpty()) {
            testCases.add("* `test_service_error_handling()`");
        }

        StringBuilder sb = new StringBuilder();
        sb.append("h3. \uD83E\uDD16 JiraPilot AI — Log Investigation Report\n\n");
        sb.append("*Ticket:* ").append(issueKey).append("\n");
        sb.append("*Analysis status:* ").append(analysisStatus).append("\n\n");
        sb.append("*Summary:*\n").append(shortSummary).append("\n\n");

        sb.append("h4. 1. API and service findings\n");
        sb.append("* Detected API: `").append(httpMethod).append(" ").append(endpoint).append("`\n");
        sb.append("* Suspected service: `").append(serviceName).append("`\n");
        sb.append("* Observed status/error: `").append(observedError).append("`\n");
        sb.append("* Correlation ID: `").append(correlationId).append("`\n\n");

        sb.append("h4. 2. Evidence\n");
        for (String ev : evidenceLines) {
            sb.append(ev).append("\n");
        }
        sb.append("\n");

        sb.append("h4. 3. Probable cause\n");
        sb.append(rootCause).append("\n\n");
        sb.append("*Confidence:* *").append(confidenceLabel).append("*\n\n");
        sb.append("*Limitations:*\n").append(limitations).append("\n\n");

        sb.append("h4. 4. Recommended repository\n");
        sb.append("* Repository: `").append(repoName).append("`\n");
        sb.append("* Reason: ").append(matchReason).append("\n");
        sb.append("* Related component: `").append(serviceName).append("`\n\n");
        sb.append("*Clone command*\n");
        sb.append("{code:bash}\n").append(cloneCmd).append("\n{code}\n\n");

        sb.append("h4. 5. Recommended debugging steps\n");
        for (String st : debugSteps) {
            sb.append(st).append("\n");
        }
        sb.append("\n");

        sb.append("h4. 6. Suggested validation tests\n");
        for (String tc : testCases) {
            sb.append(tc).append("\n");
        }
        sb.append("\n");

        sb.append("h4. 7. Next action\n");
        sb.append("Clone the suggested repository, review the referenced line numbers, and reproduce using synthetic payload.\n\n");

        sb.append("----\n");
        sb.append("_Generated by JiraPilot AI using synthetic hackathon data. AI findings are suggestions and require developer verification._\n");

        return sb.toString();
    }

    /**
     * Builds quarantine warning comment for sensitive log contents.
     */
    public String buildQuarantineComment(JiraIssue issue, IssueAttachment attachment) {
        return "h3. ⚠️ JiraPilot AI — Security Quarantine Alert\n\n" +
                "*Ticket:* " + issue.getJiraKey() + "\n" +
                "*File:* `" + attachment.getFilename() + "`\n\n" +
                "*Status:* `NEEDS_REVIEW` (Automated processing paused)\n\n" +
                "The uploaded log attachment triggered security quarantine safeguards. " +
                "Potential unredacted private credentials or certificates were detected.\n\n" +
                "*Quarantine Reason:* " + (attachment.getQuarantineReason() != null ? attachment.getQuarantineReason() : "Potential private key block detected.") + "\n\n" +
                "*Next Step:* A security officer must inspect and sanitize the log file before automated triage can proceed.\n\n" +
                "----\n_JiraPilot AI Security Compliance Policy_";
    }

    /**
     * Builds initial notification when log analysis starts.
     */
    public String buildAnalysisStartedComment(JiraIssue issue, String filename) {
        return "h3. ⚙️ JiraPilot AI — Log Ingestion Started\n\n" +
                "Detected new log attachment `" + filename + "` for issue *" + issue.getJiraKey() + "*.\n" +
                "Commencing automated parsing, secret sanitization, evidence extraction, and repository discovery...";
    }
}
