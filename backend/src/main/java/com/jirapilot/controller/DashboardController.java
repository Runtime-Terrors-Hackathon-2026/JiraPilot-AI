package com.jirapilot.controller;

import com.jirapilot.model.dto.DashboardMetricsDto;
import com.jirapilot.model.dto.DashboardSummaryDto;
import com.jirapilot.service.MetricsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final MetricsService metricsService;

    @GetMapping("/summary")
    public ResponseEntity<DashboardSummaryDto> getSummary() {
        return ResponseEntity.ok(metricsService.getSummary());
    }

    @GetMapping("/metrics")
    public ResponseEntity<DashboardMetricsDto> getMetrics() {
        return ResponseEntity.ok(metricsService.getMetrics());
    }
}
