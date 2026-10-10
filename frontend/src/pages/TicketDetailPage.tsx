import React, { useState } from 'react';
import { JiraIssue } from '../types';
import { api } from '../api/client';
import { ServiceGraph } from '../components/ServiceGraph';
import { TimelineViewer } from '../components/TimelineViewer';
import { TestCaseList } from '../components/TestCaseList';
import { CurlViewer } from '../components/CurlViewer';
import { LogInvestigationCard } from '../components/LogInvestigationCard';
import { CodeInvestigationCard } from '../components/CodeInvestigationCard';
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Send,
  MessageSquare,
  ShieldCheck,
  Zap,
  Activity,
  Sparkles,
  Copy,
  Check,
  Network,
} from 'lucide-react';
import {
  Button,
  Card,
  StatusBadge,
  ReadinessIndicator,
  AnalysisProgress,
} from '../components/ui/primitives';
import { useToast } from '../components/ui/Toast';
import { issueTone, latestAttachment } from '../lib/status';
import { labelStatus, formatDateTime } from '../lib/format';
import { ANALYSIS_STAGES, LOADING_MESSAGES } from '../lib/messaging';

interface TicketDetailPageProps {
  issue: JiraIssue;
  onBack: () => void;
  onRefresh: () => void;
  onExploreApiFlow?: (key: string) => void;
}

