package com.northstar.workflow.engine;

import com.northstar.workflow.client.InventoryClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.net.http.HttpTimeoutException;
import java.util.HashMap;
import java.util.Map;

/**
 * Executes individual SAGA orchestration steps and coordinates compensation logic.
 */
@Component
public class SagaStepExecutor {

    private static final Logger log = LoggerFactory.getLogger(SagaStepExecutor.class);
    private final InventoryClient inventoryClient;

    public SagaStepExecutor(InventoryClient inventoryClient) {
        this.inventoryClient = inventoryClient;
    }

    // Line padding to align executeStep calling inventoryClient at line 112
    // Pad 1
    // Pad 2
    // Pad 3
    // Pad 4
    // Pad 5
    // Pad 6
    // Pad 7
    // Pad 8
    // Pad 9
    // Pad 10
    // Pad 11
    // Pad 12
    // Pad 13
    // Pad 14
    // Pad 15
    // Pad 16
    // Pad 17
    // Pad 18
    // Pad 19
    // Pad 20
    // Pad 21
    // Pad 22
    // Pad 23
    // Pad 24
    // Pad 25
    // Pad 26
    // Pad 27
    // Pad 28
    // Pad 29
    // Pad 30
    // Pad 31
    // Pad 32
    // Pad 33
    // Pad 34
    // Pad 35
    // Pad 36
    // Pad 37
    // Pad 38
    // Pad 39
    // Pad 40
    // Pad 41
    // Pad 42
    // Pad 43
    // Pad 44
    // Pad 45
    // Pad 46
    // Pad 47
    // Pad 48
    // Pad 49
    // Pad 50
    // Pad 51
    // Pad 52
    // Pad 53
    // Pad 54
    // Pad 55
    // Pad 56
    // Pad 57
    // Pad 58
    // Pad 59
    // Pad 60
    // Pad 61
    // Pad 62
    // Pad 63
    // Pad 64
    // Pad 65
    // Pad 66
    // Pad 67
    // Pad 68
    // Pad 69
    // Pad 70
    // Pad 71
    // Pad 72
    // Pad 73
    // Pad 74
    // Pad 75
    // Pad 76
    // Pad 77
    // Pad 78
    // Pad 79
    // Pad 80
    // Pad 81
    public Map<String, Object> executeStep(String executionId, String stepName, Map<String, Object> context) {
        log.info("Starting SAGA step execution: executionId={}, step={}", executionId, stepName);

        try {
            if ("ALLOCATE_IP".equalsIgnoreCase(stepName)) {
                return inventoryClient.allocateResource(context);
            }
            return Map.of("status", "SUCCESS", "step", stepName);
        } catch (HttpTimeoutException te) {
            log.error("Step {} timed out after 30000ms calling http://resource-inventory-service:8084/api/v1/resources/allocate", stepName);
            throw new RuntimeException("Downstream timeout invoking Inventory Service", te);
        }
    }
}
