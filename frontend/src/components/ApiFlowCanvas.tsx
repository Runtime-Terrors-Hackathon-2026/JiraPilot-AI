import React, { useState, useRef, useEffect } from 'react';
import {
  ApiFlowNode,
  ApiFlowEdge,
} from '../types';
import {
  User,
  CheckCircle2,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  Sparkles,
  Table as TableIcon,
} from 'lucide-react';
import { cn } from '../lib/cn';

interface ApiFlowCanvasProps {
  nodes: ApiFlowNode[];
  edges: ApiFlowEdge[];
  selectedNodeId: string | null;
  onSelectNode: (node: ApiFlowNode) => void;
  hoveredNodeId: string | null;
  onHoverNode: (nodeId: string | null) => void;
}

// 3D Isometric Holographic Cube Icon
const HolographicCube: React.FC<{ isError?: boolean; size?: number }> = ({ isError, size = 26 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={cn('transition-transform duration-300', isError ? 'text-red-400' : 'text-cyan-400')}
  >
    {/* Top Face */}
    <path
      d="M16 3L28 9.5L16 16L4 9.5L16 3Z"
      fill={isError ? 'rgba(239, 68, 68, 0.35)' : 'rgba(6, 182, 212, 0.35)'}
      stroke={isError ? '#f87171' : '#38bdf8'}
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Left Face */}
    <path
      d="M4 9.5V22.5L16 29V16L4 9.5Z"
      fill={isError ? 'rgba(185, 28, 28, 0.45)' : 'rgba(2, 132, 199, 0.45)'}
      stroke={isError ? '#ef4444' : '#0284c7'}
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Right Face */}
    <path
      d="M16 16L28 9.5V22.5L16 29V16Z"
      fill={isError ? 'rgba(127, 29, 29, 0.55)' : 'rgba(3, 105, 161, 0.55)'}
      stroke={isError ? '#dc2626' : '#0369a1'}
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
    {/* Inner Core */}
    <circle
      cx="16"
      cy="16"
      r="2"
      fill={isError ? '#fca5a5' : '#7dd3fc'}
      className={isError ? 'animate-pulse' : ''}
    />
  </svg>
);

