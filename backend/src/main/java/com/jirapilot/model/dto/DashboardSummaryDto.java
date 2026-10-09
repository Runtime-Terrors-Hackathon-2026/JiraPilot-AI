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
public class DashboardSummaryDto {
    private long totalTickets;
    private long readyTickets;
    private long waitingForInfoTickets;
    private long investigationsRunning;
    private long rcaCompleted;
    private double averageReadinessScore;
    private double estimatedHoursSaved;
}
