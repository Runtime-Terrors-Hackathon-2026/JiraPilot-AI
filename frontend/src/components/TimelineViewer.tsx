import React from 'react';
import { AuditEvent, TimelineEvent } from '../types';
import { Card, EmptyState } from './ui/primitives';
import { formatDateTime } from '../lib/format';

interface TimelineViewerProps {
  events?: TimelineEvent[];
  auditEvents?: AuditEvent[];
}

export const TimelineViewer: React.FC<TimelineViewerProps> = ({ events, auditEvents }) => {
  const fromRca = events || [];
  const fromAudit = (auditEvents || []).map((event) => ({
    time: formatDateTime(event.timestamp),
    title: event.eventType,
    description: event.details,
    stage: event.workflowStage,
    status: event.status,
  }));
  const rows = fromRca.length > 0 ? fromRca : fromAudit;

  return (
    <Card className="p-5">
      <h3 className="mb-3 text-sm font-semibold text-ink">Evidence and timeline</h3>
      {rows.length === 0 ? (
        <EmptyState title="No timeline yet" description="Audit events and investigation stages appear after a workflow run." />
      ) : (
        <ol className="space-y-3 border-l border-line pl-4">
          {rows.map((evt, idx) => (
            <li key={`${evt.title}-${idx}`}>
              <div className="flex items-baseline justify-between gap-2">
                <span className="text-xs font-semibold text-ink">{evt.title}</span>
                <span className="font-mono text-[11px] text-muted">{evt.time}</span>
              </div>
              <p className="text-xs text-muted">{evt.description}</p>
            </li>
          ))}
        </ol>
      )}
    </Card>
  );
};
