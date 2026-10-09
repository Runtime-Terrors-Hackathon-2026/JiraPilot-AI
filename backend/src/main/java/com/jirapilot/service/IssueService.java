package com.jirapilot.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jirapilot.model.dto.*;
import com.jirapilot.model.entity.*;
import com.jirapilot.repository.JiraIssueRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class IssueService {

    private final JiraIssueRepository issueRepository;
    private final TriageWorkflowService workflowService;
    private final EmailNotificationService emailService;
    private final AuditService auditService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Transactional(readOnly = true)
    public List<IssueResponseDto> getAllIssues() {
        return issueRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Optional<IssueResponseDto> getIssueByKey(String key) {
        return issueRepository.findByJiraKey(key).map(this::mapToDto);
    }

    @Transactional
    public IssueResponseDto createOrUpdateIssue(CreateIssueRequest request) {
        boolean exists = request.getKey() != null && issueRepository.findByJiraKey(request.getKey()).isPresent();
        JiraIssue issue = workflowService.processNewOrUpdatedIssue(request, exists);
        return mapToDto(issue);
    }

    @Transactional
    public ValidationResultDto revalidateIssue(String key) {
        JiraIssue issue = issueRepository.findByJiraKey(key)
                .orElseThrow(() -> new IllegalArgumentException("Issue not found: " + key));
        return workflowService.runValidationWorkflow(issue);
    }

    @Transactional
    public InvestigationResultDto investigateIssue(String key) {
        JiraIssue issue = issueRepository.findByJiraKey(key)
                .orElseThrow(() -> new IllegalArgumentException("Issue not found: " + key));
        return workflowService.runInvestigationWorkflow(issue);
    }

    @Transactional
    public List<IssueResponseDto> syncJiraProject(String projectKey) {
        log.info("[JIRA SYNC] Initiating synchronization for Jira project {}", projectKey);
        List<String> keys = workflowService.getJiraClientFactory().getClient().getProjectIssueKeys(projectKey);
        List<IssueResponseDto> results = new ArrayList<>();
        for (String key : keys) {
            try {
                CreateIssueRequest req = workflowService.getJiraClientFactory().getClient().getIssue(key);
                if (req != null && req.getKey() != null) {
                    results.add(createOrUpdateIssue(req));
                }
            } catch (Exception e) {
                log.warn("[JIRA SYNC] Failed to sync issue {}: {}", key, e.getMessage());
            }
        }
        return results;
    }

    @Transactional
    public boolean addComment(String key, String comment) {
        return workflowService.postJiraComment(key, comment);
    }

    public IssueResponseDto mapToDto(JiraIssue entity) {
        if (entity == null) return null;

        ValidationResultDto validationDto = null;
        if (entity.getValidation() != null) {
            IssueValidation v = entity.getValidation();
            validationDto = ValidationResultDto.builder()
                    .readinessScore(v.getReadinessScore() != null ? v.getReadinessScore() : 0)
                    .status(v.getStatus())
                    .reason(v.getReason())
                    .suggestedJiraComment(v.getSuggestedJiraComment())
                    .suggestedEmailBody(v.getSuggestedEmailBody())
                    .missingInformation(new ArrayList<>(v.getMissingInformation()))
                    .availableInformation(new ArrayList<>(v.getAvailableInformation()))
                    .build();
        }

        InvestigationResultDto investigationDto = null;
        if (entity.getInvestigation() != null) {
            Investigation inv = entity.getInvestigation();
            InvestigationResultDto.RcaDto rcaDto = InvestigationResultDto.RcaDto.builder()
                    .executiveSummary(inv.getExecutiveSummary())
                    .affectedService(inv.getAffectedService())
                    .downstreamDependency(inv.getDownstreamDependency())
                    .errorPattern(inv.getErrorPattern())
                    .failurePoint(inv.getFailurePoint())
                    .probableRootCause(inv.getProbableRootCause())
                    .rootCauseConfidence(inv.getRootCauseConfidence())
                    .confidenceLevel(inv.getConfidenceLevel() != null ? inv.getConfidenceLevel().name() : "HIGH")
                    .recommendedFix(inv.getRecommendedFix())
                    .jiraInvestigationComment(inv.getJiraInvestigationComment())
                    .affectedApi(safeDeserializeMap(inv.getAffectedApiJson()))
                    .supportingEvidence(safeDeserializeListString(inv.getSupportingEvidenceJson()))
                    .recommendedInvestigationSteps(safeDeserializeListString(inv.getRecommendedInvestigationStepsJson()))
                    .serviceGraphNodes(safeDeserializeListMap(inv.getServiceGraphNodesJson()))
                    .serviceGraphEdges(safeDeserializeListMap(inv.getServiceGraphEdgesJson()))
                    .incidentTimeline(safeDeserializeListMap(inv.getIncidentTimelineJson()))
                    .build();

            investigationDto = InvestigationResultDto.builder()
                    .rca(rcaDto)
                    .reproductionCurl(inv.getReproductionCurl())
                    .postmanJson(inv.getPostmanJson())
                    .generatedTestCases(safeDeserializeListMap(inv.getGeneratedTestCasesJson()))
                    .similarIncidents(safeDeserializeListMap(inv.getSimilarIncidentsJson()))
                    .build();
        }

        List<MockEmailDto> notifications = emailService.getEmailsForIssue(entity.getJiraKey());

        List<IssueResponseDto.AuditEventDto> auditList = auditService.getEventsForIssue(entity.getJiraKey()).stream()
                .map(a -> IssueResponseDto.AuditEventDto.builder()
                        .id(a.getId())
                        .eventType(a.getEventType())
                        .workflowStage(a.getWorkflowStage())
                        .details(a.getDetails())
                        .status(a.getStatus())
                        .durationMs(a.getDurationMs())
                        .timestamp(a.getTimestamp())
                        .build())
                .collect(Collectors.toList());

        List<IssueResponseDto.IssueAttachmentDto> attachmentDtos = entity.getAttachments() != null
                ? entity.getAttachments().stream().map(att -> IssueResponseDto.IssueAttachmentDto.builder()
                .id(att.getId())
                .attachmentId(att.getAttachmentId())
                .filename(att.getFilename())
                .mimeType(att.getMimeType())
                .sizeBytes(att.getSizeBytes())
                .sha256Hash(att.getSha256Hash())
                .status(att.getStatus() != null ? att.getStatus().name() : "RECEIVED")
                .quarantined(att.isQuarantined())
                .quarantineReason(att.getQuarantineReason())
                .primaryService(att.getPrimaryService())
                .primaryEndpoint(att.getPrimaryEndpoint())
                .primaryStatus(att.getPrimaryStatus())
                .correlationId(att.getCorrelationId())
                .probableRootCause(att.getProbableRootCause())
                .confidenceScore(att.getConfidenceScore())
                .confidenceCategory(att.getConfidenceCategory())
                .recommendedRepo(att.getRecommendedRepo())
                .cloneCommand(att.getCloneCommand())
                .analysisSummary(att.getAnalysisSummary())
                .analysisJson(att.getAnalysisJson())
                .jiraCommentPosted(att.isJiraCommentPosted())
                .emailSent(att.isEmailSent())
                .createdAt(att.getCreatedAt())
                .analyzedAt(att.getAnalyzedAt())
                .build()).collect(Collectors.toList())
                : Collections.emptyList();

        return IssueResponseDto.builder()
                .id(entity.getId())
                .jiraKey(entity.getJiraKey())
                .summary(entity.getSummary())
                .description(entity.getDescription())
                .reporter(entity.getReporter())
                .environment(entity.getEnvironment())
                .apiDetails(entity.getApiDetails())
                .logs(entity.getLogs())
                .requestPayload(entity.getRequestPayload())
                .responsePayload(entity.getResponsePayload())
                .errorMessage(entity.getErrorMessage())
                .expectedBehavior(entity.getExpectedBehavior())
                .actualBehavior(entity.getActualBehavior())
                .replicationSteps(entity.getReplicationSteps())
                .status(entity.getStatus())
                .investigationStatus(entity.getInvestigationStatus())
                .readinessScore(entity.getReadinessScore())
                .affectedService(entity.getAffectedService())
                .probableRootCause(entity.getProbableRootCause())
                .aiConfidence(entity.getAiConfidence())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .validation(validationDto)
                .investigation(investigationDto)
                .notifications(notifications)
                .auditEvents(auditList)
                .attachments(attachmentDtos)
                .build();
    }

    private Map<String, Object> safeDeserializeMap(String json) {
        if (json == null || json.isBlank()) return Collections.emptyMap();
        try {
            return objectMapper.readValue(json, new TypeReference<Map<String, Object>>() {});
        } catch (Exception e) {
            return Collections.emptyMap();
        }
    }

    private List<String> safeDeserializeListString(String json) {
        if (json == null || json.isBlank()) return Collections.emptyList();
        try {
            return objectMapper.readValue(json, new TypeReference<List<String>>() {});
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    private List<Map<String, Object>> safeDeserializeListMap(String json) {
        if (json == null || json.isBlank()) return Collections.emptyList();
        try {
            return objectMapper.readValue(json, new TypeReference<List<Map<String, Object>>>() {});
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }
}
