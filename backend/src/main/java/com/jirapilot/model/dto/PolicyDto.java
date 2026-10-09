package com.jirapilot.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PolicyDto {
    private int weightDescription;
    private int weightApiDetails;
    private int weightLogs;
    private int weightRequestPayload;
    private int weightEnvironment;
    private int weightErrorMessage;
    private int weightExpectedActualBehavior;
    private int weightReplicationSteps;
    private int weightScreenshots;

    private int readinessThreshold;
    private int confidenceThreshold;
    private int similarityThreshold;

    private boolean autoCommentEnabled;
    private boolean autoEmailEnabled;
    private boolean autoInvestigateEnabled;
}
