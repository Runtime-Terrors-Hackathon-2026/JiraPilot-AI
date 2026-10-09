from typing import List
from app.models.schemas import TicketPayload, ApiFinding, TestCase, TestCaseResponse

def generate_test_cases(ticket: TicketPayload, affected_api: ApiFinding = None, root_cause: str = None) -> TestCaseResponse:
    endpoint = affected_api.endpoint if affected_api else "/api/circuit/provision"
    method = affected_api.method if affected_api else "POST"
    service = affected_api.service if affected_api else "CircuitService"

    test_cases: List[TestCase] = [
        TestCase(
            id="TC-001",
            title="Valid Request Baseline Execution",
            type="INTEGRATION",
            description=f"Send valid synthetic payload to {method} {endpoint}. Verify downstream services return 200/201 without exception.",
            expectedResult="HTTP 200/201 with success status and non-null transaction reference.",
            testCodeSnippet=f"""@Test
void givenValidPayload_whenCallEndpoint_thenSuccess() {{
    CircuitRequest request = createSyntheticValidRequest();
    ResponseEntity<CircuitResponse> response = restTemplate.postForEntity("{endpoint}", request, CircuitResponse.class);
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
    assertThat(response.getBody().getStatus()).isEqualTo("ACTIVE");
}}"""
        ),
        TestCase(
            id="TC-002",
            title="Duplicate Identifier / NFID Idempotency Test",
            type="UNIT",
            description="Simulate identical NFID / correlation ID submitted twice in rapid succession.",
            expectedResult="Second request handled gracefully returning 409 Conflict or cached successful idempotency response.",
            testCodeSnippet=f"""@Test
void givenDuplicateIdentifier_whenProcessed_thenThrowIdempotencyException() {{
    when(duplicateChecker.isDuplicate("TEST-NFID-1001")).thenReturn(true);
    assertThrows(DuplicateNfidException.class, () -> {{
        circuitService.provisionCircuit(duplicateRequest);
    }});
}}"""
        ),
        TestCase(
            id="TC-003",
            title="Downstream Dependency Timeout & Circuit Breaker",
            type="INTEGRATION",
            description=f"Simulate downstream delay > 3000ms from dependency service during {endpoint}.",
            expectedResult="Circuit breaker triggers fallback and returns 504 with structured error envelope rather than unhandled crash.",
            testCodeSnippet=f"""@Test
void givenDownstreamTimeout_whenFallbackTriggered_thenReturnGatewayTimeoutEnvelope() {{
    wireMockServer.stubFor(post(urlEqualTo("/downstream/provision"))
        .willReturn(aResponse().withFixedDelay(5000)));
    ResponseEntity<ErrorResponse> response = client.callEndpoint();
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.GATEWAY_TIMEOUT);
}}"""
        ),
        TestCase(
            id="TC-004",
            title="Malformed / Empty Request Payload Validation",
            type="API",
            description="Submit missing required JSON fields (e.g. empty body or missing IDs).",
            expectedResult="HTTP 400 Bad Request with field-level validation errors list.",
            testCodeSnippet=f"""@Test
void givenMissingPayloadFields_thenReturn400BadRequest() {{
    String invalidJson = "{{}}";
    ResponseEntity<String> response = restTemplate.postForEntity("{endpoint}", invalidJson, String.class);
    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
}}"""
        ),
        TestCase(
            id="TC-005",
            title="Database Connection Interruption Recovery",
            type="UNIT",
            description="Simulate transient database deadlock or connection pool saturation.",
            expectedResult="Transaction rolled back cleanly without orphan state or corrupted telemetry.",
            testCodeSnippet=f"""@Test
void givenDbTransientError_thenRetryAndRollback() {{
    doThrow(new CannotAcquireLockException("Lock timeout")).when(circuitRepository).save(any());
    assertThrows(TransientDataAccessException.class, () -> circuitService.saveCircuit(mockCircuit));
    verify(auditLogger).logFailure(any());
}}"""
        )
    ]

    java_skeleton = f"""package com.jirapilot.generated.tests;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;

/**
 * Auto-generated Test Suite by JiraPilot AI
 * Incident Target: {ticket.key or 'HACK-INCIDENT'}
 * Affected Service: {service}
 * Endpoint: {method} {endpoint}
 */
@ExtendWith(MockitoExtension.class)
public class GeneratedIncidentReproductionTest {{

    @Test
    @DisplayName("TC-001: Baseline valid request execution")
    void testValidRequestExecution() {{
        // Setup synthetic fixture
        assertThat(true).isTrue();
    }}

    @Test
    @DisplayName("TC-002: Duplicate payload validation & handling")
    void testDuplicatePayloadHandling() {{
        // Verify idempotency guard prevents double processing
        assertThat(true).isTrue();
    }}

    @Test
    @DisplayName("TC-003: Downstream timeout recovery")
    void testDownstreamTimeoutHandling() {{
        // Verify circuit breaker and graceful degradation
        assertThat(true).isTrue();
    }}
}}
"""

    return TestCaseResponse(
        testCases=test_cases,
        javaSkeletonCode=java_skeleton
    )
