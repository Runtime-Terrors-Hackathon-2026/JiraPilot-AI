import React, { useState } from 'react';
import { ApiFlowNode, ApiFlowEdge } from '../types';
import {
  X,
  Copy,
  Check,
  AlertTriangle,
  ShieldCheck,
  Terminal,
  FileText,
  Layers,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';
import { cn } from '../lib/cn';
import { useToast } from './ui/Toast';

interface ApiFlowDetailsPanelProps {
  node: ApiFlowNode | null;
  edges: ApiFlowEdge[];
  nodes: ApiFlowNode[];
  onClose: () => void;
  onSelectNode: (node: ApiFlowNode) => void;
}

export const ApiFlowDetailsPanel: React.FC<ApiFlowDetailsPanelProps> = ({
  node,
  edges,
  nodes,
  onClose,
  onSelectNode,
}) => {
  const { push } = useToast();
  const [activeTab, setActiveTab] = useState<'overview' | 'logs' | 'payload' | 'related'>('overview');
  const [copiedLog, setCopiedLog] = useState(false);

  if (!node) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center rounded-2xl border border-indigo-500/20 bg-[#090e1c] p-6 text-center text-indigo-300/70">
        <Layers className="mb-3 h-8 w-8 text-indigo-400/40" />
        <h4 className="text-sm font-semibold text-white">No API Call Selected</h4>
        <p className="mt-1 max-w-[240px] text-xs">
          Click any node on the request topology or timeline to inspect its telemetry, logs, and root cause evidence.
        </p>
      </div>
    );
  }

  const isError = node.isFailurePoint || node.status === 'FAILED';

  // Connected incoming & outgoing edges
  const incomingEdges = edges.filter((e) => e.target === node.id);
  const outgoingEdges = edges.filter((e) => e.source === node.id);

  const incomingNodes = incomingEdges
    .map((e) => nodes.find((n) => n.id === e.source))
    .filter((n): n is ApiFlowNode => Boolean(n));

  const outgoingNodes = outgoingEdges
    .map((e) => nodes.find((n) => n.id === e.target))
    .filter((n): n is ApiFlowNode => Boolean(n));

  const handleCopyLogs = () => {
    if (!node.relatedLogs || node.relatedLogs.length === 0) return;
    const text = node.relatedLogs.map((l) => `[Line ${l.line}] ${l.text}`).join('\n');
    navigator.clipboard.writeText(text);
    setCopiedLog(true);
    push({ kind: 'success', title: 'Telemetry logs copied to clipboard' });
    setTimeout(() => setCopiedLog(false), 2000);
  };

  return (
    <div className="flex h-full flex-col rounded-2xl border border-indigo-500/25 bg-[#090f20]/95 p-5 shadow-2xl backdrop-blur-xl">
      {/* Panel Top Header */}
      <div className="flex items-start justify-between border-b border-indigo-500/20 pb-4">
        <div className="min-w-0 pr-3">
          <div className="flex items-center gap-2">
            {isError ? (
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-red-500/20 text-red-400">
                <AlertTriangle className="h-4 w-4" />
              </div>
            ) : (
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-400">
                <Layers className="h-4 w-4" />
              </div>
            )}
            <h3 className="truncate text-sm font-bold text-white tracking-wide">
              {node.label} {node.endpoint ? `— ${node.endpoint}` : ''}
            </h3>
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span
              className={cn(
                'rounded-md px-2 py-0.5 font-mono text-[11px] font-bold',
                isError
                  ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              )}
            >
              {node.statusText || `${node.statusCode || 200} OK`}
            </span>
            <span className="font-mono text-xs text-indigo-300">
              {node.serviceName}
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="rounded-lg p-1.5 text-indigo-400 hover:bg-indigo-500/20 hover:text-white transition-colors"
          title="Close details"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Tabs Bar */}
      <div className="mt-3 flex gap-1 border-b border-indigo-500/15 pb-2 text-xs font-semibold">
        {[
          { id: 'overview' as const, label: 'Overview' },
          { id: 'logs' as const, label: `Logs (${node.relatedLogs?.length || 0})` },
          { id: 'payload' as const, label: 'Request/Response' },
          { id: 'related' as const, label: 'Related' },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'rounded-lg px-2.5 py-1.5 transition-colors',
              activeTab === tab.id
                ? 'bg-indigo-600/40 text-cyan-300 border border-indigo-400/40'
                : 'text-indigo-400 hover:bg-indigo-500/10 hover:text-indigo-200'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content Body */}
      <div className="flex-1 overflow-y-auto pt-4 space-y-4 text-xs font-sans">
        {/* 1. OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Meta Key-Value Grid */}
            <div className="grid grid-cols-2 gap-2.5 rounded-xl border border-indigo-500/20 bg-[#0c1427]/80 p-3.5 text-xs">
              <div>
                <span className="text-[10px] uppercase font-bold text-indigo-400/70 tracking-wider">Endpoint</span>
                <p className="mt-0.5 font-mono text-white truncate">{node.endpoint || 'Not present in logs'}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-indigo-400/70 tracking-wider">Method</span>
                <p className="mt-0.5 font-mono font-bold text-red-400">{node.method || 'UNKNOWN'}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-indigo-400/70 tracking-wider">Status Code</span>
                <p className={cn('mt-0.5 font-mono font-bold', isError ? 'text-red-400' : 'text-emerald-400')}>
                  {node.statusCode || 'Unavailable'}
                </p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-indigo-400/70 tracking-wider">Response Time</span>
                <p className="mt-0.5 font-mono text-cyan-300">
                  {node.responseTimeMs ? `${node.responseTimeMs} ms` : 'Not present in logs'}
                </p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-indigo-400/70 tracking-wider">Timestamp</span>
                <p className="mt-0.5 font-mono text-indigo-200">{node.timestamp || 'Mar 15, 2025 10:24:32 AM'}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-indigo-400/70 tracking-wider">Correlation ID</span>
                <p className="mt-0.5 font-mono text-cyan-400 truncate">{node.correlationId || 'Unavailable'}</p>
              </div>
              <div className="col-span-2 pt-1 border-t border-indigo-500/15">
                <span className="text-[10px] uppercase font-bold text-indigo-400/70 tracking-wider">Service</span>
                <p className="mt-0.5 font-sans font-medium text-white">{node.serviceName}</p>
              </div>
            </div>

            {/* Error Message Card if failure */}
            {isError && (
              <div className="rounded-xl border border-red-500/40 bg-red-950/30 p-3.5 space-y-1.5">
                <div className="flex items-center gap-1.5 text-red-400 font-bold text-xs uppercase tracking-wide">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  <span>Observed Error Message</span>
                </div>
                <p className="text-red-200 text-xs leading-relaxed font-sans">
                  {node.errorMessage || 'Service temporarily unavailable. Please try again later.'}
                </p>
              </div>
            )}

            {/* Possible Root Cause Hypothesis Card */}
            {node.possibleCause && (
              <div className="rounded-xl border border-amber-500/40 bg-amber-950/25 p-3.5 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-amber-400 font-bold text-xs uppercase tracking-wide">
                    <span>⚡ Probable Cause Hypothesis</span>
                  </div>
                  {node.confidenceLevel && (
                    <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300 border border-amber-500/30">
                      {node.confidenceLevel} Confidence
                    </span>
                  )}
                </div>
                <p className="text-amber-100 text-xs leading-relaxed font-sans">
                  {node.possibleCause}
                </p>
                <p className="text-[10px] text-amber-300/70 italic">
                  Note: This is an evidence-backed hypothesis from diagnostic telemetry, not a confirmed root cause.
                </p>
              </div>
            )}

            {/* Related Logs Preview */}
            {node.relatedLogs && node.relatedLogs.length > 0 && (
              <div className="rounded-xl border border-indigo-500/20 bg-[#070b16] p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-300">Related Telemetry Excerpt</span>
                  <button
                    type="button"
                    onClick={() => setActiveTab('logs')}
                    className="text-[11px] text-cyan-400 hover:underline flex items-center gap-1"
                  >
                    View All Logs &rarr;
                  </button>
                </div>
                <div className="space-y-1 font-mono text-[11px] text-indigo-300/90 max-h-32 overflow-y-auto">
                  {node.relatedLogs.slice(0, 3).map((l, i) => (
                    <div key={i} className="flex gap-2 leading-relaxed">
                      <span className="text-indigo-500 select-none">L{l.line}:</span>
                      <span className="truncate">{l.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 2. LOGS TAB */}
        {activeTab === 'logs' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-indigo-200">
                Log Telemetry with Line References
              </span>
              <button
                type="button"
                onClick={handleCopyLogs}
                className="flex items-center gap-1 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-1 text-[11px] text-indigo-300 hover:bg-indigo-500/20"
              >
                {copiedLog ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copiedLog ? 'Copied' : 'Copy Logs'}</span>
              </button>
            </div>

            {node.relatedLogs && node.relatedLogs.length > 0 ? (
              <div className="max-h-80 overflow-y-auto rounded-xl border border-indigo-500/20 bg-[#050814] p-3 font-mono text-[11px]">
                {node.relatedLogs.map((logItem, idx) => (
                  <div key={idx} className="flex gap-3 py-1 border-b border-indigo-500/10 last:border-0">
                    <span className="text-indigo-500 select-none w-10 text-right shrink-0">
                      {logItem.line}
                    </span>
                    <span
                      className={cn(
                        'break-all leading-relaxed',
                        logItem.text.includes('500') || logItem.text.includes('503') || logItem.text.includes('ERROR')
                          ? 'text-red-300 font-semibold'
                          : 'text-indigo-200'
                      )}
                    >
                      {logItem.text}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-indigo-500/15 p-4 text-center text-xs text-indigo-400">
                No direct line-referenced logs isolated for this node.
              </div>
            )}
          </div>
        )}

        {/* 3. REQUEST / RESPONSE TAB */}
        {activeTab === 'payload' && (
          <div className="space-y-3">
            <div>
              <span className="text-xs font-bold text-indigo-300 block mb-1">Reproduction cURL</span>
              {node.curlCommand ? (
                <div className="rounded-xl border border-indigo-500/20 bg-[#050814] p-3 font-mono text-[11px] text-cyan-300 break-all leading-relaxed">
                  {node.curlCommand}
                </div>
              ) : (
                <p className="text-xs text-indigo-400/80 italic">cURL command not present in investigation.</p>
              )}
            </div>

            <div>
              <span className="text-xs font-bold text-indigo-300 block mb-1">Request Payload (Sanitized)</span>
              {node.requestPayload ? (
                <pre className="rounded-xl border border-indigo-500/20 bg-[#050814] p-3 font-mono text-[11px] text-indigo-200 overflow-x-auto">
                  {node.requestPayload}
                </pre>
              ) : (
                <p className="text-xs text-indigo-400/80 italic">Request payload not captured in logs.</p>
              )}
            </div>
          </div>
        )}

        {/* 4. RELATED SERVICES TAB */}
        {activeTab === 'related' && (
          <div className="space-y-4">
            <div>
              <span className="text-xs font-bold text-indigo-300 uppercase tracking-wide block mb-2">
                Upstream Ingress Callers
              </span>
              {incomingNodes.length > 0 ? (
                <div className="space-y-1.5">
                  {incomingNodes.map((inc) => (
                    <button
                      key={inc.id}
                      type="button"
                      onClick={() => onSelectNode(inc)}
                      className="flex w-full items-center justify-between rounded-xl border border-indigo-500/20 bg-[#0c1427] p-2.5 text-left text-xs text-white hover:border-cyan-400/50"
                    >
                      <div>
                        <div className="font-bold">{inc.label} &bull; {inc.serviceName}</div>
                        <div className="text-[10px] text-cyan-300 font-mono">{inc.endpoint}</div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-indigo-400" />
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-indigo-400/80 italic">Root caller node (no upstream callers).</p>
              )}
            </div>

            <div>
              <span className="text-xs font-bold text-indigo-300 uppercase tracking-wide block mb-2">
                Downstream Target Dependencies
              </span>
              {outgoingNodes.length > 0 ? (
                <div className="space-y-1.5">
                  {outgoingNodes.map((out) => (
                    <button
                      key={out.id}
                      type="button"
                      onClick={() => onSelectNode(out)}
                      className="flex w-full items-center justify-between rounded-xl border border-indigo-500/20 bg-[#0c1427] p-2.5 text-left text-xs text-white hover:border-cyan-400/50"
                    >
                      <div>
                        <div className="font-bold">{out.label} &bull; {out.serviceName}</div>
                        <div className="text-[10px] text-cyan-300 font-mono">{out.endpoint}</div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-indigo-400" />
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-indigo-400/80 italic">Leaf node (no downstream dependencies).</p>
              )}
            </div>

            <div className="rounded-xl border border-indigo-500/15 bg-indigo-950/20 p-3 text-[11px] text-indigo-300/90 leading-relaxed">
              <span className="font-bold text-white block mb-0.5">Evidence Status:</span>
              {node.isObserved ? (
                <span className="text-emerald-300">
                  &bull; Directly Observed: This API call and status code were parsed from line-referenced application logs.
                </span>
              ) : (
                <span className="text-purple-300">
                  &bull; Inferred Relationship: {node.inferredReason || 'Inferred from architectural topology; explicit line timestamp not present.'}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
