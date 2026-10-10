import React, { useState, useMemo } from 'react';
import { JiraIssue, ApiFlowNode } from '../types';
import { normalizeApiFlow } from '../lib/apiFlowNormalizer';
import { ApiFlowCanvas } from '../components/ApiFlowCanvas';
import { ApiFlowDetailsPanel } from '../components/ApiFlowDetailsPanel';
import { ApiFlowTimeline } from '../components/ApiFlowTimeline';
import {
  ArrowLeft,
  Link as LinkIcon,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  Zap,
  Shield,
  Layers,
  ChevronDown,
} from 'lucide-react';
import { formatDateTime } from '../lib/format';

interface ApiFlowPageProps {
  issues: JiraIssue[];
  currentIssueKey?: string | null;
  onBack: () => void;
  onSelectIssue: (key: string) => void;
}

export const ApiFlowPage: React.FC<ApiFlowPageProps> = ({
  issues,
  currentIssueKey,
  onBack,
  onSelectIssue,
}) => {
  // Find current issue, fallback to first investigated or first available
  const activeIssue = useMemo(() => {
    if (currentIssueKey) {
      const found = issues.find((i) => i.jiraKey === currentIssueKey);
      if (found) return found;
    }
    const investigated = issues.find((i) => i.status === 'INVESTIGATED' || i.investigation);
    return investigated || issues[0] || null;
  }, [issues, currentIssueKey]);

  // Normalize data into graph topology
  const graphData = useMemo(() => {
    if (!activeIssue) return null;
    return normalizeApiFlow(activeIssue);
  }, [activeIssue]);

  // Selected node state - defaults to failure point if available
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Initialize selected node to failure point if exists
  React.useEffect(() => {
    if (graphData && !selectedNodeId) {
      const errorNode = graphData.nodes.find((n) => n.isFailurePoint || n.status === 'FAILED');
      if (errorNode) {
        setSelectedNodeId(errorNode.id);
      } else if (graphData.nodes.length > 1) {
        setSelectedNodeId(graphData.nodes[1].id);
      }
    }
  }, [graphData, selectedNodeId]);

  const selectedNode = useMemo(() => {
    if (!graphData || !selectedNodeId) return null;
    return graphData.nodes.find((n) => n.id === selectedNodeId) || null;
  }, [graphData, selectedNodeId]);

  if (!activeIssue || !graphData) {
    return (
      <div className="flex min-h-[600px] flex-col items-center justify-center rounded-2xl border border-indigo-500/20 bg-[#060a17] p-8 text-center text-indigo-300">
        <Layers className="mb-4 h-12 w-12 text-indigo-400/40" />
        <h2 className="text-lg font-bold text-white">No Diagnostic Telemetry Available</h2>
        <p className="mt-1 max-w-md text-xs text-indigo-300/70">
          No Jira incident tickets found with log telemetry. Sync Jira or ingest synthetic incidents to explore the API Flow Map.
        </p>
        <button
          type="button"
          onClick={onBack}
          className="mt-6 flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Return to Dashboard</span>
        </button>
      </div>
    );
  }

  const { metrics } = graphData;

  return (
    <div className="space-y-6 pb-12 animate-fade-in text-slate-100">
      {/* 1. TOP HEADER & BREADCRUMB */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          {/* Back button */}
          <button
            type="button"
            onClick={onBack}
            className="group mb-2 flex items-center gap-1.5 text-xs font-semibold text-indigo-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5 transition-transform group-hover:-translate-x-1" />
            <span>Back to Dashboard</span>
          </button>

          {/* Breadcrumb */}
          <div className="flex items-center gap-2 font-mono text-xs text-indigo-400/70">
            <span>Dashboard</span>
            <span>&rsaquo;</span>
            <span>Investigation</span>
            <span>&rsaquo;</span>
            <span className="text-cyan-300 font-bold">{activeIssue.jiraKey}</span>
          </div>

          <h1 className="mt-1 text-2xl font-black tracking-tight text-white sm:text-3xl">
            API Flow Visualization
          </h1>
          <p className="mt-1 text-xs text-indigo-300/80 sm:text-sm">
            Explore the request flow, dependencies and errors across services. Click on any API call to view details.
          </p>
        </div>

        {/* Right Header Metadata Pill & Ticket Selector */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Issue Switcher Dropdown */}
          <div className="relative">
            <select
              value={activeIssue.jiraKey}
              onChange={(e) => {
                onSelectIssue(e.target.value);
                setSelectedNodeId(null);
              }}
              className="appearance-none rounded-xl border border-indigo-500/30 bg-[#0c1427] px-3.5 py-2 pr-9 font-mono text-xs font-bold text-white shadow-lg focus:border-cyan-400 focus:outline-none"
            >
              {issues.map((iss) => (
                <option key={iss.jiraKey} value={iss.jiraKey} className="bg-[#0c1427]">
                  {iss.jiraKey} — {iss.summary.slice(0, 32)}...
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-2.5 h-3.5 w-3.5 text-indigo-400" />
          </div>

          {/* Metadata pill */}
          <div className="flex items-center gap-2 rounded-xl border border-indigo-500/30 bg-[#0c1427] px-3 py-2 font-mono text-xs shadow-lg">
            <span className="font-bold text-indigo-200">{activeIssue.jiraKey}</span>
            <span className="rounded-md bg-red-500/20 px-2 py-0.5 text-[10px] font-bold text-red-400 border border-red-500/30">
              High Priority
            </span>
            <span className="text-[11px] text-indigo-400">
              {formatDateTime(activeIssue.updatedAt || activeIssue.createdAt)}
            </span>
          </div>
        </div>
      </div>

      {/* 2. SUMMARY METRIC KPI CARDS */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
        {/* Card 1: Total APIs */}
        <div className="rounded-2xl border border-indigo-500/20 bg-[#090f20]/90 p-4 shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-300">
              <LinkIcon className="h-4 w-4" />
            </div>
            <span>Total APIs</span>
          </div>
          <div className="mt-3 text-2xl font-black text-white font-mono">
            {metrics.totalApis}
          </div>
        </div>

        {/* Card 2: Successful */}
        <div className="rounded-2xl border border-emerald-500/20 bg-[#07171a]/90 p-4 shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-300">
              <CheckCircle2 className="h-4 w-4" />
            </div>
            <span>Successful</span>
          </div>
          <div className="mt-3 text-2xl font-black text-emerald-300 font-mono">
            {metrics.successfulCount}
          </div>
        </div>

        {/* Card 3: Errors */}
        <div className="rounded-2xl border border-red-500/30 bg-[#1f0a12]/90 p-4 shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-2 text-red-400 text-xs font-semibold">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-red-500/20 text-red-400">
              <AlertTriangle className="h-4 w-4" />
            </div>
            <span>Errors</span>
          </div>
          <div className="mt-3 text-2xl font-black text-red-400 font-mono">
            {metrics.errorCount}
          </div>
        </div>

        {/* Card 4: Avg. Response Time */}
        <div className="rounded-2xl border border-cyan-500/20 bg-[#071424]/90 p-4 shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-300">
              <Clock className="h-4 w-4" />
            </div>
            <span>Avg. Response Time</span>
          </div>
          <div className="mt-3 text-2xl font-black text-cyan-300 font-mono">
            {metrics.avgResponseTimeMs !== null ? `${metrics.avgResponseTimeMs}ms` : 'Not present in logs'}
          </div>
        </div>
      </div>

      {/* 3. MAIN INTERACTIVE VISUALIZATION GRID */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left 2 Cols: Interactive Holographic Canvas + Timeline + Feature Cards */}
        <div className="space-y-6 lg:col-span-2">
          {/* Main Holographic Canvas */}
          <ApiFlowCanvas
            nodes={graphData.nodes}
            edges={graphData.edges}
            selectedNodeId={selectedNodeId}
            onSelectNode={(node) => setSelectedNodeId(node.id)}
            hoveredNodeId={hoveredNodeId}
            onHoverNode={setHoveredNodeId}
          />

          {/* Synchronized Request Flow Timeline */}
          <ApiFlowTimeline
            steps={graphData.timeline}
            selectedNodeId={selectedNodeId}
            onSelectStep={(nodeId) => setSelectedNodeId(nodeId)}
          />

          {/* Bottom 3 Feature Highlights (matching mockup) */}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {/* Feature 1 */}
            <div className="flex items-start gap-3 rounded-2xl border border-indigo-500/20 bg-[#090f20]/80 p-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-indigo-500/20 text-indigo-300">
                <Sparkles className="h-4 w-4 text-cyan-400" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">Interactive API Flow</h4>
                <p className="mt-0.5 text-[11px] text-indigo-300/70">
                  Explore the full request chain and service dependencies.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex items-start gap-3 rounded-2xl border border-indigo-500/20 bg-[#090f20]/80 p-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-purple-500/20 text-purple-300">
                <Zap className="h-4 w-4 text-purple-400" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">Instant Error Insights</h4>
                <p className="mt-0.5 text-[11px] text-indigo-300/70">
                  Click any failed API to see detailed error telemetry.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="flex items-start gap-3 rounded-2xl border border-indigo-500/20 bg-[#090f20]/80 p-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-300">
                <Shield className="h-4 w-4 text-cyan-400" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">Faster Root Cause Analysis</h4>
                <p className="mt-0.5 text-[11px] text-indigo-300/70">
                  Understand the bigger picture, not just the isolated error.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Details & Evidence Panel */}
        <div className="lg:col-span-1">
          <ApiFlowDetailsPanel
            node={selectedNode}
            edges={graphData.edges}
            nodes={graphData.nodes}
            onClose={() => setSelectedNodeId(null)}
            onSelectNode={(node) => setSelectedNodeId(node.id)}
          />
        </div>
      </div>
    </div>
  );
};
