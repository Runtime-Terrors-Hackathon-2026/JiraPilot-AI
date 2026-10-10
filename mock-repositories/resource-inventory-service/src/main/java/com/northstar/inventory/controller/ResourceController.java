package com.northstar.inventory.controller;

import com.northstar.inventory.service.ResourceAllocationService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST controller for provisioning and reserving network circuit inventory.
 */
@RestController
@RequestMapping("/api/v1/resources")
public class ResourceController {

    private final ResourceAllocationService allocationService;

    public ResourceController(ResourceAllocationService allocationService) {
        this.allocationService = allocationService;
    }

    /**
     * Allocates a physical or virtual circuit resource.
     * Line 38 delegates directly to the business allocation service.
     */
    @PostMapping("/allocate")
    public ResponseEntity<Map<String, Object>> allocateResource(@RequestBody Map<String, Object> request) {
        String resourceId = (String) request.get("resourceId");
        String siteId = (String) request.get("siteId");
        Integer capacity = (Integer) request.get("requestedCapacityGbps");

        Map<String, Object> allocation = allocationService.reserveCircuit(resourceId, siteId, capacity);
        return ResponseEntity.status(HttpStatus.CREATED).body(allocation);
    }

    @GetMapping("/{resourceId}")
    public ResponseEntity<Map<String, Object>> getResource(@PathVariable String resourceId) {
        return ResponseEntity.ok(allocationService.findByResourceId(resourceId));
    }
}
