package com.jirapilot.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.client.JiraClientFactory;
import com.jirapilot.client.PythonAiClient;
import com.jirapilot.model.dto.*;
import com.jirapilot.model.entity.*;
import com.jirapilot.model.enums.*;
import com.jirapilot.repository.InvestigationRepository;
import com.jirapilot.repository.IssueValidationRepository;
import com.jirapilot.repository.JiraIssueRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
@lombok.Getter
public class TriageWorkflowService {

    private final JiraIssueRepository issueRepository;
    private final IssueValidationRepository validationRepository;
    private final InvestigationRepository investigationRepository;
    private final PythonAiClient aiClient;
    private final JiraClientFactory jiraClientFactory;
    private final EmailNotificationService emailService;
    private final PolicyService policyService;
    private final AuditService auditService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Transactional
    public JiraIssue processNewOrUpdatedIssue(CreateIssueRequest request, boolean isUpdate) {
        long startTime = System.currentTimeMillis();
        String jiraKey = request.getKey() != null ? request.getKey() : "HACK-" + (1000 + (int)(Math.random() * 9000));

        JiraIssue issue = issueRepository.findByJiraKey(jiraKey).orElseGet(() ->
                JiraIssue.builder()
                        .jiraKey(jiraKey)
                        .summary(request.getSummary() != null ? request.getSummary() : "Incident")
                        .reporter(request.getReporter() != null ? request.getReporter() : "reporter@example.com")
                        .status(IssueStatus.OPEN)
                        .build()
        );

        // Update fields
        if (request.getSummary() != null) issue.setSummary(request.getSummary());
        if (request.getDescription() != null) issue.setDescription(request.getDescription());
        if (request.getReporter() != null) issue.setReporter(request.getReporter());
        if (request.getEnvironment() != null) issue.setEnvironment(request.getEnvironment());
        if (request.getApiDetails() != null) issue.setApiDetails(request.getApiDetails());
        if (request.getLogs() != null) issue.setLogs(request.getLogs());
        if (request.getRequestPayload() != null) issue.setRequestPayload(request.getRequestPayload());
        if (request.getResponsePayload() != null) issue.setResponsePayload(request.getResponsePayload());
        if (request.getErrorMessage() != null) issue.setErrorMessage(request.getErrorMessage());
        if (request.getExpectedBehavior() != null) issue.setExpectedBehavior(request.getExpectedBehavior());
        if (request.getActualBehavior() != null) issue.setActualBehavior(request.getActualBehavior());
        if (request.getReplicationSteps() != null) issue.setReplicationSteps(request.getReplicationSteps());

        issue = issueRepository.save(issue);

        auditService.recordEvent(
                issue,
                isUpdate ? "ISSUE_UPDATED" : "ISSUE_INGESTED",
                "INGESTION",
                "Issue " + jiraKey + " ingested: " + issue.getSummary(),
                "SUCCESS",
                System.currentTimeMillis() - startTime
        );

        // Step 2: Validate Ticket
        runValidationWorkflow(issue);

        return issue;
    }

    @Transactional
    public ValidationResultDto runValidationWorkflow(JiraIssue issue) {
        long startTime = System.currentTimeMillis();
        PolicyDto policy = policyService.getPolicy();

        ValidationResultDto validationResult = aiClient.validateIssue(issue, policy);

        // Persist validation
        IssueValidation validation = issue.getValidation();
        if (validation == null) {
            validation = IssueValidation.builder().jiraIssue(issue).build();
        }

        validation.setReadinessScore(validationResult.getReadinessScore());
        validation.setStatus(validationResult.getStatus());
        validation.setReason(validationResult.getReason());
        validation.setSuggestedJiraComment(validationResult.getSuggestedJiraComment());
        validation.setSuggestedEmailBody(validationResult.getSuggestedEmailBody());
        validation.setMissingInformation(new ArrayList<>(validationResult.getMissingInformation()));
        validation.setAvailableInformation(new ArrayList<>(validationResult.getAvailableInformation()));

        validationRepository.save(validation);
        issue.setValidation(validation);
        issue.setReadinessScore(validationResult.getReadinessScore());

        boolean isReady = "READY".equalsIgnoreCase(validationResult.getStatus());

        if (!isReady) {
            issue.setStatus(IssueStatus.WAITING_FOR_INFORMATION);
            issue.setInvestigationStatus(InvestigationStatus.NOT_STARTED);
            issueRepository.save(issue);

            auditService.recordEvent(
                    issue,
                    "VALIDATION_COMPLETED",
                    "VALIDATION",
                    "Ticket readiness score: " + validationResult.getReadinessScore() + "/100. Missing: " + String.join(", ", validationResult.getMissingInformation()),
                    "WARNING",
                    System.currentTimeMillis() - startTime
            );

            // Post missing info comment to Jira if enabled
            if (policy.isAutoCommentEnabled()) {
                postJiraComment(issue.getJiraKey(), validationResult.getSuggestedJiraComment());
            }

            // Send notification email to reporter if enabled
            if (policy.isAutoEmailEnabled()) {
                emailService.sendMissingInformationEmail(issue, validationResult.getSuggestedEmailBody());
            }

        } else {
            issue.setStatus(IssueStatus.READY);
            issueRepository.save(issue);

            auditService.recordEvent(
                    issue,
                    "VALIDATION_COMPLETED",
                    "VALIDATION",
                    "Ticket verified READY for investigation (Readiness: " + validationResult.getReadinessScore() + "/100).",
                    "SUCCESS",
                    System.currentTimeMillis() - startTime
            );

            // If auto-investigate is enabled, launch investigation
            if (policy.isAutoInvestigateEnabled()) {
                runInvestigationWorkflow(issue);
            }
        }

        return validationResult;
    }

