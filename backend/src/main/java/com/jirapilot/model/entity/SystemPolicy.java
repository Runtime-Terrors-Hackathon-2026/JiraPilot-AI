package com.jirapilot.model.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "system_policies")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SystemPolicy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 64)
    private String policyKey; // "DEFAULT"

    private int weightDescription;
    private int weightApiDetails;
    private int weightLogs;
    private int weightRequestPayload;
    private int weightEnvironment;
    private int weightErrorMessage;
    private int weightExpectedActualBehavior;
    private int weightReplicationSteps;
    private int weightScreenshots;

    private int readinessThreshold; // e.g., 70
    private int confidenceThreshold; // e.g., 75
    private int similarityThreshold; // e.g., 60

    private boolean autoCommentEnabled;
    private boolean autoEmailEnabled;
    private boolean autoInvestigateEnabled;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
