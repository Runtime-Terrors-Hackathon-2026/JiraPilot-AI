import React, { useMemo } from 'react';
import {
  AlertTriangle,
  Bell,
  CheckCircle2,
  FileSearch,
  GitBranch,
  Inbox,
  PlayCircle,
  ShieldCheck,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { DashboardMetrics, DashboardSummary, IssueFilter, JiraIssue, MockEmail } from '../types';
import { MetricCard, Card, EmptyState, PageHeader, StatusBadge, Button } from '../components/ui/primitives';
import { PRIMARY_MESSAGE, SUPPORTING_MESSAGE } from '../lib/messaging';
import { formatDateTime, labelStatus } from '../lib/format';
import { attachmentTone, issueTone, latestAttachment, nextAction } from '../lib/status';
import { IssueTable } from '../components/IssueTable';

interface DashboardPageProps {
  issues: JiraIssue[];
  summary: DashboardSummary | null;
  metrics: DashboardMetrics | null;
  emails: MockEmail[];
  onSelectIssue: (key: string) => void;
  onNavigateIssues: (filter: IssueFilter) => void;
  onOpenSimulate: () => void;
  search: string;
  filter: IssueFilter;
  onFilterChange: (filter: IssueFilter) => void;
  loading: boolean;
  backendReachable: boolean;
  demoMode?: boolean | null;
  aiConfigured: boolean;
}

const CHART = ['#3b5ccc', '#0f766e', '#b45309', '#64748b', '#dc2626', '#6b8bff'];

export const DashboardPage: React.FC<DashboardPageProps> = ({
  issues,
  summary,
  metrics,
  emails,
  onSelectIssue,
  onNavigateIssues,
  onOpenSimulate,
  search,
  filter,
  onFilterChange,
  loading,
  backendReachable,
  demoMode,
  aiConfigured,
}) => {
  const waiting = summary?.waitingForInfoTickets ?? issues.filter((i) => i.status === 'WAITING_FOR_INFORMATION').length;
  const ready = summary?.readyTickets ?? issues.filter((i) => i.status === 'READY').length;
  const running = summary?.investigationsRunning ?? issues.filter((i) => i.investigationStatus === 'RUNNING').length;
  const completed = summary?.rcaCompleted ?? issues.filter((i) => i.investigationStatus === 'COMPLETED').length;
  const attentionEmails = emails.filter((e) => (e.status || '').toUpperCase() === 'FAILED').length;

  const statusData = metrics?.ticketsByStatus
    ? Object.entries(metrics.ticketsByStatus).map(([name, value]) => ({ name: name.replace(/_/g, ' '), value }))
    : [];
  const analysisData = useMemo(() => {
    const counts: Record<string, number> = {};
    issues.forEach((issue) => {
      const key = issue.investigationStatus || 'NOT_STARTED';
      counts[key] = (counts[key] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name: name.replace(/_/g, ' '), value }));
  }, [issues]);

  const apiErrors = issues.flatMap((issue) =>
    (issue.attachments || [])
      .filter((att) => att.primaryStatus && att.primaryStatus >= 400)
      .map((att) => ({ issue, att }))
  ).slice(0, 6);

  const repos = issues.flatMap((issue) =>
    (issue.attachments || [])
      .filter((att) => att.recommendedRepo)
      .map((att) => ({ issue, att }))
  ).slice(0, 5);

  const timeline = issues
    .flatMap((issue) => (issue.auditEvents || []).map((event) => ({ issue, event })))
    .sort((a, b) => new Date(b.event.timestamp).getTime() - new Date(a.event.timestamp).getTime())
    .slice(0, 8);

  const attention = [
    ...issues.filter((i) => i.status === 'WAITING_FOR_INFORMATION').map((i) => ({
      key: i.jiraKey,
      title: `${i.jiraKey} is missing essential information`,
      action: 'Open ticket',
    })),
    ...issues.flatMap((i) =>
      (i.attachments || [])
        .filter((a) => a.status === 'FAILED')
        .map((a) => ({ key: i.jiraKey, title: `Failed analysis: ${a.filename}`, action: 'Retry from issue' }))
    ),
    ...emails
      .filter((e) => (e.status || '').toUpperCase() === 'FAILED')
      .map((e) => ({ key: e.jiraKey, title: `Failed email for ${e.jiraKey}`, action: 'Review notifications' })),
  ].slice(0, 8);

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="Incident Operations"
        description="A clear view of ticket readiness, investigation progress and recommended next actions."
        actions={
          <Button variant="primary" onClick={onOpenSimulate}>
            <PlayCircle className="h-4 w-4" />
            Simulate issue
          </Button>
        }
      />

      <Card className="p-4">
        <p className="text-sm font-medium text-ink">{PRIMARY_MESSAGE}</p>
        <p className="mt-1 text-xs text-muted">{SUPPORTING_MESSAGE}</p>
      </Card>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard title="Total issues" value={summary?.totalTickets ?? issues.length} hint="Ingested from Jira, demo, or simulation" icon={Inbox} onClick={() => onNavigateIssues('ALL')} />
        <MetricCard title="Awaiting reporter information" value={waiting} hint="Asking for details is normal engineering practice" icon={AlertTriangle} tone="warning" onClick={() => onNavigateIssues('WAITING')} />
        <MetricCard title="Ready for investigation" value={ready} hint="Required diagnostic fields are present" icon={CheckCircle2} tone="success" onClick={() => onNavigateIssues('READY')} />
        <MetricCard title="Investigations in progress" value={running} hint="Analysis currently running" icon={FileSearch} tone="accent" onClick={() => onNavigateIssues('INVESTIGATING')} />
        <MetricCard title="Completed analyses" value={completed} hint="Evidence-backed findings ready for review" icon={ShieldCheck} tone="info" onClick={() => onNavigateIssues('INVESTIGATED')} />
        <MetricCard title="Notifications requiring attention" value={attentionEmails} hint="Failed email deliveries only" icon={Bell} tone={attentionEmails ? 'danger' : 'neutral'} />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="p-4 xl:col-span-2">
          <h3 className="mb-3 text-sm font-semibold text-ink">Ticket readiness distribution</h3>
          {statusData.length === 0 ? (
            <EmptyState title="No status metrics yet" description="Metrics appear after the backend has ingested issues." />
          ) : (
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={statusData} dataKey="value" innerRadius={48} outerRadius={72} paddingAngle={3}>
                    {statusData.map((_, index) => (
                      <Cell key={index} fill={CHART[index % CHART.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
        <Card className="p-4">
          <h3 className="mb-3 text-sm font-semibold text-ink">Analysis status</h3>
          {analysisData.length === 0 ? (
            <EmptyState title="No investigations yet" description="Start an investigation from an issue workspace." />
          ) : (
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analysisData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--jp-line)" />
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} stroke="var(--jp-muted)" />
                  <YAxis allowDecimals={false} tick={{ fontSize: 10 }} stroke="var(--jp-muted)" />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b5ccc" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="p-4">
          <h3 className="mb-3 text-sm font-semibold text-ink">Investigation activity</h3>
          {timeline.length === 0 ? (
            <EmptyState title="No audit events yet" description="Activity appears after validation or investigation runs." />
          ) : (
            <ol className="space-y-3">
              {timeline.map(({ issue, event }) => (
                <li key={`${issue.jiraKey}-${event.id}`}>
                  <button type="button" className="w-full text-left" onClick={() => onSelectIssue(issue.jiraKey)}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-xs font-semibold text-accent">{issue.jiraKey}</span>
                      <span className="text-[11px] text-muted">{formatDateTime(event.timestamp)}</span>
                    </div>
                    <p className="text-xs text-ink">{event.eventType}</p>
                    <p className="text-[11px] text-muted">{event.details}</p>
                  </button>
                </li>
              ))}
            </ol>
          )}
        </Card>
        <Card className="p-4">
          <h3 className="mb-3 text-sm font-semibold text-ink">Needs attention</h3>
          {attention.length === 0 ? (
            <EmptyState title="No blocking items" description="Issues currently have a clear next action or are waiting on analysis." />
          ) : (
            <ul className="space-y-2">
              {attention.map((item, idx) => (
                <li key={`${item.key}-${idx}`}>
                  <button type="button" className="flex w-full items-center justify-between rounded-md border border-line px-3 py-2 text-left hover:bg-surface-2" onClick={() => onSelectIssue(item.key)}>
                    <span className="text-xs text-ink">{item.title}</span>
                    <span className="text-[11px] text-accent">{item.action}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="p-4">
          <h3 className="mb-3 text-sm font-semibold text-ink">Recently identified API errors</h3>
          {apiErrors.length === 0 ? (
            <EmptyState title="No extracted API errors" description="Upload or ingest a log attachment to extract endpoints and HTTP status codes." />
          ) : (
            <ul className="space-y-2 text-xs">
              {apiErrors.map(({ issue, att }) => (
                <li key={att.id}>
                  <button type="button" className="w-full text-left" onClick={() => onSelectIssue(issue.jiraKey)}>
                    <div className="font-mono text-accent">{att.primaryEndpoint}</div>
                    <div className="text-muted">HTTP {att.primaryStatus} · {issue.jiraKey}</div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card className="p-4">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-ink">
            <GitBranch className="h-4 w-4 text-accent" />
            Repository recommendations
          </h3>
          {repos.length === 0 ? (
            <EmptyState title="No verified repository matches yet" description="Review the service catalog or analyze a log attachment to match an approved repository." />
          ) : (
            <ul className="space-y-2 text-xs">
              {repos.map(({ issue, att }) => (
                <li key={att.id} className="rounded-md border border-line px-3 py-2">
                  <div className="font-medium text-ink">{att.recommendedRepo}</div>
                  <div className="text-muted">{issue.jiraKey} · {att.primaryEndpoint || 'endpoint pending'}</div>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card className="p-4">
          <h3 className="mb-3 text-sm font-semibold text-ink">Integration health</h3>
          <ul className="space-y-2 text-xs">
            <li className="flex items-center justify-between">
              <span>Orchestrator backend</span>
              <StatusBadge tone={backendReachable ? 'success' : 'danger'}>{backendReachable ? 'Reachable' : 'Unreachable'}</StatusBadge>
            </li>
            <li className="flex items-center justify-between">
              <span>Jira mode</span>
              <StatusBadge tone="warning">{demoMode ? 'Demo' : backendReachable ? 'Live config' : 'Unknown'}</StatusBadge>
            </li>
            <li className="flex items-center justify-between">
              <span>AI provider</span>
              <StatusBadge tone={aiConfigured ? 'success' : 'warning'}>{aiConfigured ? 'Configured' : 'Fallback'}</StatusBadge>
            </li>
          </ul>
          <p className="mt-3 text-[11px] text-muted">Indicators reflect backend health and configuration, not assumed connectivity.</p>
        </Card>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold text-ink">Recent Jira issues</h3>
        <IssueTable
          issues={issues}
          onSelectIssue={onSelectIssue}
          filter={filter}
          onFilterChange={onFilterChange}
          search={search}
          loading={loading}
        />
      </div>
    </div>
  );
};
