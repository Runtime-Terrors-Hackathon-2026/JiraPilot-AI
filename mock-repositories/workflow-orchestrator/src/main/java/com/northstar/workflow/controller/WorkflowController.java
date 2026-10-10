package com.northstar.workflow.controller;

import com.northstar.workflow.service.WorkflowService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/workflows")
public class WorkflowController {

    private final WorkflowService workflowService;

    public WorkflowController(WorkflowService workflowService) {
        this.workflowService = workflowService;
    }

    @PostMapping("/start")
    public ResponseEntity<Map<String, Object>> startWorkflow(@RequestBody Map<String, Object> payload) {
        Map<String, Object> result = workflowService.startWorkflow(payload);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{executionId}/status")
    public ResponseEntity<Map<String, Object>> getStatus(@PathVariable String executionId) {
        return ResponseEntity.ok(workflowService.getExecutionStatus(executionId));
    }
}
