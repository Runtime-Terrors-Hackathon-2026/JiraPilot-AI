import React, { useMemo, useState } from 'react';
import { ChevronRight, Search } from 'lucide-react';
import { IssueFilter, JiraIssue } from '../types';
import { attachmentTone, investigationTone, issueTone, latestAttachment, nextAction } from '../lib/status';
import { formatDateTime, labelStatus } from '../lib/format';
import { Button, EmptyState, ReadinessIndicator, StatusBadge } from './ui/primitives';

interface IssueTableProps {
  issues: JiraIssue[];
  onSelectIssue: (key: string) => void;
  filter: IssueFilter;
  onFilterChange: (filter: IssueFilter) => void;
  search: string;
  onSearchChange?: (value: string) => void;
  loading?: boolean;
}

function matchesFilter(issue: JiraIssue, filter: IssueFilter) {
  if (filter === 'READY') return issue.status === 'READY';
  if (filter === 'WAITING') return issue.status === 'WAITING_FOR_INFORMATION';
  if (filter === 'INVESTIGATING') return issue.status === 'INVESTIGATING' || issue.investigationStatus === 'RUNNING';
  if (filter === 'INVESTIGATED') return issue.status === 'INVESTIGATED' || issue.investigationStatus === 'COMPLETED';
  return true;
}

