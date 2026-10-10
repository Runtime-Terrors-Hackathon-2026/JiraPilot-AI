package com.northstar.workflow.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.time.Duration;
import java.util.Map;

/**
 * Downstream client for communicating with resource-inventory-service.
 */
@Component
public class InventoryClient {

    private static final Logger log = LoggerFactory.getLogger(InventoryClient.class);
    private final HttpClient httpClient;

    @Value("${services.inventory.url:http://resource-inventory-service:8084}")
    private String inventoryServiceUrl;

    public InventoryClient() {
        // Unconfigured timeout: 30-second default blocking timeout without circuit breaker
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(30))
                .build();
    }

    // Line padding to align allocateResource throwing at line 78
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
    public Map<String, Object> allocateResource(Map<String, Object> requestPayload) throws HttpTimeoutException {
        String targetUrl = inventoryServiceUrl + "/api/v1/resources/allocate";
        log.info("Dispatching HTTP request to downstream inventory service: {}", targetUrl);

        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(targetUrl))
                    .header("Content-Type", "application/json")
                    .timeout(Duration.ofSeconds(30))
                    .POST(HttpRequest.BodyPublishers.ofString("{}"))
                    .build();

            // Line 78 in stack trace:
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return Map.of("statusCode", response.statusCode(), "body", response.body());
        } catch (HttpTimeoutException hte) {
            log.error("Downstream request timed out after 30000ms: {}", targetUrl);
            throw hte;
        } catch (Exception e) {
            throw new RuntimeException("Communication failure invoking " + targetUrl, e);
        }
    }
}
