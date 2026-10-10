import React, { useState, useEffect, useCallback } from 'react';
import {
  JiraIssue,
  DashboardSummary,
  DashboardMetrics,
  MockEmail,
  BackendHealth,
  NvidiaStatus,
  AppView,
  IssueFilter,
} from './types';
import { api } from './api/client';
import { AppShell } from './layout/AppShell';
import { DashboardPage } from './pages/DashboardPage';
import { IssuesPage } from './pages/IssuesPage';
import { LogsPage } from './pages/LogsPage';
import { ReposPage } from './pages/ReposPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { NotificationsPage } from './pages/NotificationsPage';
import { SettingsPage } from './pages/SettingsPage';
import { TicketDetailPage } from './pages/TicketDetailPage';
import { ApiFlowPage } from './pages/ApiFlowPage';
import { SimulateModal } from './components/SimulateModal';
import { EmailViewerModal } from './components/EmailViewerModal';
import { PolicyModal } from './components/PolicyModal';
import { useToast } from './components/ui/Toast';
import { ErrorState } from './components/ui/primitives';
import { Server, Link2 } from 'lucide-react';

export const App: React.FC = () => {
  const { push } = useToast();
  const [currentView, setCurrentView] = useState<AppView>('overview');
  const [selectedIssueKey, setSelectedIssueKey] = useState<string | null>(null);
  const [issues, setIssues] = useState<JiraIssue[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [emails, setEmails] = useState<MockEmail[]>([]);
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [aiStatus, setAiStatus] = useState<NvidiaStatus | null>(null);
  const [backendReachable, setBackendReachable] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [customBackendUrl, setCustomBackendUrl] = useState('');

  // Filters & Search
  const [search, setSearch] = useState('');
  const [issueFilter, setIssueFilter] = useState<IssueFilter>('ALL');

  // Modals
  const [isSimulateOpen, setIsSimulateOpen] = useState(false);
  const [isEmailsOpen, setIsEmailsOpen] = useState(false);
  const [isPolicyOpen, setIsPolicyOpen] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [issuesData, summaryData, metricsData, emailsData, healthData, aiData] =
        await Promise.all([
          api.getIssues().catch(() => []),
          api.getSummary().catch(() => null),
          api.getMetrics().catch(() => null),
          api.getAllEmails().catch(() => []),
          api.getHealth().catch(() => null),
          api.getNvidiaStatus().catch(() => null),
        ]);

      setIssues(issuesData);
      setSummary(summaryData);
      setMetrics(metricsData);
      setEmails(emailsData);
      setHealth(healthData);
      setAiStatus(aiData);
      setBackendReachable(healthData !== null || issuesData.length > 0);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setBackendReachable(false);
      setError('Unable to reach JiraPilot backend service. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Auto refresh data every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleSyncJira = async () => {
    setLoading(true);
    try {
      push({ kind: 'info', title: 'Syncing live tickets from Jira Cloud project KAN...' });
      const synced = await api.syncJiraCloud('KAN');
      push({
        kind: 'success',
        title: `Jira sync completed: ${synced.length} tickets synchronized`,
      });
      await fetchData();
    } catch (err: any) {
      console.error(err);
      push({ kind: 'error', title: 'Jira Sync Failed', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleLoadDemoData = async () => {
    setLoading(true);
    try {
      const res = await api.loadDemoData();
      push({
        kind: 'success',
        title: `Demo Data Loaded: ${res.loadedCount} synthetic tickets ready`,
      });
      await fetchData();
    } catch (err: any) {
      console.error(err);
      push({ kind: 'error', title: 'Failed to load demo data', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateSuccess = async (newIssue: JiraIssue) => {
    push({ kind: 'success', title: `Issue ${newIssue.jiraKey} simulated successfully` });
    await fetchData();
    setSelectedIssueKey(newIssue.jiraKey);
  };

  const [apiFlowIssueKey, setApiFlowIssueKey] = useState<string | null>(null);

  const handleOpenApiFlow = (key?: string) => {
    if (key) {
      setApiFlowIssueKey(key);
    } else if (selectedIssueKey) {
      setApiFlowIssueKey(selectedIssueKey);
    } else if (issues.length > 0) {
      const target = issues.find((i) => i.status === 'INVESTIGATED' || i.investigation) || issues[0];
      setApiFlowIssueKey(target.jiraKey);
    }
    setSelectedIssueKey(null);
    setCurrentView('api-flow');
  };

  const selectedIssue = issues.find((i) => i.jiraKey === selectedIssueKey);

  const unreadOrFailedEmails = emails.filter(
    (e) => (e.status || '').toUpperCase() === 'FAILED'
  ).length;

  return (
    <AppShell
      currentView={currentView}
      onNavigate={(view) => {
        setCurrentView(view);
        setSelectedIssueKey(null);
      }}
      issueKey={selectedIssueKey}
      search={search}
      onSearch={setSearch}
      onOpenNotifications={() => {
        setCurrentView('notifications');
        setSelectedIssueKey(null);
      }}
      health={health}
      aiStatus={aiStatus}
      backendReachable={backendReachable}
      notificationCount={unreadOrFailedEmails}
      onSyncJira={handleSyncJira}
      onLoadDemoData={handleLoadDemoData}
      onOpenSimulate={() => setIsSimulateOpen(true)}
      loading={loading}
    >
      {(!backendReachable || error) && (
        <div className="mb-6 rounded-2xl border border-indigo-500/30 bg-[#0c1427]/95 p-4 shadow-2xl backdrop-blur-md">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Server className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-white">Backend Connection Setup</h4>
                  <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300 border border-amber-500/30">
                    {backendReachable ? 'Reconnecting' : 'Offline / Awaiting URL'}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-indigo-300/80">
                  Current Target: <code className="rounded bg-black/50 px-1.5 py-0.5 font-mono text-cyan-300">{api.getApiBase()}</code>
                </p>
                <p className="text-[11px] text-indigo-400/70">
                  If deployed on Vercel, paste your live Render backend URL (e.g. <code className="text-white">https://jirapilot-backend.onrender.com</code>) to connect immediately.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="https://your-backend.onrender.com"
                value={customBackendUrl}
                onChange={(e) => setCustomBackendUrl(e.target.value)}
                className="w-full sm:w-64 rounded-xl border border-indigo-500/30 bg-[#050814] px-3 py-2 text-xs text-white placeholder-indigo-400/40 focus:border-cyan-400 focus:outline-none font-mono"
              />
              <button
                type="button"
                onClick={() => {
                  if (customBackendUrl.trim()) {
                    api.setApiBaseOverride(customBackendUrl.trim());
                  }
                }}
                className="shrink-0 flex items-center gap-1.5 rounded-xl bg-cyan-600 px-3.5 py-2 text-xs font-bold text-white hover:bg-cyan-500 transition-colors shadow-lg hover:shadow-cyan-500/20"
              >
                <Link2 className="h-3.5 w-3.5" />
                <span>Connect</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {currentView === 'api-flow' ? (
        <ApiFlowPage
          issues={issues}
          currentIssueKey={apiFlowIssueKey || selectedIssueKey}
          onBack={() => {
            if (apiFlowIssueKey) {
              setSelectedIssueKey(apiFlowIssueKey);
              setCurrentView('overview');
            } else {
              setCurrentView('overview');
            }
          }}
          onSelectIssue={(key) => setApiFlowIssueKey(key)}
          onInspectCode={(key) => {
            setSelectedIssueKey(key);
            setCurrentView('overview');
          }}
        />
      ) : selectedIssue ? (
        <TicketDetailPage
          issue={selectedIssue}
          onBack={() => setSelectedIssueKey(null)}
          onRefresh={fetchData}
          onExploreApiFlow={handleOpenApiFlow}
        />
      ) : currentView === 'overview' ? (
        <DashboardPage
          issues={issues}
          summary={summary}
          metrics={metrics}
          emails={emails}
          onSelectIssue={(key) => setSelectedIssueKey(key)}
          onNavigateIssues={(f) => {
            setIssueFilter(f);
            setCurrentView('issues');
          }}
          onOpenSimulate={() => setIsSimulateOpen(true)}
          onSyncJira={handleSyncJira}
          onLoadDemoData={handleLoadDemoData}
          search={search}
          filter={issueFilter}
          onFilterChange={setIssueFilter}
          loading={loading}
          backendReachable={backendReachable}
          demoMode={health?.demoMode}
          aiConfigured={Boolean(aiStatus?.configured)}
        />
      ) : currentView === 'issues' ? (
        <IssuesPage
          issues={issues}
          onSelectIssue={(key) => setSelectedIssueKey(key)}
          search={search}
          onSearchChange={setSearch}
          filter={issueFilter}
          onFilterChange={setIssueFilter}
          onRefresh={fetchData}
          onSyncJira={handleSyncJira}
          loading={loading}
        />
      ) : currentView === 'logs' ? (
        <LogsPage issues={issues} onSelectIssue={(key) => setSelectedIssueKey(key)} />
      ) : currentView === 'repos' ? (
        <ReposPage issues={issues} onSelectIssue={(key) => setSelectedIssueKey(key)} />
      ) : currentView === 'knowledge' ? (
        <KnowledgePage />
      ) : currentView === 'notifications' ? (
        <NotificationsPage emails={emails} onSelectIssue={(key) => setSelectedIssueKey(key)} />
      ) : currentView === 'settings' ? (
        <SettingsPage
          health={health}
          aiStatus={aiStatus}
          backendReachable={backendReachable}
        />
      ) : (
        <DashboardPage
          issues={issues}
          summary={summary}
          metrics={metrics}
          emails={emails}
          onSelectIssue={(key) => setSelectedIssueKey(key)}
          onNavigateIssues={(f) => {
            setIssueFilter(f);
            setCurrentView('issues');
          }}
          onOpenSimulate={() => setIsSimulateOpen(true)}
          onSyncJira={handleSyncJira}
          onLoadDemoData={handleLoadDemoData}
          search={search}
          filter={issueFilter}
          onFilterChange={setIssueFilter}
          loading={loading}
          backendReachable={backendReachable}
          demoMode={health?.demoMode}
          aiConfigured={Boolean(aiStatus?.configured)}
        />
      )}

      {/* Modals */}
      <SimulateModal
        isOpen={isSimulateOpen}
        onClose={() => setIsSimulateOpen(false)}
        onSuccess={handleSimulateSuccess}
      />

      <EmailViewerModal
        isOpen={isEmailsOpen}
        onClose={() => setIsEmailsOpen(false)}
        selectedKey={selectedIssueKey || undefined}
      />

      <PolicyModal
        isOpen={isPolicyOpen}
        onClose={() => setIsPolicyOpen(false)}
      />
    </AppShell>
  );
};

export default App;
