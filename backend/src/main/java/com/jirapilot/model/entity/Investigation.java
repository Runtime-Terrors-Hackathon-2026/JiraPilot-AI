package com.jirapilot.model.entity;

import com.jirapilot.model.enums.ConfidenceLevel;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "investigations")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Investigation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "jira_issue_id", nullable = false)
    private JiraIssue jiraIssue;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String executiveSummary;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String affectedApiJson;

    @Column(length = 128)
    private String affectedService;

    @Column(length = 128)
    private String downstreamDependency;

    @Column(length = 256)
    private String errorPattern;

    @Column(length = 256)
    private String failurePoint;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String probableRootCause;

    private Integer rootCauseConfidence;

    @Enumerated(EnumType.STRING)
    @Column(length = 32)
    private ConfidenceLevel confidenceLevel;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String supportingEvidenceJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String recommendedInvestigationStepsJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String recommendedFix;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String serviceGraphNodesJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String serviceGraphEdgesJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String incidentTimelineJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String reproductionCurl;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String postmanJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String generatedTestCasesJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String similarIncidentsJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String jiraInvestigationComment;

    @CreationTimestamp
    private LocalDateTime investigatedAt;
}
