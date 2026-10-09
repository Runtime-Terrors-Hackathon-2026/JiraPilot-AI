package com.jirapilot.model.entity;

import com.jirapilot.model.enums.InvestigationStatus;
import com.jirapilot.model.enums.IssueStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "jira_issues", indexes = {
        @Index(name = "idx_jira_key", columnList = "jiraKey", unique = true),
        @Index(name = "idx_issue_status", columnList = "status")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class JiraIssue {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 64)
    private String jiraKey;

    @Column(nullable = false, length = 512)
    private String summary;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(length = 128)
    private String reporter;

    @Column(length = 64)
    private String environment;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String apiDetails;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String logs;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String requestPayload;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String responsePayload;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String errorMessage;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String expectedBehavior;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String actualBehavior;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String replicationSteps;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    @Builder.Default
    private IssueStatus status = IssueStatus.OPEN;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    @Builder.Default
    private InvestigationStatus investigationStatus = InvestigationStatus.NOT_STARTED;

    private Integer readinessScore;

    @Column(length = 128)
    private String affectedService;

    @Column(length = 256)
    private String probableRootCause;

    private Integer aiConfidence;

    @OneToOne(mappedBy = "jiraIssue", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private IssueValidation validation;

    @OneToOne(mappedBy = "jiraIssue", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private Investigation investigation;

    @OneToMany(mappedBy = "jiraIssue", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<NotificationLog> notifications = new ArrayList<>();

    @OneToMany(mappedBy = "jiraIssue", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<AuditEvent> auditEvents = new ArrayList<>();

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
