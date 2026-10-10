import React, { useState, useEffect } from 'react';
import {
  Code2,
  GitBranch,
  FileCode,
  CheckCircle2,
  AlertTriangle,
  Play,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  Shield,
  RotateCw,
  Terminal,
  FileText,
  Download,
  Flame,
  ArrowRight,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import {
  CodeInvestigationReport,
  ExecutionPathStep,
  FailureLocation,
  CodeDiff,
  TestRecommendation,
} from '../types';
import { api } from '../api/client';
import { Card, Button, StatusBadge, CloneCommand } from './ui/primitives';
import { useToast } from './ui/Toast';

interface Props {
  issueKey: string;
  initialReport?: CodeInvestigationReport;
  onExploreApiFlow?: (key: string) => void;
  onRefreshParent?: () => void;
}

const STAGE_STEPS = [
  { id: 'WAITING_FOR_REPOSITORY', label: 'Waiting for Repo' },
  { id: 'REPOSITORY_INDEXING', label: 'Repo Indexing' },
  { id: 'SEARCHING_SOURCE_CODE', label: 'Searching Code' },
  { id: 'TRACING_EXECUTION_PATH', label: 'Tracing Execution' },
  { id: 'GENERATING_DIAGNOSIS', label: 'Generating Diagnosis' },
  { id: 'READY_FOR_REVIEW', label: 'Ready for Review' },
];

export const CodeInvestigationCard: React.FC<Props> = ({
  issueKey,
  initialReport,
  onExploreApiFlow,
  onRefreshParent,
}) => {
  const { push } = useToast();
  const [report, setReport] = useState<CodeInvestigationReport | null>(initialReport || null);
  const [loading, setLoading] = useState(false);
  const [generatingDiff, setGeneratingDiff] = useState(false);
  const [runningTests, setRunningTests] = useState(false);
  const [testOutput, setTestOutput] = useState<any | null>(null);
  const [expandedStep, setExpandedStep] = useState<number | null>(1);
  const [copiedPatch, setCopiedPatch] = useState(false);
  const [activeTab, setActiveTab] = useState<'flow' | 'locations' | 'diff' | 'tests' | 'evidence'>('flow');

  useEffect(() => {
    if (initialReport) {
      setReport(initialReport);
    } else {
      fetchCodeInvestigation();
    }
  }, [issueKey, initialReport]);

  const fetchCodeInvestigation = async () => {
    setLoading(true);
    try {
      const data = await api.getCodeInvestigation(issueKey);
      setReport(data);
    } catch (err: any) {
      console.warn('Code investigation fetch deferred:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRerun = async () => {
    setLoading(true);
    try {
      push({ kind: 'info', title: 'Running deterministic source-code investigation...' });
      const data = await api.runCodeInvestigation(issueKey);
      setReport(data);
      push({ kind: 'success', title: 'Code investigation completed', message: 'Traced execution path and isolated defect.' });
      if (onRefreshParent) onRefreshParent();
    } catch (err: any) {
      push({ kind: 'error', title: 'Code investigation failed', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDiff = async () => {
    if (!report) return;
    setGeneratingDiff(true);
    try {
      const rootLoc = report.failureLocations?.find((fl) => fl.category === 'ROOT_CAUSE');
      const diff = await api.generateDiff(issueKey, {
        investigationId: report.investigationId,
        repositoryId: report.repositoryId,
        filePath: rootLoc?.filePath || 'src/main/java/com/northstar/inventory/service/ResourceAllocationService.java',
        targetMethod: rootLoc?.methodName || 'reserveCircuit',
      });
      setReport({ ...report, codeDiff: diff });
      setActiveTab('diff');
      push({ kind: 'success', title: 'Suggested fix patch generated', message: 'Inspect side-by-side unified diff.' });
    } catch (err: any) {
      push({ kind: 'error', title: 'Diff generation failed', message: err.message });
    } finally {
      setGeneratingDiff(false);
    }
  };

  const handleRunTests = async (testRec?: TestRecommendation) => {
    if (!report) return;
    setRunningTests(true);
    setTestOutput(null);
    try {
      const cmd = testRec?.runCommand || 'mvn test -Dtest=ResourceAllocationServiceTest';
      const tc = testRec?.testClass || 'ResourceAllocationServiceTest';
      push({ kind: 'info', title: `Running isolated test suite: ${tc}...` });
      const res = await api.runRecommendedTests(issueKey, cmd, tc);
      setTestOutput(res);
      setActiveTab('tests');
      push({
        kind: res.passed ? 'success' : 'error',
        title: res.passed ? 'All recommended tests passed' : 'Test suite failed',
        message: `Command: ${cmd} (Duration: ${res.durationMs}ms)`,
      });
    } catch (err: any) {
      push({ kind: 'error', title: 'Test execution failed', message: err.message });
    } finally {
      setRunningTests(false);
    }
  };

  const copyPatch = () => {
    if (!report?.codeDiff?.unifiedDiff) return;
    navigator.clipboard.writeText(report.codeDiff.unifiedDiff);
    setCopiedPatch(true);
    push({ kind: 'success', title: 'Patch copied to clipboard', message: 'Ready to apply via `git apply`.' });
    setTimeout(() => setCopiedPatch(false), 2000);
  };

  const downloadPatch = () => {
    if (!report?.codeDiff?.unifiedDiff) return;
    const blob = new Blob([report.codeDiff.unifiedDiff], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `fix-${issueKey.toLowerCase()}.patch`;
    link.click();
    URL.revokeObjectURL(url);
    push({ kind: 'success', title: 'Patch file downloaded', message: `Saved fix-${issueKey.toLowerCase()}.patch` });
  };

  if (!report && !loading) {
    return (
      <Card className="p-6 border-indigo-500/20 bg-surface">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-accent-soft text-accent">
              <Code2 className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-ink">AI Code Investigation</h3>
              <p className="text-xs text-muted">
                Continue from log analysis into actual source code, trace execution paths, and generate suggested fixes.
              </p>
            </div>
          </div>
          <Button variant="primary" size="sm" onClick={handleRerun} disabled={loading}>
            <Sparkles className="h-3.5 w-3.5" />
            Launch Code Investigation
          </Button>
        </div>
      </Card>
    );
  }

  const currentStatusIndex = STAGE_STEPS.findIndex((s) => s.id === (report?.status || 'READY_FOR_REVIEW'));
  const effectiveIndex = currentStatusIndex >= 0 ? currentStatusIndex : STAGE_STEPS.length - 1;

  return (
    <Card className="overflow-hidden border-indigo-500/30 bg-surface shadow-xl">
      {/* 1. Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-5 py-4 bg-surface-2/60">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-accent-soft text-accent border border-accent/20">
            <Code2 className="h-5 w-5 text-accent animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-ink tracking-tight">AI Code Investigation</h3>
              <StatusBadge tone="accent">
                {report?.status === 'READY_FOR_REVIEW' ? 'Ready for Review' : report?.status || 'Analyzing'}
              </StatusBadge>
              {report?.revision && (
                <span className="font-mono text-[11px] text-muted rounded bg-canvas px-1.5 py-0.5 border border-line">
                  rev:{report.revision.substring(0, 7)}
                </span>
              )}
              <span className="text-[11px] font-semibold text-teal flex items-center gap-1 rounded bg-teal-soft px-2 py-0.5 border border-teal/20">
                <Shield className="h-3 w-3" />
                {report?.accessPermission || 'READ_ONLY'}
              </span>
            </div>
            <p className="text-xs text-muted mt-0.5">
              Service: <strong className="text-ink font-semibold">{report?.serviceName}</strong> · Repo:{' '}
              <span className="font-mono text-accent">{report?.repositoryName}</span>
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {onExploreApiFlow && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onExploreApiFlow(issueKey)}
              className="text-xs border-indigo-500/30 text-accent hover:bg-accent-soft"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              API Flow Map
            </Button>
          )}

          <Button
            variant="secondary"
            size="sm"
            onClick={handleRerun}
            disabled={loading}
            className="text-xs"
          >
            <RotateCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-accent' : ''}`} />
            {loading ? 'Inspecting...' : 'Rerun Code Analysis'}
          </Button>

          {!report?.codeDiff && (
            <Button
              variant="primary"
              size="sm"
              onClick={handleGenerateDiff}
              disabled={generatingDiff}
              className="text-xs"
            >
              <Sparkles className="h-3.5 w-3.5" />
              {generatingDiff ? 'Generating...' : 'Generate Fix'}
            </Button>
          )}
        </div>
      </div>

      {/* 2. Investigation Lifecycle Stepper */}
      <div className="border-b border-line/60 bg-canvas/60 px-5 py-3 overflow-x-auto">
        <div className="flex items-center justify-between min-w-[620px] gap-2">
          {STAGE_STEPS.map((step, idx) => {
            const isDone = idx <= effectiveIndex;
            const isCurrent = idx === effectiveIndex;
            return (
              <div key={step.id} className="flex items-center gap-2 flex-1">
                <div
                  className={`flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold transition-all ${
                    isDone
                      ? 'bg-accent text-white shadow-sm'
                      : 'border border-line bg-surface text-muted'
                  } ${isCurrent ? 'ring-2 ring-accent ring-offset-1 ring-offset-canvas' : ''}`}
                >
                  {isDone ? <Check className="h-3 w-3" /> : idx + 1}
                </div>
                <span
                  className={`text-xs whitespace-nowrap ${
                    isCurrent ? 'font-semibold text-accent' : isDone ? 'text-ink font-medium' : 'text-muted'
                  }`}
                >
                  {step.label}
                </span>
                {idx < STAGE_STEPS.length - 1 && (
                  <div className={`h-0.5 flex-1 mx-1 ${idx < effectiveIndex ? 'bg-accent' : 'bg-line'}`} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="p-5 space-y-6">
        {/* 3. Executive Summary & Code Location Banner */}
        <div className="rounded-xl border border-indigo-500/20 bg-gradient-to-r from-accent-soft/20 via-surface-2 to-surface p-4">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="space-y-2 max-w-3xl">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-accent flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-accent" />
                  Executive Code Diagnosis
                </span>
                <span className="font-mono text-xs font-bold text-teal bg-teal-soft border border-teal/20 px-2 py-0.5 rounded-full">
                  {report?.confidenceScore || 94}% Confidence
                </span>
              </div>
              <p className="text-sm font-medium text-ink leading-relaxed">
                {report?.executiveSummary || 'Analyzing codebase to identify verified execution path and root cause.'}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
                <div className="rounded-lg border border-line bg-surface p-2.5">
                  <span className="font-semibold text-muted block mb-1">Observed Symptoms:</span>
                  <ul className="space-y-1 text-ink">
                    {(report?.observedSymptoms || []).map((s, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-danger font-bold">•</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="rounded-lg border border-line bg-surface p-2.5">
                  <span className="font-semibold text-muted block mb-1">Confirmed Source Facts:</span>
                  <ul className="space-y-1 text-ink">
                    {(report?.confirmedFacts || []).map((f, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-teal font-bold">•</span>
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Approved Repository Box */}
            <div className="rounded-xl border border-line bg-surface p-3.5 text-xs space-y-2 min-w-[260px] shrink-0">
              <div className="flex items-center justify-between text-muted">
                <span className="font-semibold uppercase tracking-wider text-[10px]">Configured Repository</span>
                <GitBranch className="h-3.5 w-3.5 text-accent" />
              </div>
              <div className="font-semibold text-ink text-sm">{report?.repositoryName}</div>
              <div className="text-[11px] text-muted font-mono truncate">{report?.repositoryUrl}</div>
              <CloneCommand
                command={`git clone ${report?.repositoryUrl || ''}`}
                onCopied={() => push({ kind: 'success', title: 'Git clone command copied' })}
              />
            </div>
          </div>
        </div>

        {/* 4. Tab Navigation for Details */}
        <div className="flex items-center gap-2 border-b border-line pb-2">
          {[
            { id: 'flow', label: 'Suspected Execution Path', count: report?.executionPath?.length },
            { id: 'locations', label: 'Failure Locations', count: report?.failureLocations?.length },
            { id: 'diff', label: 'Suggested Fix (Code Diff)', badge: report?.codeDiff ? 'Ready' : undefined },
            { id: 'tests', label: 'Recommended Tests', count: report?.testRecommendations?.length },
            { id: 'evidence', label: 'Inspected Files & Evidence', count: report?.filesInspected?.length },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-accent text-white shadow-sm'
                  : 'text-muted hover:bg-surface-2 hover:text-ink'
              }`}
            >
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span
                  className={`rounded-full px-1.5 py-0.2 text-[10px] font-mono ${
                    activeTab === tab.id ? 'bg-white/20 text-white' : 'bg-surface-2 text-muted'
                  }`}
                >
                  {tab.count}
                </span>
              )}
              {tab.badge && (
                <span className="rounded-full bg-teal/20 text-teal px-1.5 py-0.2 text-[10px] font-bold">
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Tab 1: Execution Path Stepper */}
        {activeTab === 'flow' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted">
                HTTP Request &rarr; Controller &rarr; Business Service &rarr; Persistence / Client &rarr; Exception Handler
              </span>
              <span className="text-xs text-muted font-mono">
                {report?.executionPath?.length || 0} Traced Hops
              </span>
            </div>

            <div className="space-y-2.5">
              {(report?.executionPath || []).map((step: ExecutionPathStep) => {
                const isExpanded = expandedStep === step.stepNumber;
                const isObserved = step.evidenceType === 'OBSERVED';
                return (
                  <div
                    key={step.stepNumber}
                    className={`rounded-xl border transition-all ${
                      isObserved
                        ? 'border-danger/30 bg-danger-soft/10'
                        : 'border-line bg-surface-2/60 hover:border-accent/30'
                    }`}
                  >
                    <div
                      className="flex items-center justify-between p-3.5 cursor-pointer"
                      onClick={() => setExpandedStep(isExpanded ? null : step.stepNumber)}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`flex h-7 w-7 items-center justify-center rounded-lg font-mono text-xs font-bold ${
                            isObserved ? 'bg-danger text-white' : 'bg-accent-soft text-accent'
                          }`}
                        >
                          {step.stepNumber}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-sm font-bold text-ink">
                              {step.className}.{step.methodName}
                            </span>
                            <span
                              className={`rounded text-[10px] font-bold px-2 py-0.5 uppercase ${
                                isObserved
                                  ? 'bg-danger-soft text-danger border border-danger/20'
                                  : 'bg-accent-soft text-accent border border-accent/20'
                              }`}
                            >
                              {step.evidenceType}
                            </span>
                          </div>
                          <div className="text-xs text-muted mt-0.5 flex items-center gap-2">
                            <span className="font-mono text-[11px] text-accent">{step.filePath}</span>
                            <span>•</span>
                            <span>Lines {step.startLine}–{step.endLine}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="text-xs text-muted hidden md:inline max-w-sm truncate text-right">
                          {step.reason}
                        </span>
                        {isExpanded ? (
                          <ChevronDown className="h-4 w-4 text-muted" />
                        ) : (
                          <ChevronRight className="h-4 w-4 text-muted" />
                        )}
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="border-t border-line/60 p-4 space-y-3 bg-canvas/40 animate-fade-in">
                        <div className="text-xs text-ink leading-relaxed">
                          <strong className="text-muted">Inclusion Rationale:</strong> {step.reason}
                        </div>
                        {step.evidenceReference && (
                          <div className="text-xs text-muted font-mono flex items-center gap-1.5">
                            <span className="font-semibold text-accent">Source Reference:</span>
                            <span>{step.evidenceReference}</span>
                          </div>
                        )}
                        {step.snippet && (
                          <div className="overflow-hidden rounded-lg border border-line bg-log p-3 font-mono text-xs text-log-ink">
                            <div className="text-[10px] text-muted border-b border-white/10 pb-1 mb-2 flex items-center justify-between">
                              <span>Source Snippet ({step.filePath})</span>
                              <span>Lines {step.startLine}–{step.endLine}</span>
                            </div>
                            <pre className="overflow-x-auto whitespace-pre-wrap">{step.snippet}</pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tab 2: Failure Locations (Observed vs Propagated vs Root Cause) */}
        {activeTab === 'locations' && (
          <div className="space-y-4">
            <p className="text-xs text-muted">
              Distinguishing where the error was observed, where it propagated, and where the defect actually resides.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {(report?.failureLocations || []).map((loc: FailureLocation, idx: number) => {
                const isObserved = loc.category === 'OBSERVED';
                const isPropagated = loc.category === 'PROPAGATED';
                const isRoot = loc.category === 'ROOT_CAUSE';

                return (
                  <div
                    key={idx}
                    className={`rounded-xl border p-4 flex flex-col justify-between ${
                      isRoot
                        ? 'border-accent bg-accent-soft/10 ring-1 ring-accent/30'
                        : isObserved
                        ? 'border-danger/30 bg-danger-soft/10'
                        : 'border-amber/30 bg-amber-soft/10'
                    }`}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span
                          className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                            isRoot
                              ? 'bg-accent text-white'
                              : isObserved
                              ? 'bg-danger text-white'
                              : 'bg-amber text-ink'
                          }`}
                        >
                          {loc.category}
                        </span>
                        <span className="font-mono text-xs text-muted">Line {loc.line}</span>
                      </div>
                      <h4 className="text-sm font-bold text-ink">{loc.title}</h4>
                      <p className="text-xs text-muted leading-relaxed">{loc.description}</p>
                      <div className="font-mono text-[11px] text-accent truncate">{loc.filePath}</div>
                    </div>

                    <div className="mt-3 pt-3 border-t border-line/60">
                      <div className="text-[11px] text-muted mb-1 font-semibold">Evidence Link:</div>
                      <p className="text-xs text-ink">{loc.evidenceReason}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tab 3: Code Diff & Suggested Patch */}
        {activeTab === 'diff' && (
          <div className="space-y-4">
            {report?.codeDiff ? (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-teal/20 bg-teal-soft/20 p-3.5">
                  <div>
                    <h4 className="text-xs font-bold text-teal uppercase tracking-wide">
                      Proposed Remediation Patch (Read-Only Preview)
                    </h4>
                    <p className="text-xs text-ink mt-0.5">{report.codeDiff.purpose}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="secondary" size="sm" onClick={copyPatch}>
                      {copiedPatch ? <Check className="h-3.5 w-3.5 text-teal" /> : <Copy className="h-3.5 w-3.5" />}
                      Copy Patch
                    </Button>
                    <Button variant="secondary" size="sm" onClick={downloadPatch}>
                      <Download className="h-3.5 w-3.5" />
                      Download .patch
                    </Button>
                  </div>
                </div>

                {/* Unified Diff Box */}
                <div className="overflow-hidden rounded-xl border border-line bg-log">
                  <div className="flex items-center justify-between border-b border-white/10 px-4 py-2.5 text-xs text-log-ink bg-black/40">
                    <span className="font-mono">{report.codeDiff.filePath}</span>
                    <span className="text-[11px] text-muted">Unified Git Diff</span>
                  </div>
                  <div className="p-4 font-mono text-xs overflow-x-auto max-h-96">
                    {report.codeDiff.unifiedDiff.split('\n').map((line, lIdx) => {
                      const isAdd = line.startsWith('+') && !line.startsWith('+++');
                      const isSub = line.startsWith('-') && !line.startsWith('---');
                      const isHeader = line.startsWith('@@') || line.startsWith('---') || line.startsWith('+++');

                      return (
                        <div
                          key={lIdx}
                          className={`py-0.5 px-2 ${
                            isAdd
                              ? 'bg-teal/20 text-teal-200'
                              : isSub
                              ? 'bg-danger/20 text-danger'
                              : isHeader
                              ? 'text-accent font-bold'
                              : 'text-log-ink'
                          }`}
                        >
                          {line}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Risks & Affected Files */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="rounded-lg border border-line bg-surface p-3 space-y-1.5">
                    <span className="font-semibold text-muted block uppercase tracking-wider text-[10px]">
                      Potential Risks & Side Effects
                    </span>
                    <ul className="space-y-1 text-ink">
                      {(report.codeDiff.affectedRisks || []).map((r, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <AlertTriangle className="h-3.5 w-3.5 text-amber shrink-0 mt-0.5" />
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="rounded-lg border border-line bg-surface p-3 space-y-1.5">
                    <span className="font-semibold text-muted block uppercase tracking-wider text-[10px]">
                      Affected Files
                    </span>
                    <ul className="space-y-1 font-mono text-accent">
                      {(report.codeDiff.affectedFiles || []).map((af, i) => (
                        <li key={i} className="flex items-center gap-1.5">
                          <FileCode className="h-3.5 w-3.5 text-muted" />
                          <span>{af}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              <div className="rounded-xl border border-dashed border-line p-8 text-center space-y-3">
                <FileCode className="h-8 w-8 text-muted mx-auto" />
                <p className="text-xs text-muted max-w-sm mx-auto">
                  Click below to generate a proposed code diff targeting the isolated root cause method.
                </p>
                <Button variant="primary" size="sm" onClick={handleGenerateDiff} disabled={generatingDiff}>
                  <Sparkles className="h-3.5 w-3.5" />
                  {generatingDiff ? 'Synthesizing Fix...' : 'Generate Suggested Code Patch'}
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Tab 4: Recommended Tests */}
        {activeTab === 'tests' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted">
                Unit and regression test recommendations based on inspected code structure.
              </span>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleRunTests(report?.testRecommendations?.[0])}
                disabled={runningTests}
                className="text-xs"
              >
                <Play className="h-3.5 w-3.5" />
                {runningTests ? 'Running Sandbox Tests...' : 'Run Recommended Tests'}
              </Button>
            </div>

            <div className="space-y-3">
              {(report?.testRecommendations || []).map((tr: TestRecommendation, idx: number) => (
                <div key={idx} className="rounded-xl border border-line bg-surface-2/60 p-4 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-accent-soft text-accent text-[10px] font-bold px-2 py-0.5">
                        {tr.testType}
                      </span>
                      <span className="font-mono text-sm font-bold text-ink">{tr.testClass}</span>
                      <span className="text-xs text-muted">#{tr.testMethod}</span>
                    </div>
                    {tr.isExistingTest ? (
                      <span className="text-[11px] font-semibold text-teal flex items-center gap-1">
                        <CheckCircle2 className="h-3.5 w-3.5" /> Existing Test
                      </span>
                    ) : (
                      <span className="text-[11px] font-semibold text-accent flex items-center gap-1">
                        <Sparkles className="h-3.5 w-3.5" /> Proposed Test
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-muted leading-relaxed">{tr.explanation}</p>

                  <div className="rounded-lg border border-line bg-canvas p-2.5 flex items-center justify-between gap-2 font-mono text-xs">
                    <span className="text-ink truncate">{tr.runCommand}</span>
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard.writeText(tr.runCommand);
                        push({ kind: 'success', title: 'Command copied' });
                      }}
                      className="text-muted hover:text-ink shrink-0"
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  {tr.codeSnippet && (
                    <div className="overflow-hidden rounded-lg bg-log p-3 font-mono text-xs text-log-ink">
                      <pre className="overflow-x-auto whitespace-pre-wrap">{tr.codeSnippet}</pre>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Test Execution Output Console */}
            {testOutput && (
              <div className="rounded-xl border border-line bg-log overflow-hidden mt-4 animate-fade-in">
                <div className="flex items-center justify-between border-b border-white/10 px-4 py-2.5 text-xs text-log-ink bg-black/40">
                  <span className="flex items-center gap-2">
                    <Terminal className="h-3.5 w-3.5 text-teal" />
                    <span>Isolated Test Execution Console</span>
                  </span>
                  <span className="font-mono text-teal font-bold">
                    {testOutput.passed ? 'BUILD SUCCESS (0 Errors)' : 'BUILD FAILED'} ({testOutput.durationMs}ms)
                  </span>
                </div>
                <div className="p-4 font-mono text-xs text-log-ink overflow-x-auto max-h-64">
                  <pre className="whitespace-pre-wrap">{testOutput.stdout}</pre>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 5: Inspected Files & Limitations */}
        {activeTab === 'evidence' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-xl border border-line bg-surface p-4 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted">Files Inspected on Disk</h4>
                <ul className="space-y-1.5 font-mono text-xs">
                  {(report?.filesInspected || []).map((file, i) => (
                    <li key={i} className="flex items-center gap-2 text-ink">
                      <FileCode className="h-3.5 w-3.5 text-accent shrink-0" />
                      <span className="truncate">{file}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-line bg-surface p-4 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-muted">Analysis Limitations & Questions</h4>
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="font-semibold text-amber block mb-1">Limitations:</span>
                    <ul className="space-y-1 text-muted">
                      {(report?.limitations || []).map((l, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span>•</span>
                          <span>{l}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="pt-2 border-t border-line/60">
                    <span className="font-semibold text-accent block mb-1">Unresolved Questions for Developer:</span>
                    <ul className="space-y-1 text-muted">
                      {(report?.unresolvedQuestions || []).map((q, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span>?</span>
                          <span>{q}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default CodeInvestigationCard;
