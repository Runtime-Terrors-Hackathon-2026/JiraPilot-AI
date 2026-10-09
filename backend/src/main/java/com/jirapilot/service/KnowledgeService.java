package com.jirapilot.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

@Slf4j
@Service
@RequiredArgsConstructor
public class KnowledgeService {

    private final List<Map<String, Object>> memoryKnowledge = new CopyOnWriteArrayList<>();

    public List<Map<String, Object>> getAllKnowledge() {
        if (memoryKnowledge.isEmpty()) {
            loadDefaultKnowledge();
        }
        return memoryKnowledge;
    }

    public synchronized void saveKnowledge(Map<String, Object> record) {
        memoryKnowledge.add(record);
        log.info("[KNOWLEDGE] Saved new resolved incident into knowledge memory: {}", record.get("jiraKey"));
    }

    private void loadDefaultKnowledge() {
        memoryKnowledge.addAll(List.of(
                Map.of(
                        "jiraKey", "HACK-102",
                        "summary", "PEDS circuit provisioning failure due to duplicate NFID from upstream",
                        "affectedService", "PEDS",
                        "affectedApi", "POST /api/circuit/provision",
                        "rootCause", "Duplicate NFID received from upstream NTLS integration causing unique constraint violation in PEDS DB.",
                        "resolution", "Added NFID idempotency cache layer and pre-validation uniqueness check before database persist.",
                        "similarityScore", 91
                ),
                Map.of(
                        "jiraKey", "HACK-205",
                        "summary", "WFM downstream timeout when communicating with Inventory Service",
                        "affectedService", "WFM",
                        "affectedApi", "POST /api/work-order/dispatch",
                        "rootCause", "Connection pool exhaustion on Inventory Service downstream endpoint during peak traffic hours.",
                        "resolution", "Increased HikariCP max pool size to 50 and reduced HTTP client timeout with circuit breaker fallback.",
                        "similarityScore", 85
                ),
                Map.of(
                        "jiraKey", "HACK-318",
                        "summary", "Circuit Service NullPointerException in payload deserialization",
                        "affectedService", "CIRCUIT-SVC",
                        "affectedApi", "POST /api/circuit/create",
                        "rootCause", "Missing null check for customerId in incoming JSON request payload.",
                        "resolution", "Added @NotNull validation annotation and custom GlobalExceptionHandler.",
                        "similarityScore", 78
                )
        ));
    }
}
