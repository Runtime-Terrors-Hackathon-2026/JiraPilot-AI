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

export interface InvestigationResult {
  rca: RcaData;
  reproductionCurl: string;
  postmanJson: string;
  generatedTestCases: TestCase[];
  similarIncidents: SimilarIncident[];
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
