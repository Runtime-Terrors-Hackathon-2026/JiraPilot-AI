export type AppView =
  | 'overview'
  | 'issues'
  | 'logs'
  | 'repos'
  | 'knowledge'
  | 'notifications'
  | 'settings'
  | 'api-flow';

export interface ApiFlowNode {
  id: string;
  label: string;
  type: 'client' | 'api' | 'service' | 'response';
  serviceName: string;
  endpoint?: string;
  method?: string;
  statusCode?: number;
  statusText?: string;
  responseTimeMs?: number;
  status: 'HEALTHY' | 'DEGRADED' | 'FAILED' | 'UNKNOWN';
  isFailurePoint: boolean;
  timestamp?: string;
  correlationId?: string;
  traceId?: string;
  sourceLog?: string;
  lineNumber?: number;
  errorMessage?: string;
  possibleCause?: string;
  confidenceLevel?: string;
  evidenceReference?: string;
  relatedLogs?: Array<{ line: number; text: string }>;
  requestPayload?: string;
  responsePayload?: string;
  curlCommand?: string;
  isObserved: boolean;
  inferredReason?: string;
  branch: 'main' | 'top' | 'bottom';
  x: number;
  y: number;
}

export interface ApiFlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  status: 'NORMAL' | 'ERROR';
  isObserved: boolean;
  inferredReason?: string;
  dashed?: boolean;
}

export interface ApiFlowTimelineStep {
  stepNumber: number;
  nodeId: string;
  label: string;
  service: string;
  endpoint?: string;
  status: 'HEALTHY' | 'DEGRADED' | 'FAILED';
  duration?: string;
  isFailurePoint: boolean;
}

export interface ApiFlowMetrics {
  totalApis: number;
  successfulCount: number;
  errorCount: number;
  avgResponseTimeMs: number | null;
  hasInferredData: boolean;
}

export interface ApiFlowGraphData {
  nodes: ApiFlowNode[];
  edges: ApiFlowEdge[];
  timeline: ApiFlowTimelineStep[];
  metrics: ApiFlowMetrics;
  evidenceSummary: string[];
}

export type IssueFilter = 'ALL' | 'WAITING' | 'READY' | 'INVESTIGATING' | 'INVESTIGATED';

export type IssueStatus = 'OPEN' | 'WAITING_FOR_INFORMATION' | 'READY' | 'INVESTIGATING' | 'INVESTIGATED' | 'RESOLVED';
export type InvestigationStatus = 'NOT_STARTED' | 'RUNNING' | 'COMPLETED' | 'FAILED';
export type ConfidenceLevel = 'HIGH' | 'MEDIUM' | 'LOW';

export interface ValidationResult {
  readinessScore: number;
  status: string;
  missingInformation: string[];
  availableInformation: string[];
  reason: string;
  suggestedJiraComment: string;
  suggestedEmailBody: string;
}

export interface ServiceNode {
  id: string;
  name: string;
  type: 'gateway' | 'service' | 'downstream' | 'database';
  status: 'HEALTHY' | 'DEGRADED' | 'FAILED';
  isFailurePoint: boolean;
  details?: string;
}

export interface ServiceEdge {
  source: string;
  target: string;
  label?: string;
  status: 'NORMAL' | 'ERROR';
}

export interface TimelineEvent {
  time: string;
  title: string;
  description: string;
  stage: string;
  status: string;
}

export interface TestCase {
  id: string;
  title: string;
  type: 'UNIT' | 'INTEGRATION' | 'API';
  description: string;
  expectedResult: string;
  testCodeSnippet?: string;
}

export interface SimilarIncident {
  jiraKey: string;
  summary: string;
  similarityScore: number;
  affectedService: string;
  affectedApi: string;
  rootCause: string;
  resolution: string;
  explanation: string;
}

export interface RcaData {
  executiveSummary: string;
  affectedService: string;
  downstreamDependency?: string;
  errorPattern: string;
  failurePoint: string;
  probableRootCause: string;
  rootCauseConfidence: number;
  confidenceLevel: ConfidenceLevel;
  supportingEvidence: string[];
  recommendedInvestigationSteps: string[];
  recommendedFix: string;
  jiraInvestigationComment: string;
  affectedApi?: {
    method: string;
    endpoint: string;
    service: string;
    downstreamService?: string;
    statusCode?: number;
    latencyMs?: number;
    failureReason: string;
  };
  serviceGraphNodes?: ServiceNode[];
  serviceGraphEdges?: ServiceEdge[];
  incidentTimeline?: TimelineEvent[];
}

export type CodeInvestigationStatus =
  | 'WAITING_FOR_REPOSITORY'
  | 'REPOSITORY_ACCESS_REQUIRED'
  | 'REPOSITORY_INDEXING'
  | 'SEARCHING_SOURCE_CODE'
  | 'TRACING_EXECUTION_PATH'
  | 'GENERATING_DIAGNOSIS'
  | 'READY_FOR_REVIEW'
  | 'INSUFFICIENT_EVIDENCE'
  | 'ANALYSIS_FAILED';

export interface InspectedSymbol {
  filePath: string;
  className?: string;
  methodName?: string;
  startLine: number;
  endLine: number;
  snippet: string;
  role: 'CONTROLLER' | 'SERVICE' | 'REPOSITORY' | 'CLIENT' | 'EXCEPTION_HANDLER' | 'TEST' | 'CONFIG';
}

export interface ExecutionPathStep {
  stepNumber: number;
  service: string;
  className: string;
  methodName: string;
  filePath: string;
  startLine: number;
  endLine: number;
  reason: string;
  evidenceType: 'OBSERVED' | 'STATICALLY_INFERRED' | 'UNCERTAIN';
  evidenceReference?: string;
  snippet?: string;
}

