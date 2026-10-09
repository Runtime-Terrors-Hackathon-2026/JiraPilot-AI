import React from 'react';
import { FileSearch } from 'lucide-react';
import { JiraIssue } from '../types';
import { Card, EmptyState, PageHeader, StatusBadge } from '../components/ui/primitives';
import { attachmentTone } from '../lib/status';
import { formatBytes, formatDateTime, labelStatus } from '../lib/format';

interface LogsPageProps {
  issues: JiraIssue[];
  onSelectIssue: (key: string) => void;
}

export const LogsPage: React.FC<LogsPageProps> = ({ issues, onSelectIssue }) => {
  const rows = issues.flatMap((issue) => (issue.attachments || []).map((att) => ({ issue, att })));

  return (
    <div>
      <PageHeader
        title="Log Investigations"
        description="Attachment processing status, extracted APIs and analysis outcomes across issues."
      />
      <Card className="overflow-hidden">
        {rows.length === 0 ? (
          <EmptyState
            icon={FileSearch}
            title="No log attachments have been analyzed yet."
            description="Add a synthetic log attachment from an issue workspace to begin an investigation."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[880px] text-left text-xs">
              <thead className="border-b border-line bg-surface-2 text-[11px] uppercase tracking-wide text-muted">
                <tr>
                  <th className="px-3 py-2.5 font-medium">Issue</th>
                  <th className="px-3 py-2.5 font-medium">File</th>
                  <th className="px-3 py-2.5 font-medium">Status</th>
                  <th className="px-3 py-2.5 font-medium">Endpoint</th>
                  <th className="px-3 py-2.5 font-medium">Service</th>
                  <th className="px-3 py-2.5 font-medium">Size</th>
                  <th className="px-3 py-2.5 font-medium">Analyzed</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(({ issue, att }) => (
                  <tr key={att.id} className="cursor-pointer border-b border-line hover:bg-surface-2" onClick={() => onSelectIssue(issue.jiraKey)}>
                    <td className="px-3 py-3 font-mono font-semibold text-accent">{issue.jiraKey}</td>
                    <td className="px-3 py-3 text-ink">{att.filename}</td>
                    <td className="px-3 py-3">
                      <StatusBadge tone={attachmentTone(att.status)}>{labelStatus(att.status)}</StatusBadge>
                    </td>
                    <td className="px-3 py-3 font-mono text-ink">{att.primaryEndpoint || '—'}</td>
                    <td className="px-3 py-3">{att.primaryService || '—'}</td>
                    <td className="px-3 py-3 text-muted">{formatBytes(att.sizeBytes)}</td>
                    <td className="px-3 py-3 text-muted">{formatDateTime(att.analyzedAt || att.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