export const ApiFlowCanvas: React.FC<ApiFlowCanvasProps> = ({
  nodes,
  edges,
  selectedNodeId,
  onSelectNode,
  hoveredNodeId,
  onHoverNode,
}) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number } | null>(null);
  const [showTableView, setShowTableView] = useState(false);
  const [holographicRings, setHolographicRings] = useState(true);

  const containerRef = useRef<HTMLDivElement>(null);

  // Track cursor coordinates for holographic scanner ring
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setCursorPos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });

    if (isDragging) {
      setPan((prev) => ({
        x: prev.x + (e.clientX - dragStart.x),
        y: prev.y + (e.clientY - dragStart.y),
      }));
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    // Only drag when clicking background
    if ((e.target as HTMLElement).closest('.interactive-node')) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Node lookup map
  const nodeMap = new Map<string, ApiFlowNode>();
  nodes.forEach((n) => nodeMap.set(n.id, n));

  // Determine if edge connects to active/hovered/selected node
  const isEdgeHighlighted = (edge: ApiFlowEdge) => {
    const activeId = selectedNodeId || hoveredNodeId;
    if (!activeId) return false;
    return edge.source === activeId || edge.target === activeId;
  };

  return (
    <div className="relative w-full overflow-hidden rounded-2xl border border-indigo-500/20 bg-[#060a17] shadow-2xl">
      {/* Top Controls Toolbar */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-2">
        <div className="flex items-center rounded-xl border border-indigo-500/30 bg-[#0c1427]/85 p-1 backdrop-blur-md">
          <button
            type="button"
            onClick={() => setZoom((z) => Math.min(z + 0.15, 1.6))}
            className="rounded-lg p-1.5 text-indigo-300 hover:bg-indigo-500/20 hover:text-white transition-colors"
            title="Zoom In"
            aria-label="Zoom in"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => setZoom((z) => Math.max(z - 0.15, 0.65))}
            className="rounded-lg p-1.5 text-indigo-300 hover:bg-indigo-500/20 hover:text-white transition-colors"
            title="Zoom Out"
            aria-label="Zoom out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={handleResetView}
            className="rounded-lg p-1.5 text-indigo-300 hover:bg-indigo-500/20 hover:text-white transition-colors"
            title="Reset View"
            aria-label="Reset canvas zoom"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          <div className="mx-1 h-4 w-px bg-indigo-500/30" />
          <button
            type="button"
            onClick={() => setHolographicRings(!holographicRings)}
            className={cn(
              'flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold transition-colors',
              holographicRings
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'text-indigo-400 hover:bg-indigo-500/10'
            )}
            title="Toggle Holographic Scanner Rings"
          >
            <Sparkles className="h-3 w-3" />
            <span>Holo FX</span>
          </button>
        </div>

        {/* View Mode Switcher: Graph vs Accessible Table */}
        <button
          type="button"
          onClick={() => setShowTableView(!showTableView)}
          className={cn(
            'flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold backdrop-blur-md transition-colors',
            showTableView
              ? 'border-indigo-400 bg-indigo-600/30 text-indigo-200'
              : 'border-indigo-500/30 bg-[#0c1427]/85 text-indigo-300 hover:bg-indigo-500/20'
          )}
        >
          {showTableView ? <Layers className="h-3.5 w-3.5" /> : <TableIcon className="h-3.5 w-3.5" />}
          <span>{showTableView ? 'Show Graph Canvas' : 'Accessible List View'}</span>
        </button>
      </div>

      {/* Canvas View or Tabular Accessibility View */}
      {showTableView ? (
        <div className="min-h-[560px] p-6 text-indigo-200">
          <div className="mb-4">
            <h3 className="text-sm font-bold text-white">API Call Sequence Table (Accessible View)</h3>
            <p className="text-xs text-indigo-300/70">
              Textual alternative of the request topology with line references and observed findings.
            </p>
          </div>
          <div className="overflow-x-auto rounded-xl border border-indigo-500/20 bg-[#0b1021]">
            <table className="w-full text-left text-xs" role="table">
              <thead className="border-b border-indigo-500/20 bg-indigo-950/40 text-indigo-300 uppercase tracking-wider font-mono">
                <tr>
                  <th className="px-4 py-3">Step</th>
                  <th className="px-4 py-3">Service Name</th>
                  <th className="px-4 py-3">Method & Endpoint</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Latency</th>
                  <th className="px-4 py-3">Evidence Category</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-indigo-500/10 font-mono">
                {nodes.map((node, i) => (
                  <tr
                    key={node.id}
                    onClick={() => onSelectNode(node)}
                    className={cn(
                      'cursor-pointer transition-colors',
                      selectedNodeId === node.id
                        ? 'bg-indigo-600/25 text-white'
                        : 'hover:bg-indigo-950/30',
                      node.isFailurePoint && 'text-red-300'
                    )}
                  >
                    <td className="px-4 py-3 font-bold">{node.label}</td>
                    <td className="px-4 py-3 text-indigo-200 font-sans">{node.serviceName}</td>
                    <td className="px-4 py-3">
                      <span className="font-bold text-indigo-400 mr-2">{node.method}</span>
                      <span>{node.endpoint || 'N/A'}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          'rounded-md px-2 py-0.5 text-[11px] font-bold',
                          node.status === 'FAILED'
                            ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                        )}
                      >
                        {node.statusText || node.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">{node.responseTimeMs ? `${node.responseTimeMs}ms` : 'Unavailable'}</td>
                    <td className="px-4 py-3 text-indigo-400 font-sans">
                      {node.isObserved ? 'Directly Observed Log Evidence' : 'Inferred Architecture Dependency'}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectNode(node);
                        }}
                        className="text-cyan-400 hover:underline text-[11px]"
                      >
                        Inspect Details &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div
          ref={containerRef}
          onMouseMove={handleMouseMove}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          className="relative min-h-[580px] w-full cursor-grab active:cursor-grabbing select-none"
          style={{
            backgroundImage: `
              radial-gradient(circle at 50% 30%, rgba(99, 102, 241, 0.12) 0%, transparent 60%),
              radial-gradient(circle at 65% 65%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
              linear-gradient(to right, rgba(99, 102, 241, 0.05) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(99, 102, 241, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '100% 100%, 100% 100%, 48px 48px, 48px 48px',
          }}
        >
          {/* Subtle Cyber Radar Scanning Circle following pointer */}
          {holographicRings && cursorPos && (
            <div
              className="pointer-events-none absolute -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-500/25 transition-all duration-75"
              style={{
                left: cursorPos.x,
                top: cursorPos.y,
                width: 180,
                height: 180,
                background: 'radial-gradient(circle, rgba(6, 182, 212, 0.05) 0%, transparent 70%)',
                boxShadow: '0 0 25px rgba(6, 182, 212, 0.12)',
              }}
            >
              <div className="absolute inset-4 rounded-full border border-indigo-400/20" />
              <div className="absolute inset-10 rounded-full border border-dashed border-cyan-400/30" />
            </div>
          )}

          {/* SVG Connection Edges Layer */}
          <svg
            className="absolute inset-0 h-full w-full pointer-events-none"
            viewBox="0 0 1060 580"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: '50% 50%',
            }}
          >
            <defs>
              <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
              <filter id="glow-red" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {edges.map((edge) => {
              const src = nodeMap.get(edge.source);
              const tgt = nodeMap.get(edge.target);
              if (!src || !tgt) return null;

              const isHighlighted = isEdgeHighlighted(edge);
              const isError = edge.status === 'ERROR';

              // Smooth cubic bezier curved paths
              const dx = tgt.x - src.x;
              const cp1x = src.x + dx * 0.45;
              const cp1y = src.y;
              const cp2x = tgt.x - dx * 0.45;
              const cp2y = tgt.y;
              const pathD = `M ${src.x} ${src.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${tgt.x} ${tgt.y}`;

              return (
                <g key={edge.id} className="transition-all duration-300">
                  {/* Background glow stroke */}
                  <path
                    d={pathD}
                    fill="none"
                    stroke={isError ? 'rgba(239, 68, 68, 0.3)' : 'rgba(6, 182, 212, 0.25)'}
                    strokeWidth={isHighlighted ? 4 : 2}
                    filter={isError ? 'url(#glow-red)' : 'url(#glow-cyan)'}
                    strokeDasharray={edge.dashed ? '6 6' : undefined}
                  />

                  {/* Sharp core path */}
                  <path
                    d={pathD}
                    fill="none"
                    stroke={
                      isError
                        ? '#ef4444'
                        : isHighlighted
                        ? '#38bdf8'
                        : '#0284c7'
                    }
                    strokeWidth={isHighlighted ? 2.5 : 1.5}
                    strokeDasharray={edge.dashed ? '6 6' : undefined}
                  />

                  {/* Traveling Pulse Particle */}
                  <circle r={isHighlighted ? 3.5 : 2.5} fill={isError ? '#f87171' : '#7dd3fc'}>
                    <animateMotion
                      path={pathD}
                      dur={isError ? '1.8s' : '2.8s'}
                      repeatCount="indefinite"
                    />
                  </circle>
                </g>
              );
            })}
          </svg>

          {/* Interactive Graph Nodes Layer */}
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: '50% 50%',
            }}
          >
            {nodes.map((node) => {
              const isSelected = selectedNodeId === node.id;
              const isHovered = hoveredNodeId === node.id;
              const isDimmed = selectedNodeId != null && !isSelected;
              const isClient = node.type === 'client';
              const isResponse = node.type === 'response';
              const isError = node.isFailurePoint || node.status === 'FAILED';

              return (
                <div
                  key={node.id}
                  tabIndex={0}
                  role="button"
                  aria-label={`${node.label}: ${node.serviceName} ${node.endpoint || ''}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectNode(node);
                  }}
                  onMouseEnter={() => onHoverNode(node.id)}
                  onMouseLeave={() => onHoverNode(null)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelectNode(node);
                    }
                  }}
                  className={cn(
                    'interactive-node pointer-events-auto absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 focus:outline-none',
                    isDimmed && 'opacity-40 hover:opacity-100',
                    isSelected && 'scale-110 z-30',
                    isHovered && !isSelected && 'scale-105 z-20'
                  )}
                  style={{ left: node.x, top: node.y }}
                >
                  {/* CLIENT INGRESS NODE */}
                  {isClient && (
                    <div className="flex flex-col items-center">
                      <div
                        className={cn(
                          'relative flex h-14 w-14 items-center justify-center rounded-full border-2 transition-all',
                          isSelected
                            ? 'border-indigo-400 bg-indigo-600/40 shadow-[0_0_25px_rgba(99,102,241,0.6)]'
                            : 'border-indigo-500/50 bg-[#0c1427] shadow-[0_0_15px_rgba(99,102,241,0.3)]'
                        )}
                      >
                        <User className="h-6 w-6 text-indigo-300" />
                        <div className="absolute -inset-1 rounded-full border border-indigo-500/30 animate-ping opacity-25" />
                      </div>
                      <span className="mt-2 text-xs font-bold text-white tracking-wide">{node.label}</span>
                      <span className="text-[10px] text-indigo-300/80 font-mono">Request</span>
                    </div>
                  )}

                  {/* RESPONSE EGRESS NODE */}
                  {isResponse && (
                    <div className="flex flex-col items-center">
                      <div
                        className={cn(
                          'relative flex h-14 w-14 items-center justify-center rounded-full border-2 transition-all',
                          isError
                            ? 'border-red-500 bg-red-950/60 shadow-[0_0_25px_rgba(239,68,68,0.6)] text-red-300'
                            : isSelected
                            ? 'border-cyan-400 bg-cyan-600/40 shadow-[0_0_25px_rgba(6,182,212,0.6)] text-cyan-300'
                            : 'border-cyan-500/50 bg-[#0c1427] shadow-[0_0_15px_rgba(6,182,212,0.3)] text-cyan-300'
                        )}
                      >
                        {isError ? (
                          <AlertTriangle className="h-6 w-6 text-red-400 animate-pulse" />
                        ) : (
                          <CheckCircle2 className="h-6 w-6 text-cyan-300" />
                        )}
                      </div>
                      <span className="mt-2 text-xs font-bold text-white tracking-wide">{node.label}</span>
                      <span
                        className={cn(
                          'text-[10px] font-mono font-bold',
                          isError ? 'text-red-400' : 'text-cyan-400'
                        )}
                      >
                        {isError ? 'Error (503)' : 'Success'}
                      </span>
                    </div>
                  )}

                  {/* INTERMEDIATE API / SERVICE NODES */}
                  {!isClient && !isResponse && (
                    <div
                      className={cn(
                        'relative flex flex-col items-center rounded-2xl border p-3 backdrop-blur-md transition-all',
                        isError
                          ? 'border-red-500/80 bg-[#1e0a13]/95 shadow-[0_0_30px_rgba(239,68,68,0.4)] ring-2 ring-red-500/40'
                          : isSelected
                          ? 'border-cyan-400 bg-[#0c192f]/95 shadow-[0_0_30px_rgba(6,182,212,0.5)] ring-2 ring-cyan-400/50'
                          : 'border-cyan-500/30 bg-[#0a1224]/90 shadow-[0_0_15px_rgba(6,182,212,0.15)] hover:border-cyan-400/70',
                        'min-w-[140px] max-w-[160px]'
                      )}
                    >
                      {/* Pulsing Aura on Failure */}
                      {isError && (
                        <div className="absolute -inset-1 rounded-2xl border border-red-500/40 animate-pulse opacity-50" />
                      )}

                      {/* 3D Holographic Cube Icon */}
                      <div className="mb-1.5 flex h-9 w-9 items-center justify-center rounded-xl bg-black/40 border border-white/5">
                        <HolographicCube isError={isError} size={24} />
                      </div>

                      {/* API Label (e.g. API 1, API 4) */}
                      <div className="text-xs font-bold text-white tracking-wide">{node.label}</div>

                      {/* Endpoint route */}
                      <div className="mt-0.5 truncate max-w-[130px] font-mono text-[11px] text-cyan-200/90 font-medium">
                        {node.endpoint}
                      </div>

                      {/* Status Code & Response Time Pill */}
                      <div className="mt-2 flex items-center gap-1.5 font-mono text-[10px]">
                        <span
                          className={cn(
                            'flex items-center gap-1 font-bold',
                            isError ? 'text-red-400' : 'text-emerald-400'
                          )}
                        >
                          {isError ? '▲' : '●'} {node.statusCode || 200}
                        </span>
                        {node.responseTimeMs && (
                          <span className="text-indigo-300/80">
                            {node.responseTimeMs}ms
                          </span>
                        )}
                      </div>

                      {/* Inferred Dependency Indicator */}
                      {!node.isObserved && (
                        <span className="mt-1 rounded-full bg-purple-500/20 px-1.5 py-0.5 text-[9px] font-semibold text-purple-300 border border-purple-500/30">
                          Inferred
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
