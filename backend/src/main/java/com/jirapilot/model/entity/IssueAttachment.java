package com.jirapilot.model.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.jirapilot.model.enums.AttachmentStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "issue_attachments", indexes = {
        @Index(name = "idx_att_sha256", columnList = "sha256Hash"),
        @Index(name = "idx_att_status", columnList = "status"),
        @Index(name = "idx_att_issue", columnList = "jira_issue_id")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class IssueAttachment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "jira_issue_id", nullable = false)
    @JsonIgnore
    private JiraIssue jiraIssue;

    @Column(length = 128)
    private String attachmentId;

    @Column(nullable = false, length = 255)
    private String filename;

    @Column(length = 128)
    private String mimeType;

    private Long sizeBytes;

    @Column(length = 64)
    private String sha256Hash;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    @Builder.Default
    private AttachmentStatus status = AttachmentStatus.RECEIVED;

    @Builder.Default
    private boolean quarantined = false;

    @Column(length = 512)
    private String quarantineReason;

    @Column(length = 128)
    private String primaryService;

    @Column(length = 255)
    private String primaryEndpoint;

    private Integer primaryStatus;

    @Column(length = 128)
    private String correlationId;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String probableRootCause;

    private Double confidenceScore;

    @Column(length = 32)
    private String confidenceCategory;

    @Column(length = 128)
    private String recommendedRepo;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String cloneCommand;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String analysisSummary;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String analysisJson;

    @Builder.Default
    private boolean jiraCommentPosted = false;

    @Builder.Default
    private boolean emailSent = false;

    @CreationTimestamp
    private LocalDateTime createdAt;

    private LocalDateTime analyzedAt;
}
