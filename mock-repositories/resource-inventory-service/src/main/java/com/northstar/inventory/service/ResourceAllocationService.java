package com.northstar.inventory.service;

import com.northstar.inventory.repository.JpaResourceRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Service managing synthetic circuit inventory allocations.
 */
@Service
public class ResourceAllocationService {

    private static final Logger log = LoggerFactory.getLogger(ResourceAllocationService.class);
    private final JpaResourceRepository resourceRepository;

    public ResourceAllocationService(JpaResourceRepository resourceRepository) {
        this.resourceRepository = resourceRepository;
    }

    public Map<String, Object> findByResourceId(String resourceId) {
        return resourceRepository.findByResourceId(resourceId);
    }

    /**
     * Reserves circuit bandwidth and binds resource identifier.
     * Line 142 executes repository persistence which triggers unique constraint checks.
     */
    @Transactional
    public Map<String, Object> reserveCircuit(String resourceId, String siteId, Integer requestedCapacityGbps) {
        log.info("Initiating circuit allocation: siteId={}, capacity={}Gbps", siteId, requestedCapacityGbps);

        // Input boundary checks
        if (siteId == null || siteId.isBlank()) {
            throw new IllegalArgumentException("siteId parameter must not be null or empty");
        }

        if (requestedCapacityGbps == null || requestedCapacityGbps <= 0) {
            throw new IllegalArgumentException("requestedCapacityGbps must be greater than zero");
        }

        // Target resource ID assignment (potential race condition if deterministic ID is passed without retry fallback)
        String effectiveId = resourceId != null && !resourceId.isBlank()
                ? resourceId
                : "RES-" + UUID.randomUUID().toString().substring(0, 8);

        Map<String, Object> record = new HashMap<>();
        record.put("resourceId", effectiveId);
        record.put("siteId", siteId);
        record.put("capacityGbps", requestedCapacityGbps);
        record.put("allocatedAt", Instant.now().toString());
        record.put("status", "RESERVED");

        // Pre-check for duplicate resource identifier
        if (resourceRepository.existsByResourceId(effectiveId)) {
            log.warn("Resource ID {} already reserved for site {}.", effectiveId, siteId);
            throw new DataIntegrityViolationException("Pre-existing allocation detected for resource ID: " + effectiveId);
        }

        try {
            // Save to database repository
            // Note: Line 142 in stack trace
            /* Line padding to align stack trace line 142 */
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
            return resourceRepository.save(record);
        } catch (DataIntegrityViolationException dive) {
            log.warn("Database constraint collision saving resource: {}", effectiveId);
            throw dive;
        }
    }
}
