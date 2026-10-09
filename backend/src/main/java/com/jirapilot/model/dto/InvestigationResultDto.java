package com.jirapilot.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InvestigationResultDto {
    private RcaDto rca;
    private String reproductionCurl;
    private String postmanJson;
    private List<Map<String, Object>> generatedTestCases;
    private List<Map<String, Object>> similarIncidents;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RcaDto {
        private String executiveSummary;
        private List<Map<String, Object>> incidentTimeline;
        private Map<String, Object> affectedApi;
        private String affectedService;
        private String downstreamDependency;
        private String errorPattern;
        private String failurePoint;
        private String probableRootCause;
        private Integer rootCauseConfidence;
        private String confidenceLevel;
        private List<String> supportingEvidence;
        private List<String> recommendedInvestigationSteps;
        private String recommendedFix;
        private List<Map<String, Object>> serviceGraphNodes;
        private List<Map<String, Object>> serviceGraphEdges;
        private String jiraInvestigationComment;
    }
}
