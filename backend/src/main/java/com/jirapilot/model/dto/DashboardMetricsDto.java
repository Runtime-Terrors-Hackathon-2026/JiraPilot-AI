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
public class DashboardMetricsDto {
    private Map<String, Long> ticketsByStatus;
    private Map<String, Long> missingInfoFrequency;
    private Map<String, Long> incidentsByService;
    private Map<String, Long> rootCauseCategories;
    private List<Map<String, Object>> investigationTrend;
    private Map<String, Object> timeSavingsComparison;
}
