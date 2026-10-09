import React from 'react';
import { Database, Server } from 'lucide-react';
import { ServiceEdge, ServiceNode } from '../types';
import { Card, EmptyState, StatusBadge } from './ui/primitives';
import { cn } from '../lib/cn';

interface ServiceGraphProps {
  nodes?: ServiceNode[];
  edges?: ServiceEdge[];
}

export const ServiceGraph: React.FC<ServiceGraphProps> = ({ nodes, edges }) => {
  const graphNodes = nodes || [];

  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold text-ink">Service path</h3>
      <p className="mb-3 text-xs text-muted">Shown only when the investigation engine returns a service graph.</p>
      {graphNodes.length === 0 ? (
        <EmptyState title="No service graph for this issue" description="Topology is omitted until the analysis engine returns nodes." />
      ) : (
        <div className="grid grid-cols-1 gap-2 md:grid-cols-5">
          {graphNodes.map((node) => (
            <div
              key={node.id}
              className={cn(
                'rounded-lg border p-3',
                node.isFailurePoint || node.status === 'FAILED'
                  ? 'border-danger/40 bg-danger-soft'
                  : node.status === 'DEGRADED'
                  ? 'border-amber/40 bg-amber-soft'
                  : 'border-line bg-surface-2'
              )}
            >
              <div className="mb-2 flex items-center justify-between">
                {node.type === 'database' ? <Database className="h-4 w-4 text-muted" /> : <Server className="h-4 w-4 text-muted" />}
                <StatusBadge tone={node.status === 'FAILED' ? 'danger' : node.status === 'DEGRADED' ? 'warning' : 'success'}>
                  {node.status}
                </StatusBadge>
              </div>
              <div className="text-xs font-semibold text-ink">{node.name}</div>
              <div className="text-[11px] text-muted">{node.details}</div>
            </div>
          ))}
        </div>
      )}
      {edges && edges.length > 0 && (
        <p className="mt-3 text-[11px] text-muted">{edges.length} recorded service edges in the investigation payload.</p>
      )}
    </Card>
  );
};
