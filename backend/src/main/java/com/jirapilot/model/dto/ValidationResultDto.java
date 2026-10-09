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
public class ValidationResultDto {
    private int readinessScore;
    private String status;
    private List<String> missingInformation;
    private List<String> availableInformation;
    private String reason;
    private String suggestedJiraComment;
    private String suggestedEmailBody;
}
