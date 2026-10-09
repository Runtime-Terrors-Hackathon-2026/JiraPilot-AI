import React from 'react';
import { GitBranch } from 'lucide-react';
import { JiraIssue } from '../types';
import { Card, CloneCommand, EmptyState, PageHeader, StatusBadge } from '../components/ui/primitives';

interface ReposPageProps {
  issues: JiraIssue[];
  onSelectIssue: (key: string) => void;
}

export const ReposPage: React.FC<ReposPageProps> = ({ issues, onSelectIssue }) => {
  const matches = issues.flatMap((issue) =>
    (issue.attachments || [])
      .filter((att) => att.recommendedRepo || att.cloneCommand)
      .map((att) => ({ issue, att }))
  );

  return (
    <div>
      <PageHeader
        title="Repository Explorer"
        description="Approved repository matches returned by the analysis engine. Clone commands are copied exactly as provided."
      />
      {matches.length === 0 ? (
        <Card>
          <EmptyState
            icon={GitBranch}
            title="No verified repository matches this workspace yet."
            description="Review the service catalog or analyze a log attachment so JiraPilot AI can recommend an approved repository."
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
          {matches.map(({ issue, att }) => (
            <Card key={att.id} className="p-4">
              <div className="mb-2 flex items-start justify-between gap-2">
                <div>
                  <h3 className="text-sm font-semibold text-ink">{att.recommendedRepo || 'Repository match'}</h3>
                  <p className="text-xs text-muted">{att.primaryService || issue.affectedService || 'Service pending'} · {att.primaryEndpoint || 'Endpoint pending'}</p>
                </div>
                <StatusBadge tone={att.cloneCommand ? 'success' : 'warning'}>
                  {att.cloneCommand ? 'Command available' : 'Unverified command'}
                </StatusBadge>
              </div>
              <p className="mb-3 text-xs text-muted">
                {att.analysisSummary || 'Matched from attachment evidence. Open the issue to review why this repository was recommended.'}
              </p>
              <CloneCommand command={att.cloneCommand} />
              <button type="button" className="mt-3 text-xs font-medium text-accent" onClick={() => onSelectIssue(issue.jiraKey)}>
                Open {issue.jiraKey}
              </button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
