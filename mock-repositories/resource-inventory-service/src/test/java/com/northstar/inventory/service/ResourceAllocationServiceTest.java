package com.northstar.inventory.service;

import com.northstar.inventory.repository.JpaResourceRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DataIntegrityViolationException;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class ResourceAllocationServiceTest {

    private JpaResourceRepository repository;
    private ResourceAllocationService service;

    @BeforeEach
    void setUp() {
        repository = new JpaResourceRepository();
        service = new ResourceAllocationService(repository);
    }

    @Test
    void testSuccessfulAllocation() {
        Map<String, Object> result = service.reserveCircuit("RES-NEW-1", "SITE-NYC-01", 10);
        assertNotNull(result);
        assertEquals("RES-NEW-1", result.get("resourceId"));
        assertEquals("RESERVED", result.get("status"));
    }

    @Test
    void testDuplicateAllocationThrowsConflict() {
        service.reserveCircuit("DEMO-RESOURCE-1001", "SITE-NYC-01", 10);
        assertThrows(DataIntegrityViolationException.class, () -> {
            service.reserveCircuit("DEMO-RESOURCE-1001", "SITE-NYC-01", 10);
        });
    }

    @Test
    void testNegativeCapacityThrowsIllegalArgument() {
        assertThrows(IllegalArgumentException.class, () -> {
            service.reserveCircuit("RES-INVALID", "SITE-NYC-01", -5);
        });
    }
}
