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
  loading,
}) => (
  <div>
    <PageHeader
      title="Jira Issues"
      description="Search, filter and open tickets without leaving the investigation workflow."
      actions={
        <Button onClick={onRefresh} disabled={loading}>
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
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