export const IssueTable: React.FC<IssueTableProps> = ({
  issues,
  onSelectIssue,
  filter,
  onFilterChange,
  search,
  onSearchChange,
  loading,
}) => {
  const [sortKey, setSortKey] = useState<'updated' | 'readiness' | 'key'>('updated');
  const [page, setPage] = useState(0);
  const pageSize = 12;

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return issues
      .filter((issue) => {
        const matchesSearch =
          !q ||
          issue.jiraKey.toLowerCase().includes(q) ||
          issue.summary.toLowerCase().includes(q) ||
          (issue.affectedService || '').toLowerCase().includes(q) ||
          (issue.reporter || '').toLowerCase().includes(q);
        return matchesSearch && matchesFilter(issue, filter);
      })
      .sort((a, b) => {
        if (sortKey === 'readiness') return (b.readinessScore || 0) - (a.readinessScore || 0);
        if (sortKey === 'key') return a.jiraKey.localeCompare(b.jiraKey);
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
      });
  }, [issues, search, filter, sortKey]);

  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const current = Math.min(page, pages - 1);
  const slice = filtered.slice(current * pageSize, current * pageSize + pageSize);

  const counts = {
    ALL: issues.length,
    WAITING: issues.filter((i) => i.status === 'WAITING_FOR_INFORMATION').length,
    READY: issues.filter((i) => i.status === 'READY').length,
    INVESTIGATING: issues.filter((i) => i.status === 'INVESTIGATING' || i.investigationStatus === 'RUNNING').length,
    INVESTIGATED: issues.filter((i) => i.status === 'INVESTIGATED' || i.investigationStatus === 'COMPLETED').length,
  };

  return (
    <div className="overflow-hidden rounded-xl border border-line bg-surface shadow-panel">
      <div className="flex flex-col gap-3 border-b border-line p-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          {onSearchChange && (
            <label className="relative">
              <span className="sr-only">Filter issues</span>
              <Search className="pointer-events-none absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted" />
              <input
                value={search}
                onChange={(e) => {
                  onSearchChange(e.target.value);
                  setPage(0);
                }}
                placeholder="Filter this table"
                className="h-8 w-56 rounded-md border border-line bg-canvas pl-8 pr-3 text-xs text-ink placeholder:text-muted focus:border-accent focus:outline-none"
              />
            </label>
          )}
          {(Object.keys(counts) as IssueFilter[]).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => {
                onFilterChange(key);
                setPage(0);
              }}
              className={`rounded-md px-2.5 py-1 text-xs font-medium ${
                filter === key ? 'bg-accent-soft text-accent' : 'text-muted hover:bg-surface-2'
              }`}
            >
              {key === 'WAITING' ? 'Awaiting info' : key.charAt(0) + key.slice(1).toLowerCase()} ({counts[key]})
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 text-xs text-muted">
          <span>{loading ? 'Refreshing…' : `${filtered.length} issues`}</span>
          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as typeof sortKey)}
            className="h-8 rounded-md border border-line bg-canvas px-2 text-xs text-ink"
            aria-label="Sort issues"
          >
            <option value="updated">Last updated</option>
            <option value="readiness">Readiness</option>
            <option value="key">Issue key</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[960px] text-left text-xs">
          <thead className="border-b border-line bg-surface-2 text-[11px] uppercase tracking-wide text-muted">
            <tr>
              <th className="px-3 py-2.5 font-medium">Issue key</th>
              <th className="px-3 py-2.5 font-medium">Summary</th>
              <th className="px-3 py-2.5 font-medium">Reporter</th>
              <th className="px-3 py-2.5 font-medium">Readiness</th>
              <th className="px-3 py-2.5 font-medium">Attachments</th>
              <th className="px-3 py-2.5 font-medium">Investigation</th>
              <th className="px-3 py-2.5 font-medium">Service</th>
              <th className="px-3 py-2.5 font-medium">Updated</th>
              <th className="px-3 py-2.5 font-medium">Next action</th>
            </tr>
          </thead>
          <tbody>
            {slice.length === 0 ? (
              <tr>
                <td colSpan={9}>
                  <EmptyState
                    title={issues.length === 0 ? 'No issues ingested yet' : 'No issues match these filters.'}
                    description={
                      issues.length === 0
                        ? 'Load demo data, simulate an issue, or sync from Jira to begin triage.'
                        : 'Try a different search term or status filter.'
                    }
                  />
                </td>
              </tr>
            ) : (
              slice.map((issue) => {
                const attachment = latestAttachment(issue);
                return (
                  <tr
                    key={issue.id || issue.jiraKey}
                    className="cursor-pointer border-b border-line/80 hover:bg-surface-2"
                    onClick={() => onSelectIssue(issue.jiraKey)}
                  >
                    <td className="px-3 py-3 font-mono font-semibold text-accent">{issue.jiraKey}</td>
                    <td className="max-w-[280px] truncate px-3 py-3 font-medium text-ink">{issue.summary}</td>
                    <td className="max-w-[140px] truncate px-3 py-3 text-muted">{issue.reporter || '—'}</td>
                    <td className="px-3 py-3">
                      <ReadinessIndicator score={issue.readinessScore} />
                    </td>
                    <td className="px-3 py-3">
                      {attachment ? (
                        <StatusBadge tone={attachmentTone(attachment.status)}>{labelStatus(attachment.status)}</StatusBadge>
                      ) : (
                        <span className="text-muted">None</span>
                      )}
                    </td>
                    <td className="px-3 py-3">
                      <div className="flex flex-col gap-1">
                        <StatusBadge tone={issueTone(issue.status)}>{labelStatus(issue.status)}</StatusBadge>
                        <StatusBadge tone={investigationTone(issue.investigationStatus)}>
                          {labelStatus(issue.investigationStatus)}
                        </StatusBadge>
                      </div>
                    </td>
                    <td className="px-3 py-3 font-mono text-ink">{issue.affectedService || attachment?.primaryService || '—'}</td>
                    <td className="px-3 py-3 text-muted">{formatDateTime(issue.updatedAt)}</td>
                    <td className="px-3 py-3">
                      <span className="inline-flex items-center gap-1 text-muted">
                        {nextAction(issue)}
                        <ChevronRight className="h-3.5 w-3.5" />
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between border-t border-line px-3 py-2 text-xs text-muted">
        <span>
          Page {current + 1} of {pages}
        </span>
        <div className="flex gap-2">
          <Button size="sm" disabled={current === 0} onClick={() => setPage((p) => Math.max(0, p - 1))}>
            Previous
          </Button>
          <Button size="sm" disabled={current >= pages - 1} onClick={() => setPage((p) => p + 1)}>
            Next
          </Button>
        </div>
      </div>
    </div>
  );
};
