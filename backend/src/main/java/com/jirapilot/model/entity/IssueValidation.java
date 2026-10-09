package com.jirapilot.model.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "issue_validations")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class IssueValidation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "jira_issue_id", nullable = false)
    private JiraIssue jiraIssue;

    private Integer readinessScore;

    @Column(nullable = false, length = 32)
    private String status; // READY, NEEDS_INFORMATION

    @Lob
    @Column(columnDefinition = "TEXT")
    private String reason;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String suggestedJiraComment;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String suggestedEmailBody;

    @ElementCollection
    @CollectionTable(name = "missing_information", joinColumns = @JoinColumn(name = "validation_id"))
    @Column(name = "field_name")
    @Builder.Default
    private List<String> missingInformation = new ArrayList<>();

    @ElementCollection
    @CollectionTable(name = "available_information", joinColumns = @JoinColumn(name = "validation_id"))
    @Column(name = "field_name")
    @Builder.Default
    private List<String> availableInformation = new ArrayList<>();

    @CreationTimestamp
    private LocalDateTime validatedAt;
}