export interface FailureLocation {
  category: 'OBSERVED' | 'PROPAGATED' | 'ROOT_CAUSE';
  title: string;
  description: string;
  filePath: string;
  className: string;
  methodName: string;
  line: number;
  snippet: string;
  evidenceReason: string;
}

export interface CodeDiff {
  filePath: string;
  targetMethod: string;
  originalSnippet: string;
  proposedSnippet: string;
  unifiedDiff: string;
  purpose: string;
  affectedRisks: string[];
  affectedFiles: string[];
}

export interface TestRecommendation {
  testType: 'UNIT' | 'INTEGRATION' | 'REGRESSION';
  testClass: string;
  testMethod: string;
  filePath: string;
  isExistingTest: boolean;
  codeSnippet: string;
  runCommand: string;
  explanation: string;
}

export interface CodeInvestigationReport {
  investigationId: string;
  jiraKey: string;
  status: CodeInvestigationStatus;
  serviceName: string;
  repositoryId: string;
  repositoryName: string;
  repositoryUrl: string;
  revision: string;
  accessPermission: string;
  executiveSummary: string;
  observedSymptoms: string[];
  confirmedFacts: string[];
  suspectedCause: string;
  alternativeHypotheses: string[];
  filesInspected: string[];
  symbolsInspected: InspectedSymbol[];
  executionPath: ExecutionPathStep[];
  failureLocations: FailureLocation[];
  recommendedFix: string;
  codeDiff?: CodeDiff;
  testRecommendations: TestRecommendation[];
  confidenceScore: number;
  confidenceExplanation: string;
  limitations: string[];
  unresolvedQuestions: string[];
  timestamp: string;
  isStale?: boolean;
}

export interface InvestigationResult {
  rca: RcaData;
  reproductionCurl: string;
  postmanJson: string;
  generatedTestCases: TestCase[];
  similarIncidents: SimilarIncident[];
  codeInvestigation?: CodeInvestigationReport;
}

export interface MockEmail {
  id: number;
  jiraKey: string;
  recipient: string;
  subject: string;
  content: string;
  status: string;
  sentAt: string;
}

export interface AuditEvent {
  id: number;
  eventType: string;
  workflowStage: string;
  details: string;
  status: string;
  durationMs: number;
  timestamp: string;
}

export interface JiraIssue {
  id: number;
  jiraKey: string;
  key?: string;
  summary: string;
  description: string;
  reporter: string;
  environment?: string;
  apiDetails?: string;
  logs?: string;
  requestPayload?: string;
  responsePayload?: string;
  errorMessage?: string;
  expectedBehavior?: string;
  actualBehavior?: string;
  replicationSteps?: string;
  status: IssueStatus;
  investigationStatus: InvestigationStatus;
  readinessScore?: number;
  affectedService?: string;
  probableRootCause?: string;
  aiConfidence?: number;
  createdAt: string;
  updatedAt: string;
  validation?: ValidationResult;
  investigation?: InvestigationResult;
  notifications: MockEmail[];
  auditEvents: AuditEvent[];
  attachments?: IssueAttachment[];
}

export interface IssueAttachment {
  id: number;
  attachmentId?: string;
  filename: string;
  mimeType?: string;
  sizeBytes?: number;
  sha256Hash?: string;
  status: 'RECEIVED' | 'VALIDATING' | 'ANALYZING' | 'COMPLETED' | 'NEEDS_REVIEW' | 'FAILED';
  quarantined: boolean;
  quarantineReason?: string;
  primaryService?: string;
  primaryEndpoint?: string;
  primaryStatus?: number;
  correlationId?: string;
  probableRootCause?: string;
  confidenceScore?: number;
  confidenceCategory?: string;
  recommendedRepo?: string;
  cloneCommand?: string;
  analysisSummary?: string;
  analysisJson?: string;
  jiraCommentPosted: boolean;
  emailSent: boolean;
  createdAt: string;
  analyzedAt?: string;
}

export interface BackendHealth {
  status: string;
  service: string;
  demoMode: boolean;
  aiServiceUrl: string;
  timestamp: number;
}

export interface NvidiaStatus {
  provider: string;
  enabled: boolean;
  configured: boolean;
  model: string;
  baseUrl: string;
  timeoutSeconds: number;
  activeMode: string;
}

export interface DashboardSummary {
  totalTickets: number;
  readyTickets: number;
  waitingForInfoTickets: number;
  investigationsRunning: number;
  rcaCompleted: number;
  averageReadinessScore: number;
  estimatedHoursSaved: number;
}

export interface DashboardMetrics {
  ticketsByStatus: Record<string, number>;
  missingInfoFrequency: Record<string, number>;
  incidentsByService: Record<string, number>;
  rootCauseCategories: Record<string, number>;
  investigationTrend: Array<{ hour: string; tickets: number; rca: number }>;
  timeSavingsComparison: {
    manualInvestigationMinutes: number;
    aiAssistedMinutes: number;
    manualTriageMinutes: number;
    aiTriageMinutes: number;
    disclaimer: string;
  };
}

export interface PolicySettings {
  weightDescription: number;
  weightApiDetails: number;
  weightLogs: number;
  weightRequestPayload: number;
  weightEnvironment: number;
  weightErrorMessage: number;
  weightExpectedActualBehavior: number;
  weightReplicationSteps: number;
  weightScreenshots: number;
  readinessThreshold: number;
  confidenceThreshold: number;
  similarityThreshold: number;
  autoCommentEnabled: boolean;
  autoEmailEnabled: boolean;
  autoInvestigateEnabled: boolean;
}

