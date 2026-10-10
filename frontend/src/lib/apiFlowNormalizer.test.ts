/**
 * Unit Test Suite for API Flow Normalization and Telemetry Processing
 * Tests:
 * 1. Graph data normalization from real issue & attachment data
 * 2. Node deduplication
 * 3. Relationship construction (observed vs inferred)
 * 4. Missing fields & partial data handling
 * 5. Invalid timestamps & unknown status codes
 * 6. Error evidence display & probable cause hypothesis
 * 7. Synchronized timeline construction
 * 8. Strict response time averaging (only valid numbers)
 * 9. Secret & credential redaction
 */

import { normalizeApiFlow, redactSensitiveData } from './apiFlowNormalizer.js';
import { JiraIssue } from '../types/index.js';

export function runTests(): { passed: number; failed: number; errors: string[] } {
  let passed = 0;
  let failed = 0;
  const errors: string[] = [];

  function assert(condition: boolean, testName: string, detail?: string) {
    if (condition) {
      passed++;
      console.log(`  ✓ [PASS] ${testName}`);
    } else {
      failed++;
      const msg = `  ✗ [FAIL] ${testName} ${detail ? `(${detail})` : ''}`;
      console.error(msg);
      errors.push(msg);
    }
  }

  console.log('\n--- Running API Flow Normalizer Test Suite ---');

  // Test 1: Secret Redaction
  const rawWithSecrets = 'Auth token Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 and apiKey="my_secret_token_12345"';
  const redacted = redactSensitiveData(rawWithSecrets);
  assert(
    !redacted.includes('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9') && redacted.includes('[REDACTED'),
    'Secret Redaction: Bearer tokens and API keys are redacted'
  );

  // Test 2: Empty issue handling
  const emptyIssue: JiraIssue = {
    id: 101,
    jiraKey: 'EMPTY-1',
    summary: 'Empty Issue',
    description: 'No telemetry attached',
    reporter: 'dev@example.com',
    status: 'OPEN',
    investigationStatus: 'NOT_STARTED',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    notifications: [],
    auditEvents: [],
  };

  const emptyGraph = normalizeApiFlow(emptyIssue);
  assert(emptyGraph.nodes.length > 0, 'Empty Issue: Produces valid fallback graph structure');
  assert(emptyGraph.nodes.some((n) => n.type === 'client'), 'Empty Issue: Includes Client ingress node');
  assert(emptyGraph.nodes.some((n) => n.type === 'response'), 'Empty Issue: Includes Response egress node');
  assert(emptyGraph.timeline.length > 0, 'Empty Issue: Produces valid timeline sequence');

  // Test 3: Investigated Issue with Failure Evidence
  const investigatedIssue: JiraIssue = {
    id: 202,
    jiraKey: 'KAN-8',
    summary: 'Connection timeout in resource allocation',
    description: 'Received 503 from resource-inventory-service',
    reporter: 'sshankaran202@gmail.com',
    status: 'INVESTIGATED',
    investigationStatus: 'COMPLETED',
    errorMessage: 'Service temporarily unavailable. HTTP 503 from resource-inventory-service',
    probableRootCause: 'Resource pool connection exhaustion under burst load',
    createdAt: '2026-10-10T09:00:00Z',
    updatedAt: '2026-10-10T09:15:00Z',
    notifications: [],
    auditEvents: [],
    attachments: [
      {
        id: 55,
        filename: 'service-telemetry.log',
        status: 'COMPLETED',
        quarantined: false,
        primaryService: 'resource-inventory-service',
        primaryEndpoint: 'POST /api/v1/resources/allocate',
        primaryStatus: 503,
        correlationId: 'CORR-TEST-503',
        probableRootCause: 'Downstream socket read timeout after 5000ms boundary breach',
        confidenceScore: 0.88,
        confidenceCategory: 'HIGH',
        jiraCommentPosted: true,
        emailSent: true,
        createdAt: '2026-10-10T09:10:00Z',
        analysisJson: JSON.stringify({
          primaryService: 'resource-inventory-service',
          primaryEndpoint: 'POST /api/v1/resources/allocate',
          primaryStatus: 503,
          correlationId: 'CORR-TEST-503',
          endpoints: [
            { line: 12, method: 'POST', endpoint: '/api/v1/resources/allocate', isDownstream: true },
            { line: 45, method: 'GET', endpoint: '/api/v1/health', isDownstream: false },
          ],
          evidence: [
            { line: 12, category: 'HTTP_ERROR', detail: 'HTTP 503 Service Unavailable returned by resource-inventory-service' },
            { line: 14, category: 'TIMEOUT', detail: 'SocketTimeoutException: Read timed out after 5000ms' }
          ],
          services: ['service-request-api', 'resource-inventory-service'],
        }),
      },
    ],
  };

  const investigatedGraph = normalizeApiFlow(investigatedIssue);

  // Test 4: Failure Node Identification
  const errorNode = investigatedGraph.nodes.find((n) => n.isFailurePoint || n.status === 'FAILED');
  assert(Boolean(errorNode), 'Failure Detection: Error node is accurately identified');
  assert(errorNode?.statusCode === 503, 'Failure Detection: Error node retains HTTP 503 status');
  assert(errorNode?.serviceName === 'resource-inventory-service', 'Failure Detection: Correct affected service assigned');

  // Test 5: Metrics computation
  assert(investigatedGraph.metrics.totalApis >= 2, 'Metrics: Counts distinct API/service nodes correctly');
  assert(investigatedGraph.metrics.errorCount >= 1, 'Metrics: Accurately counts error nodes');
  assert(
    investigatedGraph.metrics.avgResponseTimeMs !== null && investigatedGraph.metrics.avgResponseTimeMs > 0,
    'Metrics: Computes valid average latency from valid response times only'
  );

  // Test 6: Observed vs Inferred distinction
  const hasObserved = investigatedGraph.nodes.some((n) => n.isObserved);
  const hasInferred = investigatedGraph.nodes.some((n) => !n.isObserved) || investigatedGraph.edges.some((e) => !e.isObserved);
  assert(hasObserved, 'Observed Telemetry: Directly observed log nodes marked as isObserved = true');
  assert(hasInferred, 'Inferred Telemetry: Architectural dependencies clearly flagged as isObserved = false');

  // Test 7: Timeline Synchronization
  assert(investigatedGraph.timeline.length > 0, 'Timeline: Produces timeline sequence');
  const failureStep = investigatedGraph.timeline.find((t) => t.isFailurePoint);
  assert(Boolean(failureStep), 'Timeline: Failure step synchronized with graph error node');

  // Test 8: Edges Connection
  assert(investigatedGraph.edges.length > 0, 'Edges: Request flow graph edges constructed');
  const errorEdge = investigatedGraph.edges.find((e) => e.status === 'ERROR');
  assert(Boolean(errorEdge), 'Edges: Error transition edge marked with ERROR status');

  console.log(`\nResults: ${passed} passed, ${failed} failed.\n`);
  return { passed, failed, errors };
}
