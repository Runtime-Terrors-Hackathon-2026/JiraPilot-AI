package com.jirapilot.model.dto;

import com.jirapilot.model.enums.InvestigationStatus;
import com.jirapilot.model.enums.IssueStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IssueResponseDto {
    private Long id;
    private String jiraKey;
    private String summary;
    private String description;
    private String reporter;
    private String environment;
    private String apiDetails;
    private String logs;
    private String requestPayload;
    private String responsePayload;
    private String errorMessage;
    private String expectedBehavior;
    private String actualBehavior;
    private String replicationSteps;
    private IssueStatus status;
    private InvestigationStatus investigationStatus;
    private Integer readinessScore;
    private String affectedService;
    private String probableRootCause;
    private Integer aiConfidence;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private ValidationResultDto validation;
    private InvestigationResultDto investigation;
    private List<MockEmailDto> notifications;
    private List<AuditEventDto> auditEvents;
    private List<IssueAttachmentDto> attachments;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class IssueAttachmentDto {
        private Long id;
        private String attachmentId;
        private String filename;
        private String mimeType;
        private Long sizeBytes;
        private String sha256Hash;
        private String status;
        private boolean quarantined;
        private String quarantineReason;
        private String primaryService;
        private String primaryEndpoint;
        private Integer primaryStatus;
        private String correlationId;
        private String probableRootCause;
        private Double confidenceScore;
        private String confidenceCategory;
        private String recommendedRepo;
        private String cloneCommand;
        private String analysisSummary;
        private String analysisJson;
        private boolean jiraCommentPosted;
        private boolean emailSent;
        private LocalDateTime createdAt;
        private LocalDateTime analyzedAt;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AuditEventDto {
        private Long id;
        private String eventType;
        private String workflowStage;
        private String details;
        private String status;
        private Long durationMs;
        private LocalDateTime timestamp;
    }
}
