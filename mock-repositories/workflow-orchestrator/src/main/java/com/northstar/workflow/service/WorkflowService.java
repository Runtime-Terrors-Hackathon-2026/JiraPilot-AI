package com.northstar.workflow.service;

import com.northstar.workflow.engine.SagaStepExecutor;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.UUID;

@Service
public class WorkflowService {

    private final SagaStepExecutor stepExecutor;

    public WorkflowService(SagaStepExecutor stepExecutor) {
        this.stepExecutor = stepExecutor;
    }

    public Map<String, Object> startWorkflow(Map<String, Object> request) {
        String executionId = "WF-EXEC-" + UUID.randomUUID().toString().substring(0, 8);
        return stepExecutor.executeStep(executionId, "ALLOCATE_IP", request);
    }

    public Map<String, Object> getExecutionStatus(String executionId) {
        return Map.of("executionId", executionId, "status", "RUNNING");
    }
}
