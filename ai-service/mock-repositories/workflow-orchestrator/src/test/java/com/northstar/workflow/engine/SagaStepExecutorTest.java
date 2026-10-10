package com.northstar.workflow.engine;

import com.northstar.workflow.client.InventoryClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.net.http.HttpTimeoutException;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class SagaStepExecutorTest {

    private SagaStepExecutor executor;

    @BeforeEach
    void setUp() {
        InventoryClient client = new InventoryClient();
        executor = new SagaStepExecutor(client);
    }

    @Test
    void testNonInventoryStepSucceeds() {
        Map<String, Object> result = executor.executeStep("WF-TEST-1", "VALIDATE", Map.of());
        assertEquals("SUCCESS", result.get("status"));
        assertEquals("VALIDATE", result.get("step"));
    }
}
