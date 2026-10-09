from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TicketPayload(BaseModel):
    key: Optional[str] = "HACK-NEW"
    summary: Optional[str] = ""
    description: Optional[str] = ""
    reporter: Optional[str] = "reporter@example.com"
    environment: Optional[str] = None
    apiDetails: Optional[str] = None
    logs: Optional[str] = None
    requestPayload: Optional[str] = None
    responsePayload: Optional[str] = None
    errorMessage: Optional[str] = None
    expectedBehavior: Optional[str] = None
    actualBehavior: Optional[str] = None
    replicationSteps: Optional[str] = None
    screenshots: Optional[List[str]] = []
    comments: Optional[List[Dict[str, Any]]] = []

class ReadinessScoreWeights(BaseModel):
    description: int = 10
    apiDetails: int = 15
    logs: int = 20
    requestPayload: int = 15
    environment: int = 10
    errorMessage: int = 10
    expectedActualBehavior: int = 10
    replicationSteps: int = 5
    screenshots: int = 5

class ValidationRequest(BaseModel):
    ticket: TicketPayload
    weights: Optional[ReadinessScoreWeights] = None

class ValidationResponse(BaseModel):
    readinessScore: int
    status: str # "READY", "NEEDS_INFORMATION"
    missingInformation: List[str]
    availableInformation: List[str]
    reason: str
    suggestedJiraComment: str
    suggestedEmailBody: str

class ParsedLogEntry(BaseModel):
    timestamp: Optional[str] = None
    logLevel: Optional[str] = "INFO"
    serviceName: Optional[str] = None
    correlationId: Optional[str] = None
    requestId: Optional[str] = None
    httpMethod: Optional[str] = None
    endpoint: Optional[str] = None
    statusCode: Optional[int] = None
    exceptionClass: Optional[str] = None
    message: str
    rawLine: str

class LogParseRequest(BaseModel):
    logs: str

class LogParseResponse(BaseModel):
    entries: List[ParsedLogEntry]
    correlatedIdGroups: Dict[str, List[ParsedLogEntry]]
    detectedServices: List[str]
    detectedExceptions: List[str]
    detectedEndpoints: List[str]
    probableErrorSummary: str

class ApiFinding(BaseModel):
    method: str
    endpoint: str
    service: str
    downstreamService: Optional[str] = None
    statusCode: Optional[int] = None
    latencyMs: Optional[int] = None
    failureReason: str

class ServiceDependencyNode(BaseModel):
    id: str
    name: str
    type: str # "gateway", "service", "downstream", "database"
    status: str # "HEALTHY", "DEGRADED", "FAILED"
    isFailurePoint: bool = False
    details: Optional[str] = None

class ServiceDependencyEdge(BaseModel):
    source: str
    target: str
    label: Optional[str] = None
    status: str = "NORMAL"

class TimelineEvent(BaseModel):
    time: str
    title: str
    description: str
    stage: str # "INGESTION", "VALIDATION", "NOTIFICATION", "LOG_PARSING", "API_IDENTIFICATION", "ROOT_CAUSE", "RCA_GENERATION"
    status: str = "COMPLETED"

class RootCauseAnalysis(BaseModel):
    executiveSummary: str
    incidentTimeline: List[TimelineEvent]
    affectedApi: ApiFinding
    affectedService: str
    downstreamDependency: Optional[str] = None
    errorPattern: str
    failurePoint: str
    probableRootCause: str
    rootCauseConfidence: int # 0-100
    confidenceLevel: str # "HIGH", "MEDIUM", "LOW"
    supportingEvidence: List[str]
    recommendedInvestigationSteps: List[str]
    recommendedFix: str
    serviceGraphNodes: List[ServiceDependencyNode]
    serviceGraphEdges: List[ServiceDependencyEdge]
    jiraInvestigationComment: str

class InvestigationRequest(BaseModel):
    ticket: TicketPayload
    parsedLogs: Optional[LogParseResponse] = None

class InvestigationResponse(BaseModel):
    rca: RootCauseAnalysis
    reproductionCurl: str
    postmanJson: str
    generatedTestCases: List[Dict[str, Any]]
    similarIncidents: List[Dict[str, Any]]

class SimilarIncident(BaseModel):
    jiraKey: str
    summary: str
    similarityScore: int # 0-100
    affectedService: str
    affectedApi: str
    rootCause: str
    resolution: str
    explanation: str

class SimilarityRequest(BaseModel):
    currentTicket: TicketPayload
    limit: Optional[int] = 3

class SimilarityResponse(BaseModel):
    similarIncidents: List[SimilarIncident]

class TestCase(BaseModel):
    id: str
    title: str
    type: str # "UNIT", "INTEGRATION", "API"
    description: str
    expectedResult: str
    testCodeSnippet: Optional[str] = None

class TestCaseRequest(BaseModel):
    ticket: TicketPayload
    affectedApi: Optional[ApiFinding] = None
    rootCause: Optional[str] = None

class TestCaseResponse(BaseModel):
    testCases: List[TestCase]
    javaSkeletonCode: str

class ReproductionRequest(BaseModel):
    ticket: TicketPayload
    apiFinding: Optional[ApiFinding] = None

class ReproductionResponse(BaseModel):
    curlCommand: str
    postmanPayload: Dict[str, Any]
    pythonRequestSnippet: str
