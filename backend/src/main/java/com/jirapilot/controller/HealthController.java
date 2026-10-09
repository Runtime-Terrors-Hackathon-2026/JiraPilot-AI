package com.jirapilot.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/health")
public class HealthController {

    @Value("${jirapilot.demo-mode:true}")
    private boolean demoMode;

    @Value("${jirapilot.ai-service-url:http://localhost:8000}")
    private String aiServiceUrl;

    @GetMapping
    public ResponseEntity<Map<String, Object>> checkHealth() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "JiraPilot AI Orchestrator Backend",
                "demoMode", demoMode,
                "aiServiceUrl", aiServiceUrl,
                "timestamp", System.currentTimeMillis()
        ));
    }
}
