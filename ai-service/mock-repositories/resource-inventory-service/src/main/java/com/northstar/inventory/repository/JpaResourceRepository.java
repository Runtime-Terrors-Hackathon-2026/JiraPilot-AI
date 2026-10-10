package com.northstar.inventory.repository;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Repository;

import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

/**
 * Repository interface and simulated persistence adapter for circuit resources.
 */
@Repository
public class JpaResourceRepository {

    private static final Logger log = LoggerFactory.getLogger(JpaResourceRepository.class);
    private final Map<String, Map<String, Object>> storage = new ConcurrentHashMap<>();

    public boolean existsByResourceId(String resourceId) {
        return storage.containsKey(resourceId);
    }

    public Map<String, Object> findByResourceId(String resourceId) {
        return storage.get(resourceId);
    }

    // Line padding to align save method throwing exception at line 94
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
    public Map<String, Object> save(Map<String, Object> record) {
        String id = (String) record.get("resourceId");
        if (storage.containsKey(id)) {
            log.error("Unique index collision on table circuit_resources for key: {}", id);
            throw new DataIntegrityViolationException("Pre-existing allocation detected for resource ID: " + id);
        }
        storage.put(id, record);
        return record;
    }
}