    @Transactional
    public InvestigationResultDto runInvestigationWorkflow(JiraIssue issue) {
        long startTime = System.currentTimeMillis();
        issue.setStatus(IssueStatus.INVESTIGATING);
        issue.setInvestigationStatus(InvestigationStatus.RUNNING);
        issueRepository.save(issue);

        auditService.recordEvent(
                issue,
                "INVESTIGATION_STARTED",
                "INVESTIGATION",
                "Automated RCA, dependency mapping, and test case generation started.",
                "SUCCESS",
                System.currentTimeMillis() - startTime
        );

        InvestigationResultDto result = aiClient.investigateIssue(issue);

        Investigation investigation = issue.getInvestigation();
        if (investigation == null) {
            investigation = Investigation.builder().jiraIssue(issue).build();
        }

        InvestigationResultDto.RcaDto rca = result.getRca();
        if (rca != null) {
            investigation.setExecutiveSummary(rca.getExecutiveSummary());
            investigation.setAffectedService(rca.getAffectedService());
            investigation.setDownstreamDependency(rca.getDownstreamDependency());
            investigation.setErrorPattern(rca.getErrorPattern());
            investigation.setFailurePoint(rca.getFailurePoint());
            investigation.setProbableRootCause(rca.getProbableRootCause());
            investigation.setRootCauseConfidence(rca.getRootCauseConfidence());
            investigation.setConfidenceLevel(rca.getConfidenceLevel() != null ? ConfidenceLevel.valueOf(rca.getConfidenceLevel()) : ConfidenceLevel.HIGH);
            investigation.setRecommendedFix(rca.getRecommendedFix());
            investigation.setJiraInvestigationComment(rca.getJiraInvestigationComment());

            try {
                investigation.setAffectedApiJson(objectMapper.writeValueAsString(rca.getAffectedApi()));
                investigation.setSupportingEvidenceJson(objectMapper.writeValueAsString(rca.getSupportingEvidence()));
                investigation.setRecommendedInvestigationStepsJson(objectMapper.writeValueAsString(rca.getRecommendedInvestigationSteps()));
                investigation.setServiceGraphNodesJson(objectMapper.writeValueAsString(rca.getServiceGraphNodes()));
                investigation.setServiceGraphEdgesJson(objectMapper.writeValueAsString(rca.getServiceGraphEdges()));
                investigation.setIncidentTimelineJson(objectMapper.writeValueAsString(rca.getIncidentTimeline()));
            } catch (Exception e) {
                log.warn("Failed to serialize RCA sub-fields: {}", e.getMessage());
            }

            // Sync issue summary columns
            issue.setAffectedService(rca.getAffectedService());
            issue.setProbableRootCause(rca.getProbableRootCause());
            issue.setAiConfidence(rca.getRootCauseConfidence());
        }

        investigation.setReproductionCurl(result.getReproductionCurl());
        investigation.setPostmanJson(result.getPostmanJson());

        try {
            investigation.setGeneratedTestCasesJson(objectMapper.writeValueAsString(result.getGeneratedTestCases()));
            investigation.setSimilarIncidentsJson(objectMapper.writeValueAsString(result.getSimilarIncidents()));
        } catch (Exception e) {
            log.warn("Failed to serialize test cases / similar incidents: {}", e.getMessage());
        }

        investigationRepository.save(investigation);
        issue.setInvestigation(investigation);
        issue.setStatus(IssueStatus.INVESTIGATED);
        issue.setInvestigationStatus(InvestigationStatus.COMPLETED);
        issueRepository.save(issue);

        auditService.recordEvent(
                issue,
                "INVESTIGATION_COMPLETED",
                "ROOT_CAUSE",
                "Root cause isolated: " + issue.getProbableRootCause() + " (Confidence: " + issue.getAiConfidence() + "%)",
                "SUCCESS",
                System.currentTimeMillis() - startTime
        );

        // Post investigation report to Jira if enabled
        PolicyDto policy = policyService.getPolicy();
        if (policy.isAutoCommentEnabled() && rca != null && rca.getJiraInvestigationComment() != null) {
            postJiraComment(issue.getJiraKey(), rca.getJiraInvestigationComment());
        }

        // Send email summary
        if (policy.isAutoEmailEnabled() && rca != null) {
            emailService.sendInvestigationCompletedEmail(issue, rca.getExecutiveSummary() + "\n\nRoot Cause: " + rca.getProbableRootCause());
        }

        return result;
    }

    public boolean postJiraComment(String jiraKey, String comment) {
        log.info("[JIRA COMMENT] Posting comment to {}: {}", jiraKey, comment);
        boolean success = jiraClientFactory.getClient().addComment(jiraKey, comment);
        if (success) {
            issueRepository.findByJiraKey(jiraKey).ifPresent(issue ->
                    auditService.recordEvent(issue, "JIRA_COMMENT_POSTED", "NOTIFICATION", "Automated triage comment posted to Jira issue", "SUCCESS", 50L)
            );
        }
        return success;
    }
}
