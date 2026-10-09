import React, { useState, useEffect } from 'react';
import { JiraIssue, DashboardSummary, DashboardMetrics } from './types';
import { api } from './api/client';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { TicketDetailPage } from './pages/TicketDetailPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { SimulateModal } from './components/SimulateModal';
import { EmailViewerModal } from './components/EmailViewerModal';
import { PolicyModal } from './components/PolicyModal';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<'dashboard' | 'knowledge'>('dashboard');
  const [selectedIssueKey, setSelectedIssueKey] = useState<string | null>(null);
  const [issues, setIssues] = useState<JiraIssue[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [isSimulateOpen, setIsSimulateOpen] = useState(false);
  const [isEmailsOpen, setIsEmailsOpen] = useState(false);
  const [isPolicyOpen, setIsPolicyOpen] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [issuesData, summaryData, metricsData] = await Promise.all([
        api.getIssues(),
        api.getSummary(),
        api.getMetrics(),
      ]);
      setIssues(issuesData);
      setSummary(summaryData);
      setMetrics(metricsData);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError('Unable to reach JiraPilot backend service. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto refresh data every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleLoadDemoData = async () => {
    try {
      await api.loadDemoData();
      await fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSyncJira = async () => {
    setLoading(true);
    try {
      await api.syncJiraCloud('KAN');
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateSuccess = async (newIssue: JiraIssue) => {
    await fetchData();
    setSelectedIssueKey(newIssue.jiraKey);
  };

  const selectedIssue = issues.find((i) => i.jiraKey === selectedIssueKey);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <Navbar
        currentView={currentView}
        onNavigate={(view) => {
          setCurrentView(view);
          setSelectedIssueKey(null);
        }}
        onOpenSimulate={() => setIsSimulateOpen(true)}
        onOpenEmails={() => setIsEmailsOpen(true)}
        onOpenPolicy={() => setIsPolicyOpen(true)}
        onLoadDemoData={handleLoadDemoData}
        onSyncJira={handleSyncJira}
        loading={loading}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-950/50 border border-rose-500/50 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400" />
              <span>{error}</span>
            </div>
            <button
              onClick={fetchData}
              className="px-3 py-1 rounded bg-rose-900/50 hover:bg-rose-800 text-white font-semibold transition"
            >
              Retry
            </button>
          </div>
        )}

        {selectedIssue ? (
          <TicketDetailPage
            issue={selectedIssue}
            onBack={() => setSelectedIssueKey(null)}
            onRefresh={fetchData}
          />
        ) : currentView === 'knowledge' ? (
          <KnowledgePage />
        ) : (
          <DashboardPage
            issues={issues}
            summary={summary}
            metrics={metrics}
            onSelectIssue={(key) => setSelectedIssueKey(key)}
            onRefresh={fetchData}
            loading={loading}
          />
        )}
      </main>

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
    </div>
  );
};
export default App;
