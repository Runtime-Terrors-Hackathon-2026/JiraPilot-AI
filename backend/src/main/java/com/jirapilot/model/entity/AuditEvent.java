package com.jirapilot.model.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "audit_events", indexes = {
        @Index(name = "idx_audit_jira_key", columnList = "jiraKey"),
        @Index(name = "idx_audit_timestamp", columnList = "timestamp")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuditEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "jira_issue_id")
    private JiraIssue jiraIssue;

    @Column(nullable = false, length = 64)
    private String jiraKey;

    @Column(nullable = false, length = 64)
    private String eventType; // ISSUE_INGESTED, VALIDATED, INVESTIGATED, COMMENT_POSTED, NOTIFIED, POLICY_UPDATED

    @Column(length = 64)
    private String workflowStage;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String details;

    @Column(length = 32)
    private String status; // SUCCESS, WARNING, FAILURE

    private Long durationMs;

    @CreationTimestamp
    private LocalDateTime timestamp;
}