export const TicketDetailPage: React.FC<TicketDetailPageProps> = ({
  issue,
  onBack,
  onRefresh,
  onExploreApiFlow,
}) => {
  const { push } = useToast();
  const [revalidating, setRevalidating] = useState(false);
  const [investigating, setInvestigating] = useState(false);
  const [postingComment, setPostingComment] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [updateLogs, setUpdateLogs] = useState('');
  const [showLogUpdateBox, setShowLogUpdateBox] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);

  const rca = issue.investigation?.rca;
  const isInvestigated =
    issue.status === 'INVESTIGATED' || issue.investigationStatus === 'COMPLETED';
  const isWaiting = issue.status === 'WAITING_FOR_INFORMATION';

  const triggerRevalidate = async () => {
    setRevalidating(true);
    try {
      await api.revalidateIssue(issue.jiraKey);
      onRefresh();
      push({ kind: 'success', title: 'Diagnostic validation re-run completed' });
    } catch (e: any) {
      push({ kind: 'error', title: 'Validation failed', message: e.message });
    } finally {
      setRevalidating(false);
    }
  };

  const triggerInvestigate = async () => {
    setInvestigating(true);
    try {
      await api.investigateIssue(issue.jiraKey);
      onRefresh();
      push({
        kind: 'success',
        title: 'Root Cause Analysis & Test Suite generation completed',
      });
    } catch (e: any) {
      push({ kind: 'error', title: 'Investigation failed', message: e.message });
    } finally {
      setInvestigating(false);
    }
  };

  const handlePostInvestigationToJira = async () => {
    if (!rca?.jiraInvestigationComment) return;
    setPostingComment(true);
    try {
      await api.postComment(issue.jiraKey, rca.jiraInvestigationComment);
      onRefresh();
      push({ kind: 'success', title: 'Investigation report posted to Jira issue' });
    } catch (e: any) {
      push({ kind: 'error', title: 'Failed to post comment', message: e.message });
    } finally {
      setPostingComment(false);
    }
  };

  const handlePostCustomComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setPostingComment(true);
    try {
      await api.postComment(issue.jiraKey, newComment);
      setNewComment('');
      onRefresh();
      push({ kind: 'success', title: 'Comment added successfully' });
    } catch (e: any) {
      push({ kind: 'error', title: 'Failed to post comment', message: e.message });
    } finally {
      setPostingComment(false);
    }
  };

  const handleAppendLogs = async () => {
    if (!updateLogs.trim()) return;
    try {
      await api.createOrUpdateIssue({
        key: issue.jiraKey,
        logs: (issue.logs || '') + '\n' + updateLogs,
        apiDetails: issue.apiDetails || 'POST /api/circuit/provision',
        requestPayload:
          issue.requestPayload || '{"circuitId": "TEST-1001", "nfid": "TEST-NFID-1001"}',
      });
      setUpdateLogs('');
      setShowLogUpdateBox(false);
      onRefresh();
      push({ kind: 'success', title: 'Diagnostic payload updated & re-validated' });
    } catch (e: any) {
      push({ kind: 'error', title: 'Update failed', message: e.message });
    }
  };

  const copyKey = () => {
    navigator.clipboard.writeText(issue.jiraKey);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Top Header & Actions Bar */}
      <Card className="p-4 sm:p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={onBack}
              aria-label="Back to overview"
              className="mt-0.5"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-sm font-bold text-accent">{issue.jiraKey}</span>
                <button
                  type="button"
                  onClick={copyKey}
                  className="text-muted hover:text-ink transition-colors"
                  aria-label="Copy key"
                >
                  {copiedKey ? (
                    <Check className="h-3.5 w-3.5 text-teal" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                </button>
                <StatusBadge tone={issueTone(issue.status)}>
                  {labelStatus(issue.status)}
                </StatusBadge>
                {issue.investigationStatus && (
                  <StatusBadge tone={issueTone(issue.investigationStatus)}>
                    {labelStatus(issue.investigationStatus)}
                  </StatusBadge>
                )}
              </div>
              <h1 className="mt-1 text-base font-semibold text-ink sm:text-lg">
                {issue.summary}
              </h1>
              <div className="mt-1 flex flex-wrap gap-x-4 text-xs text-muted">
                <span>Reporter: <strong className="text-ink font-normal">{issue.reporter || 'Unknown'}</strong></span>
                <span>Environment: <strong className="text-ink font-normal">{issue.environment || 'Production'}</strong></span>
                <span>Updated: <strong className="text-ink font-normal">{formatDateTime(issue.updatedAt)}</strong></span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={triggerRevalidate}
              disabled={revalidating}
            >
              <RotateCw className={`h-3.5 w-3.5 ${revalidating ? 'animate-spin text-accent' : ''}`} />
              Re-run Validation
            </Button>

            <Button
              variant="primary"
              size="sm"
              onClick={triggerInvestigate}
              disabled={investigating}
            >
              <Zap className={`h-3.5 w-3.5 ${investigating ? 'animate-bounce' : ''}`} />
              {investigating ? 'Investigating...' : 'Start Investigation'}
            </Button>

            {rca?.jiraInvestigationComment && (
              <Button
                variant="secondary"
                size="sm"
                onClick={handlePostInvestigationToJira}
                disabled={postingComment}
              >
                <Send className="h-3.5 w-3.5 text-accent" />
                Post to Jira
              </Button>
            )}

            {onExploreApiFlow && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onExploreApiFlow(issue.jiraKey)}
                className="border-indigo-500/30 text-accent hover:border-accent hover:bg-accent-soft"
              >
                <Network className="h-3.5 w-3.5 text-accent" />
                API Flow Map
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Loading Progress Panel when revalidating or investigating */}
      {(revalidating || investigating) && (
        <AnalysisProgress
          active={true}
          label={investigating ? 'Analyzing Incident & Determining Root Cause' : 'Validating Diagnostic Information'}
          message={investigating ? LOADING_MESSAGES[2] : LOADING_MESSAGES[1]}
          stages={ANALYSIS_STAGES}
        />
      )}

      {/* Ticket Diagnostic Readiness Banner */}
      <Card className="p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-4">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-sm font-semibold text-ink">Diagnostic Information Readiness</h2>
              <ReadinessIndicator score={issue.readinessScore} />
            </div>
            <p className="mt-1 text-xs text-muted">
              {issue.validation?.reason || 'Evaluation complete. All necessary diagnostic fields scored.'}
            </p>
          </div>

          {isWaiting && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowLogUpdateBox(!showLogUpdateBox)}
              className="border-amber/30 bg-amber-soft text-amber hover:bg-amber-soft/80"
            >
              <Sparkles className="h-3.5 w-3.5" />
              {showLogUpdateBox ? 'Hide Diagnostic Input' : 'Add Missing Diagnostics to Resume'}
            </Button>
          )}
        </div>

        {/* Diagnostic Checklist Pills */}
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-6 pt-2">
          {[
            { key: 'description', label: 'Description' },
            { key: 'apiDetails', label: 'API Endpoint' },
            { key: 'logs', label: 'Server Logs' },
            { key: 'requestPayload', label: 'Payload (JSON)' },
            { key: 'environment', label: 'Environment' },
            { key: 'errorMessage', label: 'Error Pattern' },
          ].map((item) => {
            const available =
              issue.validation?.availableInformation?.includes(item.key) ||
              (issue as any)[item.key];
            return (
              <div
                key={item.key}
                className={`flex items-center justify-between rounded-lg border p-2.5 text-xs transition-colors ${
                  available
                    ? 'border-teal/20 bg-teal-soft text-teal'
                    : 'border-danger/20 bg-danger-soft text-danger'
                }`}
              >
                <span>{item.label}</span>
                {available ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-teal shrink-0" />
                ) : (
                  <AlertTriangle className="h-3.5 w-3.5 text-danger shrink-0" />
                )}
              </div>
            );
          })}
        </div>

        {/* Interactive Update Box (simulate reporter response) */}
        {showLogUpdateBox && (
          <div className="mt-4 rounded-xl border border-amber/30 bg-amber-soft/20 p-4 space-y-3 animate-fade-in">
            <div className="text-xs font-semibold text-amber">
              Provide Diagnostic Artifacts (Simulate Reporter Response):
            </div>
            <textarea
              value={updateLogs}
              onChange={(e) => setUpdateLogs(e.target.value)}
              placeholder="Paste error logs or diagnostic traces (e.g. 2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001)..."
              rows={3}
              className="w-full rounded-lg border border-line bg-canvas p-3 font-mono text-xs text-ink placeholder:text-muted focus:border-accent focus:outline-none"
            />
            <div className="flex flex-wrap justify-end gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() =>
                  setUpdateLogs(
                    '2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001\n2026-10-08 10:31:43 ERROR [WFM] Downstream request failed status=500 endpoint=/api/circuit/provision correlationId=CORR-1001'
                  )
                }
              >
                Fill Sample Diagnostic Logs
              </Button>
              <Button variant="primary" size="sm" onClick={handleAppendLogs}>
                Submit & Trigger Autonomous Re-Triage
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Log Intelligence & Attachment Investigation Center */}
      <LogInvestigationCard
        issueKey={issue.jiraKey}
        attachments={issue.attachments}
        onRefresh={onRefresh}
        onExploreApiFlow={onExploreApiFlow}
      />

      {/* AI Code Investigation Center (Source-Code & Execution Path Tracing) */}
      <CodeInvestigationCard
        issueKey={issue.jiraKey}
        initialReport={issue.investigation?.codeInvestigation}
        onExploreApiFlow={onExploreApiFlow}
        onRefreshParent={onRefresh}
      />

      {/* Main Diagnostic Analysis Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left 2 Cols: RCA, Evidence, Dependency Graph, Reproduction, Test Cases */}
        <div className="space-y-6 lg:col-span-2">
          {/* RCA Card */}
          <Card className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-accent" />
                <h3 className="text-sm font-semibold text-ink">
                  Probable Root Cause & RCA Diagnosis
                </h3>
              </div>
              {rca?.rootCauseConfidence && (
                <div className="flex items-center gap-1.5 rounded-full border border-teal/20 bg-teal-soft px-2.5 py-1 text-xs font-bold font-mono text-teal">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  <span>
                    {rca.rootCauseConfidence}% Confidence ({rca.confidenceLevel})
                  </span>
                </div>
              )}
            </div>

            <div className="mb-4 rounded-xl border border-line bg-surface-2 p-4">
              <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-accent">
                Identified Root Cause
              </div>
              <p className="text-sm font-medium leading-relaxed text-ink">
                {rca?.probableRootCause ||
                  issue.probableRootCause ||
                  'Awaiting investigation trigger.'}
              </p>
            </div>

            {/* Supporting Evidence */}
            {rca?.supportingEvidence && rca.supportingEvidence.length > 0 && (
              <div className="mb-4 space-y-2">
                <div className="text-xs font-bold uppercase tracking-wider text-muted">
                  Diagnostic Evidence Base
                </div>
                <ul className="space-y-1.5">
                  {rca.supportingEvidence.map((ev, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-ink">
                      <span className="font-bold text-accent">•</span>
                      <span>{ev}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommended Fix */}
            {rca?.recommendedFix && (
              <div className="mb-4 rounded-lg border border-teal/20 bg-teal-soft/30 p-3.5 text-xs text-ink">
                <span className="mb-0.5 block font-bold text-teal">
                  Recommended Remediation & Fix:
                </span>
                {rca.recommendedFix}
              </div>
            )}

            {/* Developer Investigation Steps */}
            {rca?.recommendedInvestigationSteps &&
              rca.recommendedInvestigationSteps.length > 0 && (
                <div className="space-y-1.5">
                  <div className="text-xs font-bold uppercase tracking-wider text-muted">
                    Developer Action Items
                  </div>
                  {rca.recommendedInvestigationSteps.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs text-ink">
                      <span className="font-mono text-accent">{idx + 1}.</span>
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              )}
          </Card>

          {/* Service Dependency Graph */}
          <ServiceGraph
            nodes={rca?.serviceGraphNodes}
            edges={rca?.serviceGraphEdges}
          />

          {/* Reproduction cURL & Postman */}
          <CurlViewer
            curlCommand={issue.investigation?.reproductionCurl}
            postmanJson={issue.investigation?.postmanJson}
          />

          {/* Generated Test Cases */}
          <TestCaseList testCases={issue.investigation?.generatedTestCases} />
        </div>

        {/* Right 1 Col: Execution Timeline, Similar Incidents, Jira Comments */}
        <div className="space-y-6">
          {/* AI Timeline */}
          <TimelineViewer events={rca?.incidentTimeline} />

          {/* Similar Incidents */}
          <Card className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <Activity className="h-4 w-4 text-accent" />
              <h3 className="text-sm font-semibold text-ink">Similar Historical Incidents</h3>
            </div>

            <div className="space-y-3">
              {(
                issue.investigation?.similarIncidents || [
                  {
                    jiraKey: 'HACK-102',
                    summary: 'PEDS circuit provisioning failure due to duplicate NFID',
                    similarityScore: 91,
                    rootCause: 'Duplicate NFID from upstream NTLS',
                    resolution: 'Added NFID idempotency cache layer',
                    explanation: 'Matching duplicate NFID constraint pattern in PEDS.',
                  },
                ]
              ).map((sim, i) => (
                <div
                  key={i}
                  className="rounded-lg border border-line bg-surface-2 p-3.5 transition hover:border-accent/30"
                >
                  <div className="mb-1 flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-accent">{sim.jiraKey}</span>
                    <span className="rounded border border-accent/20 bg-accent-soft px-2 py-0.5 font-mono text-[10px] font-bold text-accent">
                      {sim.similarityScore}% Match
                    </span>
                  </div>
                  <div className="truncate text-xs font-semibold text-ink">{sim.summary}</div>
                  <p className="mt-1 text-[11px] text-muted">
                    <span className="font-medium text-muted">Prev Root Cause:</span> {sim.rootCause}
                  </p>
                  <p className="mt-0.5 text-[11px] text-teal">
                    <span className="font-medium text-muted">Prev Fix:</span> {sim.resolution}
                  </p>
                </div>
              ))}
            </div>
          </Card>

          {/* Jira Comments & Activity Stream */}
          <Card className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-accent" />
              <h3 className="text-sm font-semibold text-ink">Jira Issue Activity Stream</h3>
            </div>

            {rca?.jiraInvestigationComment && (
              <div className="mb-4 max-h-48 overflow-y-auto whitespace-pre-wrap rounded-lg border border-line bg-canvas p-3 font-mono text-xs text-ink">
                {rca.jiraInvestigationComment}
              </div>
            )}

            <form onSubmit={handlePostCustomComment} className="space-y-2">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add Jira comment..."
                rows={2}
                className="w-full rounded-lg border border-line bg-canvas p-2.5 text-xs text-ink placeholder:text-muted focus:border-accent focus:outline-none"
              />
              <div className="flex justify-end">
                <Button
                  type="submit"
                  size="sm"
                  variant="primary"
                  disabled={postingComment}
                >
                  <Send className="h-3 w-3" />
                  Post Comment
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};
export default TicketDetailPage;
