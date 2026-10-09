package com.jirapilot.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateIssueRequest {
    private String key;
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
    private List<String> screenshots;
}
