package com.jirapilot.service;

import com.jirapilot.model.dto.DashboardMetricsDto;
import com.jirapilot.model.dto.DashboardSummaryDto;
import com.jirapilot.model.enums.InvestigationStatus;
import com.jirapilot.model.enums.IssueStatus;
import com.jirapilot.repository.IssueValidationRepository;
import com.jirapilot.repository.JiraIssueRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class MetricsService {

    private final JiraIssueRepository issueRepository;
    private final IssueValidationRepository validationRepository;

    public DashboardSummaryDto getSummary() {
        long total = issueRepository.count();
        long ready = issueRepository.countByStatus(IssueStatus.READY);
        long waiting = issueRepository.countByStatus(IssueStatus.WAITING_FOR_INFORMATION);
        long running = issueRepository.countByInvestigationStatus(InvestigationStatus.RUNNING);
        long rcaDone = issueRepository.countByInvestigationStatus(InvestigationStatus.COMPLETED);
        Double avgReadiness = issueRepository.calculateAverageReadinessScore();

        // Estimated savings: ~2.5 hours saved per automated investigation + 0.5 hours per triage validation
        double hoursSaved = (rcaDone * 2.5) + (total * 0.5);

        return DashboardSummaryDto.builder()
                .totalTickets(total)
                .readyTickets(ready)
                .waitingForInfoTickets(waiting)
                .investigationsRunning(running)
                .rcaCompleted(rcaDone)
                .averageReadinessScore(avgReadiness != null ? Math.round(avgReadiness * 10.0) / 10.0 : 0.0)
                .estimatedHoursSaved(Math.round(hoursSaved * 10.0) / 10.0)
                .build();
    }

    public DashboardMetricsDto getMetrics() {
        Map<String, Long> statusMap = new HashMap<>();
        for (IssueStatus status : IssueStatus.values()) {
            long count = issueRepository.countByStatus(status);
            if (count > 0) statusMap.put(status.name(), count);
        }

        Map<String, Long> missingMap = new HashMap<>();
        List<Object[]> missingCounts = validationRepository.countMissingInformationFrequency();
        for (Object[] row : missingCounts) {
            if (row[0] != null) {
                missingMap.put(row[0].toString(), (Long) row[1]);
            }
        }

        Map<String, Long> serviceMap = new HashMap<>();
        List<Object[]> serviceCounts = issueRepository.countByAffectedService();
        for (Object[] row : serviceCounts) {
            if (row[0] != null) {
                serviceMap.put(row[0].toString(), (Long) row[1]);
            }
        }

        Map<String, Long> rootCauseMap = new HashMap<>();
        List<Object[]> rcCounts = issueRepository.countByRootCause();
        for (Object[] row : rcCounts) {
            if (row[0] != null) {
                String rcName = row[0].toString();
                if (rcName.length() > 30) rcName = rcName.substring(0, 27) + "...";
                rootCauseMap.put(rcName, (Long) row[1]);
            }
        }

        List<Map<String, Object>> trend = List.of(
                Map.of("hour", "09:00", "tickets", 2, "rca", 1),
                Map.of("hour", "10:00", "tickets", 5, "rca", 4),
                Map.of("hour", "11:00", "tickets", 8, "rca", 7),
                Map.of("hour", "12:00", "tickets", 4, "rca", 4),
                Map.of("hour", "13:00", "tickets", 6, "rca", 5)
        );

        Map<String, Object> savings = Map.of(
                "manualInvestigationMinutes", 180,
                "aiAssistedMinutes", 2,
                "manualTriageMinutes", 35,
                "aiTriageMinutes", 1,
                "disclaimer", "Simulated / Estimated metric comparing traditional manual operations vs AI-automated workflow."
        );

        return DashboardMetricsDto.builder()
                .ticketsByStatus(statusMap)
                .missingInfoFrequency(missingMap)
                .incidentsByService(serviceMap)
                .rootCauseCategories(rootCauseMap)
                .investigationTrend(trend)
                .timeSavingsComparison(savings)
                .build();
    }
}
