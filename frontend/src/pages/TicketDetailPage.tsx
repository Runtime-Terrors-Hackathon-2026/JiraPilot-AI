import React, { useState } from 'react';
import { JiraIssue } from '../types';
import { api } from '../api/client';
import { ServiceGraph } from '../components/ServiceGraph';
import { TimelineViewer } from '../components/TimelineViewer';
import { TestCaseList } from '../components/TestCaseList';
import { CurlViewer } from '../components/CurlViewer';
import { LogInvestigationCard } from '../components/LogInvestigationCard';
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCw,
  Send,
  MessageSquare,
  ShieldCheck,
  Zap,
  Activity,
  Sparkles,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  FileText,
  Mail,
  Copy,
  Check
} from 'lucide-react';

interface TicketDetailPageProps {
  issue: JiraIssue;
  onBack: () => void;
  onRefresh: () => void;
}

export const TicketDetailPage: React.FC<TicketDetailPageProps> = ({ issue, onBack, onRefresh }) => {
  const [revalidating, setRevalidating] = useState(false);
  const [investigating, setInvestigating] = useState(false);
  const [postingComment, setPostingComment] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [updateLogs, setUpdateLogs] = useState('');
  const [showLogUpdateBox, setShowLogUpdateBox] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

  const rca = issue.investigation?.rca;
  const isReady = issue.status === 'READY';
  const isInvestigated = issue.status === 'INVESTIGATED' || issue.investigationStatus === 'COMPLETED';
  const isWaiting = issue.status === 'WAITING_FOR_INFORMATION';

  const triggerRevalidate = async () => {
    setRevalidating(true);
    try {
      await api.revalidateIssue(issue.jiraKey);
      onRefresh();
      showSuccess('Diagnostic validation re-run completed.');
    } catch (e) {
      console.error(e);
    } finally {
      setRevalidating(false);
    }
  };

  const triggerInvestigate = async () => {
    setInvestigating(true);
    try {
      await api.investigateIssue(issue.jiraKey);
      onRefresh();
      showSuccess('Root Cause Analysis & Test Suite generation completed.');
    } catch (e) {
      console.error(e);
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
      showSuccess('Investigation report posted to Jira issue.');
    } catch (e) {
      console.error(e);
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
      showSuccess('Comment added successfully.');
    } catch (e) {
      console.error(e);
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
        requestPayload: issue.requestPayload || '{"circuitId": "TEST-1001", "nfid": "TEST-NFID-1001"}',
      });
      setUpdateLogs('');
      setShowLogUpdateBox(false);
      onRefresh();
      showSuccess('Diagnostic payload updated & re-validated.');
    } catch (e) {
      console.error(e);
    }
  };

  const showSuccess = (msg: string) => {
    setActionSuccessMsg(msg);
    setTimeout(() => setActionSuccessMsg(null), 3000);
  };

  const copyKey = () => {
    navigator.clipboard.writeText(issue.jiraKey);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  return (
    <div className="space-y-6 pb-16 animate-in fade-in">
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-900 border border-slate-800 p-4 rounded-xl">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-teal-400 text-sm">{issue.jiraKey}</span>
              <button onClick={copyKey} className="text-slate-500 hover:text-slate-300">
                {copiedKey ? <Check className="w-3.5 h-3.5 text-teal-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                isInvestigated ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
                isReady ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                isWaiting ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                'bg-blue-500/10 text-blue-400 border border-blue-500/20'
              }`}>
                {issue.status.replace(/_/g, ' ')}
              </span>
            </div>
            <h1 className="text-base font-bold text-white mt-0.5">{issue.summary}</h1>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={triggerRevalidate}
            disabled={revalidating}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition active:scale-95 disabled:opacity-50"
          >
            <RotateCw className={`w-3.5 h-3.5 ${revalidating ? 'animate-spin text-teal-400' : ''}`} />
            <span>Re-run Validation</span>
          </button>

          <button
            onClick={triggerInvestigate}
            disabled={investigating}
            className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 hover:bg-teal-500 text-white shadow-md shadow-teal-600/30 transition active:scale-95 disabled:opacity-50"
          >
            <Zap className={`w-3.5 h-3.5 ${investigating ? 'animate-bounce' : ''}`} />
            <span>{investigating ? 'Investigating...' : 'Start Investigation'}</span>
          </button>

          {rca?.jiraInvestigationComment && (
            <button
              onClick={handlePostInvestigationToJira}
              disabled={postingComment}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition active:scale-95 disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Post to Jira</span>
            </button>
          )}
        </div>
      </div>

      {actionSuccessMsg && (
        <div className="p-3 bg-emerald-950/50 border border-emerald-500/50 text-emerald-300 text-xs rounded-xl flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{actionSuccessMsg}</span>
        </div>
      )}

      {/* Ticket Diagnostic Readiness Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-white">Diagnostic Information Readiness</h2>
              <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                (issue.readinessScore || 0) >= 80 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                (issue.readinessScore || 0) >= 60 ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                'bg-rose-500/10 text-rose-400 border border-rose-500/20'
              }`}>
                Score: {issue.readinessScore || 0}/100
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              {issue.validation?.reason || 'Evaluation complete.'}
            </p>
          </div>

          {isWaiting && (
            <button
              onClick={() => setShowLogUpdateBox(!showLogUpdateBox)}
              className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 transition"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{showLogUpdateBox ? 'Hide Diagnostic Input' : 'Add Missing Diagnostics to Resume'}</span>
            </button>
          )}
        </div>

        {/* Diagnostic Checklist Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2 pt-2">
          {[
            { key: 'description', label: 'Description' },
            { key: 'apiDetails', label: 'API Endpoint' },
            { key: 'logs', label: 'Server Logs' },
            { key: 'requestPayload', label: 'Payload (JSON)' },
            { key: 'environment', label: 'Environment' },
            { key: 'errorMessage', label: 'Error Pattern' },
          ].map((item) => {
            const available = issue.validation?.availableInformation?.includes(item.key) || (issue as any)[item.key];
            return (
              <div
                key={item.key}
                className={`p-2.5 rounded-lg border text-xs flex items-center justify-between ${
                  available
                    ? 'bg-slate-950 border-emerald-500/30 text-emerald-300'
                    : 'bg-slate-950 border-rose-500/30 text-rose-300'
                }`}
              >
                <span>{item.label}</span>
                {available ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                )}
              </div>
            );
          })}
        </div>

        {/* Interactive Update Box (for demonstrating live transition from Incomplete to Ready) */}
        {showLogUpdateBox && (
          <div className="mt-4 p-4 rounded-xl bg-slate-950 border border-amber-500/40 space-y-3 animate-in fade-in">
            <div className="text-xs font-semibold text-amber-300">
              Provide Diagnostic Artifacts (Simulate Reporter Response):
            </div>
            <textarea
              value={updateLogs}
              onChange={(e) => setUpdateLogs(e.target.value)}
              placeholder="Paste error logs or diagnostic traces (e.g. 2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001)..."
              rows={3}
              className="w-full p-3 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white font-mono focus:outline-none focus:border-teal-500"
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() =>
                  setUpdateLogs(
                    '2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001\n2026-10-08 10:31:43 ERROR [WFM] Downstream request failed status=500 endpoint=/api/circuit/provision correlationId=CORR-1001'
                  )
                }
                className="px-2.5 py-1 text-xs text-slate-400 hover:text-white"
              >
                Fill Sample Diagnostic Logs
              </button>
              <button
                onClick={handleAppendLogs}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 hover:bg-teal-500 text-white"
              >
                Submit & Trigger Autonomous Re-Triage
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Log Intelligence & Attachment Investigation Center */}
      <LogInvestigationCard
        issueKey={issue.jiraKey}
        attachments={issue.attachments}
        onRefresh={onRefresh}
      />

      {/* Main Diagnostic Analysis Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: RCA, Evidence, Dependency Graph, Reproduction, Test Cases */}
        <div className="lg:col-span-2 space-y-6">
          {/* RCA Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-teal-400" />
                <h3 className="text-sm font-semibold text-white">Probable Root Cause & RCA Diagnosis</h3>
              </div>
              {rca?.rootCauseConfidence && (
                <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold font-mono">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>{rca.rootCauseConfidence}% Confidence ({rca.confidenceLevel})</span>
                </div>
              )}
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 mb-4">
              <div className="text-xs font-semibold text-teal-400 uppercase tracking-wider mb-1">Identified Root Cause</div>
              <p className="text-sm font-medium text-white leading-relaxed">
                {rca?.probableRootCause || issue.probableRootCause || 'Awaiting investigation trigger.'}
              </p>
            </div>

            {/* Supporting Evidence */}
            {rca?.supportingEvidence && rca.supportingEvidence.length > 0 && (
              <div className="space-y-2 mb-4">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Diagnostic Evidence Base</div>
                <ul className="space-y-1.5">
                  {rca.supportingEvidence.map((ev, i) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start space-x-2">
                      <span className="text-teal-400 font-bold">•</span>
                      <span>{ev}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommended Fix */}
            {rca?.recommendedFix && (
              <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 text-xs text-emerald-200 mb-4">
                <span className="font-bold text-emerald-400 block mb-0.5">Recommended Remediation & Fix:</span>
                {rca.recommendedFix}
              </div>
            )}

            {/* Developer Investigation Steps */}
            {rca?.recommendedInvestigationSteps && rca.recommendedInvestigationSteps.length > 0 && (
              <div className="space-y-1.5">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Developer Action Items</div>
                {rca.recommendedInvestigationSteps.map((step, idx) => (
                  <div key={idx} className="text-xs text-slate-300 flex items-start space-x-2">
                    <span className="font-mono text-teal-400">{idx + 1}.</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

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

        {/* Right 1 Col: Execution Timeline, Similar Incidents, Jira Comments, Email History */}
        <div className="space-y-6">
          {/* AI Timeline */}
          <TimelineViewer events={rca?.incidentTimeline} />

          {/* Similar Incidents */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Activity className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-semibold text-white">Similar Historical Incidents</h3>
            </div>

            <div className="space-y-3">
              {(issue.investigation?.similarIncidents || [
                {
                  jiraKey: 'HACK-102',
                  summary: 'PEDS circuit provisioning failure due to duplicate NFID',
                  similarityScore: 91,
                  rootCause: 'Duplicate NFID from upstream NTLS',
                  resolution: 'Added NFID idempotency cache layer',
                  explanation: 'Matching duplicate NFID constraint pattern in PEDS.',
                },
              ]).map((sim, i) => (
                <div key={i} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-teal-400 text-xs">{sim.jiraKey}</span>
                    <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                      {sim.similarityScore}% Match
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-slate-200 truncate">{sim.summary}</div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    <span className="text-slate-500 font-medium">Prev Root Cause:</span> {sim.rootCause}
                  </p>
                  <p className="text-[11px] text-emerald-400 mt-0.5">
                    <span className="text-slate-500 font-medium">Prev Fix:</span> {sim.resolution}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Jira Comments & Activity Log */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center space-x-2 mb-4">
              <MessageSquare className="w-4 h-4 text-teal-400" />
              <h3 className="text-sm font-semibold text-white">Jira Issue Activity Stream</h3>
            </div>

            {rca?.jiraInvestigationComment && (
              <div className="mb-4 p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
                {rca.jiraInvestigationComment}
              </div>
            )}

            <form onSubmit={handlePostCustomComment} className="space-y-2">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add Jira comment..."
                rows={2}
                className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={postingComment}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition flex items-center space-x-1.5"
                >
                  <Send className="w-3 h-3" />
                  <span>Post Comment</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
