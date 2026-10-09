import React from 'react';
import { RefreshCw } from 'lucide-react';
import { IssueFilter, JiraIssue } from '../types';
import { IssueTable } from '../components/IssueTable';
import { Button, PageHeader } from '../components/ui/primitives';

interface IssuesPageProps {
  issues: JiraIssue[];
  onSelectIssue: (key: string) => void;
  search: string;
  onSearchChange: (value: string) => void;
  filter: IssueFilter;
  onFilterChange: (filter: IssueFilter) => void;
  onRefresh: () => void;
  onSyncJira?: () => void;
  loading: boolean;
}

export const IssuesPage: React.FC<IssuesPageProps> = ({
  issues,
  onSelectIssue,
  search,
  onSearchChange,
  filter,
  onFilterChange,
  onRefresh,
  onSyncJira,
  loading,
}) => (
  <div>
    <PageHeader
      title="Jira Issues"
      description="Search, filter and open tickets without leaving the investigation workflow."
      actions={
        <div className="flex items-center gap-2">
          {onSyncJira && (
            <Button
              variant="primary"
              onClick={onSyncJira}
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-sm active:scale-95 transition"
              title="Fetch and synchronize live tickets from Atlassian Jira Cloud (KAN)"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Sync Jira (KAN)
            </Button>
          )}
          <Button onClick={onRefresh} disabled={loading}>
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      }
    />
    <IssueTable
      issues={issues}
      onSelectIssue={onSelectIssue}
      filter={filter}
      onFilterChange={onFilterChange}
      search={search}
      onSearchChange={onSearchChange}
      loading={loading}
    />
  </div>
);
