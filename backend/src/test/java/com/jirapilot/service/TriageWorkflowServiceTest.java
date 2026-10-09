package com.jirapilot.service;

import com.jirapilot.client.JiraClient;
import com.jirapilot.client.JiraClientFactory;
import com.jirapilot.client.PythonAiClient;
import com.jirapilot.model.dto.*;
import com.jirapilot.model.entity.JiraIssue;
import com.jirapilot.model.enums.IssueStatus;
import com.jirapilot.repository.InvestigationRepository;
import com.jirapilot.repository.IssueValidationRepository;
import com.jirapilot.repository.JiraIssueRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class TriageWorkflowServiceTest {

    @Mock
    private JiraIssueRepository issueRepository;

    @Mock
    private IssueValidationRepository validationRepository;

    @Mock
    private InvestigationRepository investigationRepository;

    @Mock
    private PythonAiClient aiClient;

    @Mock
    private JiraClientFactory jiraClientFactory;

    @Mock
    private JiraClient jiraClient;

    @Mock
    private EmailNotificationService emailService;

    @Mock
    private PolicyService policyService;

    @Mock
    private AuditService auditService;

    @InjectMocks
    private TriageWorkflowService workflowService;

    private PolicyDto policy;

    @BeforeEach
    void setUp() {
        policy = PolicyDto.builder()
                .autoCommentEnabled(true)
                .autoEmailEnabled(true)
                .autoInvestigateEnabled(true)
                .readinessThreshold(70)
                .build();
    }

    @Test
    void givenIncompleteIssue_whenProcessed_thenSetWaitingForInformation() {
        CreateIssueRequest req = CreateIssueRequest.builder()
                .key("HACK-1002")
                .summary("Incomplete ticket")
                .description("API failing")
                .build();

        when(issueRepository.findByJiraKey("HACK-1002")).thenReturn(Optional.empty());
        when(issueRepository.save(any())).thenAnswer(i -> i.getArgument(0));
        when(policyService.getPolicy()).thenReturn(policy);
        when(jiraClientFactory.getClient()).thenReturn(jiraClient);

        ValidationResultDto valDto = ValidationResultDto.builder()
                .readinessScore(30)
                .status("NEEDS_INFORMATION")
                .missingInformation(List.of("logs", "apiDetails"))
                .availableInformation(List.of("description"))
                .suggestedJiraComment("Additional info needed")
                .suggestedEmailBody("Please update ticket")
                .build();

        when(aiClient.validateIssue(any(), any())).thenReturn(valDto);

        JiraIssue result = workflowService.processNewOrUpdatedIssue(req, false);

        assertThat(result.getStatus()).isEqualTo(IssueStatus.WAITING_FOR_INFORMATION);
        verify(emailService).sendMissingInformationEmail(any(), any());
    }

    @Test
    void givenReadyIssue_whenProcessed_thenTriggerInvestigation() {
        CreateIssueRequest req = CreateIssueRequest.builder()
                .key("HACK-1001")
                .summary("Complete ticket")
                .description("Description with details")
                .logs("ERROR logs here")
                .apiDetails("POST /api/circuit/provision")
                .build();

        when(issueRepository.findByJiraKey("HACK-1001")).thenReturn(Optional.empty());
        when(issueRepository.save(any())).thenAnswer(i -> i.getArgument(0));
        when(policyService.getPolicy()).thenReturn(policy);
        when(jiraClientFactory.getClient()).thenReturn(jiraClient);

        ValidationResultDto valDto = ValidationResultDto.builder()
                .readinessScore(100)
                .status("READY")
                .missingInformation(List.of())
                .availableInformation(List.of("description", "logs", "apiDetails"))
                .build();

        when(aiClient.validateIssue(any(), any())).thenReturn(valDto);

        InvestigationResultDto.RcaDto rca = InvestigationResultDto.RcaDto.builder()
                .executiveSummary("Duplicate NFID root cause")
                .affectedService("WFM")
                .probableRootCause("Duplicate NFID")
                .rootCauseConfidence(94)
                .confidenceLevel("HIGH")
                .jiraInvestigationComment("Investigation comment")
                .build();

        InvestigationResultDto invDto = InvestigationResultDto.builder()
                .rca(rca)
                .reproductionCurl("curl -X POST ...")
                .build();

        when(aiClient.investigateIssue(any())).thenReturn(invDto);

        JiraIssue result = workflowService.processNewOrUpdatedIssue(req, false);

        assertThat(result.getStatus()).isEqualTo(IssueStatus.INVESTIGATED);
        assertThat(result.getProbableRootCause()).isEqualTo("Duplicate NFID");
        assertThat(result.getAiConfidence()).isEqualTo(94);
    }
}
